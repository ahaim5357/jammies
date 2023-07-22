"""A script containing helper methods used throughout the package.
"""

import os
import re
import inspect
from typing import Any, Dict, Callable, TypeVar, Tuple
from io import IOBase, BytesIO
from mimetypes import guess_extension
from zipfile import ZipFile
from urllib.parse import urlparse
import requests

def get_default(func: Callable[..., Any], param: str) -> Any | None:
    """Gets the default value of a function parameter, or `None` if not applicable.
    
    Parameters
    ----------
    func : Callable[..., Any]
        The function to check.
    param : str
        The name of the parameter.

    Returns
    -------
    Any | None
        The default value of the parameter, or `None` if not applicable.
    """
    param_sig: inspect.Parameter = inspect.signature(func).parameters[param]
    return None if param_sig.default is inspect.Parameter.empty else param_sig.default

def get_or_default(dict_obj: Dict[str, Any], key: str, func: Callable[..., Any],
        param: str | None = None) -> Any | None:
    """Gets the value within a dictionary, or the default from the function if none is specified.

    Parameters
    ----------
    dict_obj : Dict[str, Any]
        The dictionary containing the data of an object.
    key : str
        The key to obtain the value of the dictionary from.
    func : Callable[..., Any]
        The function to check the default of if the key does not exist in the dictionary.
    param : str | None (default None)
        The name of the parameter containing the default value. When `None`, defaults to the `key`.
    
    Returns
    -------
    Any | None
        The value of the key, the default value, or `None`.
    """
    if param is None:
        param: str = key

    return dict_obj[key] if key in dict_obj else get_default(func, param)

I = TypeVar('I')
"""The type of the input."""

def input_with_default(func: Callable[..., Any], param: str, text: str) -> I:
    """Read a string from standard input and defaults if no value is specified.
    
    Parameters
    ----------
    func : Callable[..., Any]
        The function to check.
    param : str
        The name of the parameter.
    text : str
        The text to display for input.

    Returns
    -------
    Any
        The input, or the default when not specified.
    """
    def_val: I = get_default(func, param)
    val: I = input(f"{text} (default '{def_val}'): ")
    return val if val else def_val

def input_yn_default(text: str, yes_or_no: bool) -> bool:
    """Accepts an input of a yes / no answer which defaults to the
    specified value.

    Parameters
    ----------
    text: str
        The text to display for input.
    yes_or_no: bool
        When `True`, the input will default to 'yes'.
    
    Returns
    -------
    bool
        `True` if the input said 'yes'.
    """
    def cap_when_true(text: str, cap: bool) -> str:
        return text.capitalize() if cap else text

    input_string: str = f"{text} ({cap_when_true('y', yes_or_no)}" \
        + f"/{cap_when_true('n', not yes_or_no)})? "

    while True:
        if yn_input := input(input_string):
            if (yes_no := yn_input.lower()[0]) in ['y', 'n']:
                return yes_no != 'n'
            print('Answer provided was not y/n, please input y/n.')
            continue
        return yes_or_no

def unzip(file: str | IOBase, out_dir: str = os.curdir) -> None:
    """Unzips the file or stream to the specified directory.

    Parameters
    ----------
    file : str | io.IOBase
        The file or stream of the zip file.
    out_dir : str (default '.')
        The directory to extract the zip file to.
    """
    with ZipFile(file, 'r') as zip_ref: # type: ZipFile
        zip_ref.extractall(out_dir)

_FILENAME_PARAM_REGEX: str = \
    r'filename=(?:([A-Za-z0-9\!\#\$\%\&\'\*\+\-\.\^\_\`\|\~]+)|(?:\"([^\"]*)\"))'
"""Regex for getting the filename from the content-disposition header using the
[RFC6266](https://datatracker.ietf.org/doc/html/rfc6266#section-4.1) spec.
"""

_FILENAME_STAR_PARAM_REGEX: str = \
    r'filename\*=(?:[A-Za-z0-9\!\#\$\%\&\+\-\^\_\`\{\}\~]+)\'[A-Za-z0-9\%\-]*\'' \
        + r'((?:%[0-9A-Fa-f]{2}|[A-Za-z0-9\!\#\$\%\&\+\-\.\^\_\`\|\~])*)'
"""Regex for getting the filename* from the content-disposition header using the
[RFC8187](https://datatracker.ietf.org/doc/html/rfc8187) spec.
"""

_CONTENT_DISPOSITION: str = 'content-disposition'
"""The header for the content disposition."""

_CONTENT_TYPE: str = 'content-type'
"""The header for the content type."""

def download_file(url: str, handler: Callable[[requests.Response, str], bool],
        stream: bool = True) -> bool:
    """Downloads a file from the specified url via a GET request and handles the response
    bytes as specified.
    
    Parameters
    ----------
    url : str
        The url to download the file from.
    handler : (requests.Response, str) -> bool
        A function which takes in the response and filename and returns whether the file was
        successfully handled.
    stream : bool (default True)
        If `False`, the response content will be immediately downloaded.

    Returns
    -------
    bool
        `True` if the file was successfully downloaded, `False` otherwise
    """

    # Download data within 5 minutes
    with requests.get(url, stream = stream, allow_redirects = True,
            timeout = 300) as response: # type: requests.Response
        # If cannot grab file, return False
        if not response.ok:
            return False

        # Get filename
        filename: str | None = None

        ## Lookup filename from content disposition if present
        if _CONTENT_DISPOSITION in response.headers:
            if 'filename*' in (disposition := response.headers[_CONTENT_DISPOSITION]):
                filename: str = re.findall(_FILENAME_STAR_PARAM_REGEX, disposition)[0]
            elif 'filename' in disposition:
                matches: Tuple[str, str] = re.findall(_FILENAME_PARAM_REGEX, disposition)[0]
                filename: str = matches[0] if matches[0] else matches[1]

        # Set to basename of path if not present
        if not filename:
            filename = os.path.basename(urlparse(url).path)

        # Check to see if extension is present
        name, ext = os.path.splitext(filename)

        # If no extension is present and we have access to the content type
        if not ext and _CONTENT_TYPE in response.headers:
            filename = name + guess_extension(response.headers[_CONTENT_TYPE]
                .partition(';')[0].strip())

        # Handle the result of the downloaded file
        return handler(response, filename)

def download_and_write(url: str, unzip_file: bool = True, out_dir: str = os.curdir,
        stream: bool = True) -> bool:
    """Downloads a file from the specified url via a GET request and writes or unzips
    the file, if applicable.

    Parameters
    ----------
    url : str
        The url to download the file from.
    unzip_file : bool (default True)
        If `True`, will attempt to unzip the file if the file extension is correct.
    out_dir : str (default '.')
        The directory to write or unzip the file to.
    stream : bool (default True)
        If `False`, the response content will be immediately downloaded.

    Returns
    -------
    bool
        `True` if the file was successfully downloaded, `False` otherwise
    """

    def __write(__response: requests.Response, __filename: str, __dir: str) -> bool:
        """Writes the file or unzips it to the specified directory.

        Parameters
        ----------
        __response : requests.Response
            The response of the url request.
        __filename : str
            The name of the file requested from the url.
        __dir : str
            The directory to write the file(s) to.
        
        Returns
        -------
        bool
            `True` if the download was successful, `False` otherwise.
        """

        # Unzip file if available and set
        if unzip_file and __filename.endswith('.zip'):
            with BytesIO(__response.content) as zip_bytes: # type: BytesIO
                unzip(zip_bytes, out_dir = __dir)
        # Otherwise do normal extraction
        else:
            # Create directory name if not already present
            name: str = os.sep.join([__dir, __filename])
            os.makedirs(os.path.dirname(name), exist_ok = True)

            with open(name, 'wb') as file:
                for data in __response.iter_content(1024): # type: ReadableBuffer
                    file.write(data)
        return True

    return download_file(url,
        lambda response, filename: __write(response, filename, out_dir), stream = stream)

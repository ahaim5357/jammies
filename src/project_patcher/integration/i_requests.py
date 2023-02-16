import os
import requests
import re
from typing import Callable, Optional
from io import BytesIO
from uuid import uuid4
from mimetypes import guess_extension
from project_patcher.utils import unzip

_FILENAME_REGEX: str = r'filename\*?=(?:\"([^\'\"\n;]+)\"|(?:(?:UTF-8|ISO-8859-1|[^\'\"])\'[^\'\"]?\')([^\'\"\n;]+));?'
"""Regex for getting the filename from the content-disposition header.
Tries to read normal filename and a fuzzy regex of the [RFC8187](https://datatracker.ietf.org/doc/html/rfc8187) spec.
"""

_CONTENT_DISPOSITION: str = 'content-disposition'
"""The header for the content disposition."""

_CONTENT_TYPE: str = 'content-type'
"""The header for the content type."""

def download_file(url: str, handler: Callable[[requests.Response, str], bool], stream: bool = True) -> bool:
    """Downloads a file from the specified url via a GET request and handles the response bytes as specified.
    
    Parameters
    ----------
    url : str
        The url to download the file from.
    handler : (requests.Response, str) -> bool
        A function which takes in the response and filename and returns whether the file was successfully handled.
    stream : bool (default True)
        If `False`, the response content will be immediately downloaded.

    Returns
    -------
    bool
        `True` if the file was successfully downloaded, `False` otherwise
    """

    # Download data
    with requests.get(url, stream = stream, allow_redirects = True) as response: # type: requests.Response
        # If cannot grab file, return False
        if not response.ok:
            return False
        
        # Get filename
        filename: Optional[str] = None

        ## Lookup filename from content disposition if present
        if _CONTENT_DISPOSITION in response.headers:
            for filename_lookup in re.findall(_FILENAME_REGEX, response.headers[_CONTENT_DISPOSITION]): # type: Tuple[str, str]
                # If filename* is present, set and then break
                if (name := filename_lookup[1]):
                    filename = name
                    break
                # Otherwise, set the normal filename and keep checking
                else:
                    filename = filename_lookup[0]
            
        ## If no filename was present, assign a default name
        if filename is None:
            filename: str = str(uuid4())
            # Set file extension from content type, if available
            if _CONTENT_TYPE in response.headers:
                if (ext := guess_extension(response.headers[_CONTENT_TYPE].partition(';')[0].strip())) is not None: # type: Optional[str]
                    filename += ext
        
        # Handle the result of the downloaded file
        return handler(response, filename)

def download_and_write(url: str, unzip_file: bool = True, dir: str = os.curdir, stream: bool = True) -> bool:
    """Downloads a file from the specified url via a GET request and writes or unzips the file, if applicable.

    Parameters
    ----------
    url : str
        The url to download the file from.
    unzip_file : bool (default True)
        If `True`, will attempt to unzip the file if the file extension is correct.
    dir : str (default '.')
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
                unzip(zip_bytes, dir = __dir)
        # Otherwise do normal extraction
        else:
            # Create directory name if not already present
            name: str = os.sep.join([__dir, __filename])
            os.makedirs(os.path.dirname(name), exist_ok = True)

            with open(name, 'wb') as file:
                for bytes in __response.iter_content(1024): # type: ReadableBuffer
                    file.write(bytes)
        return True
    
    return download_file(url, lambda response, filename: __write(response, filename, dir), stream = stream)

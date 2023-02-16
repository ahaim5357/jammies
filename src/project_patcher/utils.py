"""TODO: Document"""

import sys
import os
from importlib.util import find_spec
import inspect
from typing import Optional, Any, Dict, Callable, Union
from io import IOBase
from zipfile import ZipFile

def get_default(func: Callable[..., Any], param: str) -> Optional[Any]:
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
        param: Optional[str] = None) -> Optional[Any]:
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

def has_module(name: str) -> bool:
    """Checks whether the module is currently loaded or can be added to the current workspace.

    Parameters
    ----------
    name : str
        The name of the module.

    Returns
    -------
    bool
        `True` if the module exists, `False` otherwise.
    """
    return (name in sys.modules) or (find_spec(name) is not None)

def unzip(file: Union[str, IOBase], out_dir: str = os.curdir) -> None:
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

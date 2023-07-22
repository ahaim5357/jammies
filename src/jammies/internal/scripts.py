"""A script containing methods that can be used as part of post processing on a project file.
Methods can be referenced via 'internal:<method_name>
"""

# TODO: Deprecated for removal

import os
from shutil import unpack_archive, _find_unpack_format

def unpack(_: str, filename: str) -> bool:
    """Unpacks an archive when present and removes
    the original archive.

    Parameters
    ----------
    root_dir : str
        The project directory.
    filename : str
        The relative path of the file.
    
    Returns
    -------
    bool
        `True` when the operation is successful.
    """

    # Check if file is an archive
    if _find_unpack_format(filename):
        # Unpack and delete archive
        unpack_archive(filename, extract_dir = os.path.dirname(filename))
        os.remove(filename)

    return True

def notebook_to_script(_: str, filename: str) -> bool:
    """Converts a notebook to a script using `nbconvert`.

    Parameters
    ----------
    root_dir : str
        The project directory.
    filename : str
        The relative path of the file.
    
    Returns
    -------
    bool
        `True` when the operation is successful.
    """

    if filename.endswith('.ipynb'):
        # Run nbconvert
        os.system(f'jupyter nbconvert --to script {filename}')
    return True

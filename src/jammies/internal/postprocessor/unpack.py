"""A script containing the post processor which unpacks archives
in the directory they currently exist within.
"""

import os
from glob import glob
from shutil import unpack_archive, _find_unpack_format
from jammies.log import Logger
from jammies.registrar import JammiesRegistrar

_REGISTRY_NAME: str = 'unpack_archive'
"""The registry name of the post processor."""

def setup(registrar: JammiesRegistrar) -> None:
    """A setup method used to register components to the project.
    
    Parameters
    ----------
    registrar : `JammiesRegistrar`
        The registrar used to register the components for the project.
    """
    registrar.register_post_processor(_REGISTRY_NAME, unpack)

def unpack(logger: Logger, current_dir: str, **kwargs) -> bool:
    """Unpacks an archive when present and removes
    the original archive.
    
    Parameters
    ----------
    logger : Logger
        A logger for reporting on information.
    current_dir : str
        The current directory to execute the processor within.
    recursive : bool (default `False`)
        When `True`, recurses through subdirectories in the current
        directory.
    
    Returns
    -------
    bool
        `True` if the operation is successful.
    """
    archives: list[str] = []

    logger.debug(f'Unpacking archives in {current_dir}')

    for filename in glob(os.sep.join([current_dir, '**']),
            recursive = kwargs['recursive'] if 'recursive' in kwargs else False):
        # Check if file is an archive
        if os.path.isfile(filename) and _find_unpack_format(filename):
            archives += filename

    for filename in archives:
        logger.debug(f'Found: {filename}')
        # Unpack and delete archive
        unpack_archive(filename, extract_dir = os.path.dirname(filename))
        os.remove(filename)

    # Return true if an unpacking was performed
    return len(archives) > 0

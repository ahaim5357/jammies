"""A script containing the post processor which handles file
operations (e.g., move, delete).
"""

import os
import fnmatch
from typing import Callable, Any
from pathlib import Path
from jammies.log import Logger
from jammies.registrar import JammiesRegistrar

_REGISTRY_NAME: str = 'file_operations'
"""The registry name of the post processor."""

def setup(registrar: JammiesRegistrar) -> None:
    """A setup method used to register components to the project.
    
    Parameters
    ----------
    registrar : `JammiesRegistrar`
        The registrar used to register the components for the project.
    """
    registrar.register_post_processor(_REGISTRY_NAME, fops)

def fops(logger: Logger, current_dir: str, **kwargs) -> bool:
    """Performs file operations on the provided files matching the patterns.
    
    Parameters
    ----------
    logger : Logger
        A logger for reporting on information.
    current_dir : str
        The current directory to execute the processor within.
    move : str -> str
        A dictionary of file patterns to the directory the file(s) will
        be moved to.
    delete : list of strs
        A list of file patterns to remove from the workspace.
    error_on_missing : bool
        When `True`, an error will be thrown if a file is missing.
    
    Returns
    -------
    bool
        `True` if the operation is successful.
    """

    performed_operation: bool = False
    failed: bool = False

    def __handle_fail(message: str):
        """Handles the logic when `failed_on_error` is `True`.

        Parameters
        ----------
        message : str
            The message to log.
        """
        nonlocal failed

        logger.error(message)
        failed = True

    # Handle missing file
    handle_missing: Callable[[str], Any] = __handle_fail if \
        (kwargs['error_on_missing'] if 'error_on_missing' in kwargs else False) \
        else logger.skip

    # Get all files
    files: list[str] = [Path(os.path.relpath(path, current_dir)).as_posix() \
        for path in Path(current_dir).rglob('*') if path.is_file()]

    # Move files
    if 'move' in kwargs:
        for pattern, new_dir in kwargs['move'].items():
            for file in fnmatch.filter(files, pattern):
                # Each file matches the relative directory
                # Move to the new directory by getting the base of the file path
                # And concatenate with the current directory
                src: str = os.path.join(current_dir, file)
                dst: str = os.path.join(current_dir, new_dir, os.path.basename(file))

                if os.path.exists(src):
                    logger.debug(f'Moving: {src} -> {dst}')
                    os.renames(src, dst)
                    performed_operation = True
                else:
                    handle_missing(f'File \'{src}\' no longer exists for moving.')

    # Delete files
    if 'delete' in kwargs:
        for pattern in kwargs['delete']:
            for file in fnmatch.filter(files, pattern):
                src: str = os.path.join(current_dir, file)

                if os.path.exists(src):
                    logger.debug(f'Removing: {src}')
                    os.remove(src)
                    performed_operation = True
                else:
                    handle_missing(f'File \'{src}\' no longer exists for removing.')

    return (not failed) and performed_operation

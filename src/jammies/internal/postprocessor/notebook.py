"""A script containing the post processor which converts a notebook
to a python file.
"""

import os
from glob import iglob
import subprocess as sp
from jammies.module import has_module
from jammies.log import Logger
from jammies.registrar import JammiesRegistrar

_REGISTRY_NAME: str = 'convert_notebook'
"""The registry name of the post processor."""

def setup(registrar: JammiesRegistrar) -> None:
    """A setup method used to register components to the project.
    
    Parameters
    ----------
    registrar : `JammiesRegistrar`
        The registrar used to register the components for the project.
    """

    # Check to see if nbconvert exists
    if has_module('nbconvert'):
        registrar.register_post_processor(_REGISTRY_NAME, notebook_to_script)
    else:
        registrar.add_post_processor_missing_message(_REGISTRY_NAME,
            'The nbconvert Python library is not installed. You can install'
            + ' the library by running of the following commands:'
            + os.linesep
            + '-> pip install nbconvert'
        )

def notebook_to_script(logger: Logger, current_dir: str) -> bool:
    """Converts a Python notebook to a script via `nbconvert`.
    
    Parameters
    ----------
    logger : Logger
        A logger for reporting on information.
    current_dir : str
        The current directory to execute the processor within.
    
    Returns
    -------
    bool
        `True` if the operation is successful.
    """
    result: bool = False
    failed: list[str] = []

    logger.debug(f'Converting notebooks in {current_dir}')

    for filename in iglob(os.sep.join([current_dir, '**']), recursive = True):
        if filename.endswith('.ipynb'):
            logger.debug(f'Converting: {filename}')
            if sp.run(
                ['jupyter', 'nbconvert', '--to', 'script', filename],
                check = False,
                stdout = sp.DEVNULL
            ).returncode == 0:
                result = True
        else:
            failed += filename

    if failed:
        return logger.error(
            'Failed to convert the following scripts: '
            + os.linesep.join(list(map(lambda s: f'-> {s}', failed)))
        )

    return result

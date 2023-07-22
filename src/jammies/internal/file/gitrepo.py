"""A script obtaining a project file from a git repository.
"""

import os
import subprocess as sp
from jammies.module import load_module, has_module
from jammies.registrar import JammiesRegistrar

_REGISTRY_NAME: str = 'git'
"""The registry name of the project file handler."""

def setup(registrar: JammiesRegistrar) -> None:
    """A setup method used to register components to the project.
    
    Parameters
    ----------
    registrar : `JammiesRegistrar`
        The registrar used to register the components for the project.
    """

    # Check if git is present on the machine
    if sp.run(['git', '--help'], check = False, stdout = sp.DEVNULL).returncode == 0 \
            and has_module('git'):
        load_module('jammies.internal.file.delegate.gitrepo').setup_delegate(registrar)
    else:
        registrar.add_file_handler_missing_message(_REGISTRY_NAME,
            'git, and/or the corresponding Python library, is not installed'
            + ' on the local machine. You can install git using the installer'
            + ' at https://git-scm.com/downloads.'
            + os.linesep + os.linesep
            + 'You can install the corresponding library by running one of the'
            + ' following commands:'
            + os.linesep
            + '-> pip install GitPython>=3.1' + os.linesep
            + '-> pip install jammies[git]'
        )

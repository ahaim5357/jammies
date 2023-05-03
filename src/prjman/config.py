"""A script containing the configuration information.
"""

import sys
import os
from typing import Callable, Any
from platformdirs import site_config_dir, user_config_dir
from tomlkit import table, document, comment, TOMLDocument, load, dump, boolean
from tomlkit.items import Table
from prjman.struct.codec import DictObject
from prjman.module import dynamic_import, load_module

_ENV_VAR: str = 'PRJMAN_CONFIG_DIR'
"""The environment variable pointing to the config directory."""

_CONFIG_DIR: str = 'prjman'
"""The config directory for prjman."""

_CONFIG_FILE: str = 'prjman.toml'
"""The name of the config file."""

def _project_config(dirpath: str, path : str) -> str:
    """Returns the path relative to the project configuration.
    
    Parameters
    ----------
    dirpath : str
        The root directory of the project.
    path : str
        The relativized path.
        
    Returns
    -------
    str
        The path relative to the project configuration.
    """
    return os.sep.join([dirpath, path])

def _env_var_config(path : str) -> str | None:
    """Returns the path relative to the environment variable configuration.
    
    Parameters
    ----------
    path : str
        The relativized path.
        
    Returns
    -------
    str
        The path relative to the environment variable configuration.
    """
    if env_dir := os.getenv(_ENV_VAR):
        return os.sep.join([env_dir, path])
    return None

def _site_config(path : str) -> str | None:
    """Returns the path relative to the site configuration.
    
    Parameters
    ----------
    path : str
        The relativized path.
        
    Returns
    -------
    str
        The path relative to the site configuration.
    """
    return os.sep.join([sys.prefix, _CONFIG_DIR, path]) if sys.prefix != sys.base_prefix else None

def _user_config(path : str) -> str:
    """Returns the path relative to the user configuration.
    
    Parameters
    ----------
    path : str
        The relativized path.
        
    Returns
    -------
    str
        The path relative to the user configuration.
    """
    return user_config_dir(os.sep.join([_CONFIG_DIR, path]), appauthor = False, roaming = True)

def _global_config(path : str) -> str:
    """Returns the path relative to the global configuration.
    
    Parameters
    ----------
    path : str
        The relativized path.
        
    Returns
    -------
    str
        The path relative to the global configuration.
    """
    return site_config_dir(os.sep.join([_CONFIG_DIR, path]), appauthor = False, multipath = True)

class PrjmanProjectConfig:
    """Configurations within the 'project' table."""

    def __init__(self, display_warning_message: bool = True) -> None:
        """
        Parameters
        ----------
        display_warning_message : bool (default 'True')
            When True, shows a warning message when attempting to download a project file.
        """
        self.display_warning_message: bool = display_warning_message

    def encode_toml(self) -> Table:
        """Encodes the 'project' config into a table.

        Returns
        -------
        Table
            The encoded 'project' config.
        """
        project: Table = table()
        project.comment('Project related settings')
        project.add('display_warning_message',
            boolean(self.display_warning_message).comment(
                'When true, shows a warning message when attempting to download a project file'
            )
        )
        return project

    @classmethod
    def decode_toml(cls, obj: DictObject) -> 'PrjmanProjectConfig':
        """Decodes the 'project' table.

        Parameters
        ----------
        obj : dict[str, any]
            The encoded 'project' table.
        
        Returns
        -------
        PrjmanProjectConfig
            The decoded 'project' table.
        """
        return PrjmanProjectConfig(**obj)

class PrjmanConfig:
    """Configurations for prjman."""

    def __init__(self, project: PrjmanProjectConfig = PrjmanProjectConfig(),
            dirpath: str = os.curdir) -> None:
        """
        Parameters
        ----------
        project : PrjmanProjectConfig (default 'PrjmanProjectConfig()')
            The 'project' table within the configuration.
        dirpath : str (default '.')
            The root directory of the project.
        """
        self.project: PrjmanProjectConfig = project
        self.dirpath: str = dirpath

    def encode_toml(self) -> TOMLDocument:
        """Encodes the configuration.

        Returns
        -------
        TOMLDocument
            The encoded configuration.
        """
        doc: TOMLDocument = document()
        doc.add(comment('The configuration file for prjman'))
        doc.add('project', self.project.encode_toml())
        return doc

    @classmethod
    def decode_toml(cls, obj: DictObject) -> 'PrjmanConfig':
        """Decodes the configuration.

        Parameters
        ----------
        obj : dict[str, any]
            The encoded configuration.
        
        Returns
        -------
        PrjmanConfig
            The decoded configuration.
        """
        return PrjmanConfig(project = PrjmanProjectConfig.decode_toml(
                obj['project'] if 'project' in obj else {}
            ), dirpath = obj['dirpath']
        )

    def write_config(self, scope: int = 0) -> None:
        """Writes the configuration to a file within the specified scope.

        Parameters
        ----------
        dirpath : str
            The directory of the loaded project.
        scope : int (default '0')
            A number [0, 3] representing the project, site, user, or global config, respectively.
        """
        output_path: str | None = None

        match scope:
            case 0:
                # Project config
                output_path: str = _project_config(self.dirpath, f'.{_CONFIG_FILE}')
            case 1:
                # Env var config if present
                if env_var := _env_var_config(_CONFIG_FILE):
                    output_path: str = env_var
                # Otherwise site config if present
                elif site_var := _site_config(_CONFIG_FILE):
                    output_path: str = site_var
                # Otherwise user config
                else:
                    output_path: str = _user_config(_CONFIG_FILE)
            case 2:
                # User config
                output_path: str = _user_config(_CONFIG_FILE)
            case 3:
                # Global config
                output_path: str = _global_config(_CONFIG_FILE)
            case _:
                raise ValueError(f'Scope {scope} not supported, must be [0,3].')

        # Write config to file
        with open(output_path, mode = 'w', encoding = 'UTF-8') as file:
            dump(self.encode_toml(), file)

    def update_and_write(self, setter: Callable[['PrjmanConfig'], Any],
            save: bool = False) -> None:
        """Updates and writes the value to the project configuration.
        
        Parameter
        ---------
        setter : (PrjmanConfig) -> None
            A consumer which sets a configuration property.
        save : bool (default 'False')
            When 'True', save the configuration to the project scope.
        """
        setter(self)
        if save:
            self.write_config()

    def load_dynamic_method(self, module_type: str,
            module_method: str) -> Callable[..., bool] | None:
        """Loads a script relative to the module type's directory in the
        project configurations. If the file is present, the module is dynamically
        loaded and provides a corresponding method, which returns true on successful
        operation. If the module cannot be found, then nothing will be returned.

        Parameters
        ----------
        module_type : str
            The type of module being dynamically imported.
        module_method : str
            The name of the module and method to import, formatted as '<module>:<method>'.

        Returns
        -------
        (...) -> bool
            The method loaded by the dynamic importer.
        """
        # Separate module from method and get relative path
        module, method = tuple(module_method.split(':'))
        rel_path: str = f'{os.sep.join([module_type] + module.split("."))}.py'
        module_path: str | None = None

        # Find module path
        if (module == 'internal'):
            return getattr(load_module(f'prjman.{module}.{module_type}'), method)
        
        if (abs_path := _project_config(self.dirpath, rel_path)) and os.path.exists(abs_path):
            module_path = abs_path
        elif (abs_path := _env_var_config(rel_path)) and os.path.exists(abs_path):
            module_path = abs_path
        elif (abs_path := _site_config(rel_path)) and os.path.exists(abs_path):
            module_path = abs_path
        elif (abs_path := _user_config(rel_path)) and os.path.exists(abs_path):
            module_path = abs_path
        elif (abs_path := _global_config(rel_path)) and os.path.exists(abs_path):
            module_path = abs_path

        # Load module if present
        if module_path:
            return getattr(dynamic_import(module_type, module, module_path), method)

        # Return empty processor
        print(f'Could not find module {module_method}; return empty, failing processor.')
        return None


def _update_dict(original: DictObject, merging: DictObject) -> DictObject:
    """Merges the second dictionary into the first without replacing any
    keys.

    Parameters
    ----------
    original : dict[str, any]
        The original dictionary to merge into.
    merging : dict[str, any]
        The dictionary being merged.

    Returns
    -------
    dict[str, any]
        The merged dictionary.
    """
    for key, value in merging.items():
        # Check if value is a dictionary
        if isinstance(value, dict):
            # If so, add key and update dict
            if key not in original:
                original[key] = {}
            _update_dict(original[key], merging[key])
        # Otherwise, merge key if not in original
        elif key not in original:
            original[key] = value
    return original

def _read_and_update_dict(original: DictObject, path: str | None) -> DictObject:
    """Loads a dictionary, if present, and merges it into the existing
    dictionary.
    
    Parameters
    ----------
    original : dict[str, any]
        The current dictionary to merge into.
    path : str
        The path of the dictionary being merged.
    
    Returns
    -------
    dict[str, any]
        The merged dictionary.
    """
    if path and os.path.exists(path):
        with open(path, mode = 'r', encoding = 'UTF-8') as file:
            original = _update_dict(original, load(file))
    return original

def load_config(dirpath: str = os.curdir) -> PrjmanConfig:
    """Loads the configuration for the project. Any settings that are not
    overridden by the project gets merged from the environment variable,
    virtual environment if present, user, and finally the global scope.

    Parameters
    ----------
    dirpath : str
        The root directory of the current project.
    
    Returns
    -------
    PrjmanConfig
        The loaded configuration.
    """
    # Get project config
    config: DictObject = _read_and_update_dict({}, _project_config(dirpath, f'.{_CONFIG_FILE}'))

    # Get environment variable config
    config = _read_and_update_dict(config, _env_var_config(_CONFIG_FILE))

    # Get site config if available
    config = _read_and_update_dict(config, _site_config(_CONFIG_FILE))

    # Read user config
    config = _read_and_update_dict(config, _user_config(_CONFIG_FILE))

    # Read global config
    config = _read_and_update_dict(config, _global_config(_CONFIG_FILE))

    # Set current project directory
    config['dirpath'] = dirpath
    return PrjmanConfig.decode_toml(config)

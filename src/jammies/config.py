"""A script containing the configuration information.
"""

import sys
import os
from glob import iglob
from types import ModuleType
from typing import Callable, Any, Tuple, List, Set
from platformdirs import site_config_dir, user_config_dir
from tomlkit import table, document, comment, TOMLDocument, load, dump, boolean, array
from tomlkit.items import Table, Array
from jammies.log import Logger
from jammies.registrar import JammiesRegistrar
from jammies.struct.codec import DictObject
from jammies.module import dynamic_import, load_module

_ENV_VAR: str = 'JAMMIES_CONFIG_DIR'
"""The environment variable pointing to the config directory."""

_CONFIG_DIR: str = 'jammies'
"""The config directory for jammies."""

_SCRIPT_DIR: str = 'scripts'
"""The script directory for jammies."""

_CONFIG_FILE: str = 'jammies.toml'
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

class JammiesProjectConfig:
    """Configurations within the 'project' table."""

    def __init__(self, display_warning_message: bool = True) -> None:
        """
        Parameters
        ----------
        display_warning_message : bool (default 'True')
            When True, shows a warning message when attempting to download a project file.
        """
        self.display_warning_message: bool = display_warning_message

    def list_vals(self) -> List[str]:
        """Lists all configuration options.
        
        Returns
        -------
        list[str]
            A list of all config options.
        """
        return [
            'display_warning_message'
        ]

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
            boolean(str(self.display_warning_message).casefold()).comment(
                'When true, shows a warning message when attempting to download a project file'
            )
        )
        return project

    @classmethod
    def decode_toml(cls, obj: DictObject) -> 'JammiesProjectConfig':
        """Decodes the 'project' table.

        Parameters
        ----------
        obj : dict[str, any]
            The encoded 'project' table.
        
        Returns
        -------
        JammiesProjectConfig
            The decoded 'project' table.
        """
        return JammiesProjectConfig(**obj)

class JammiesInternalConfig:
    """Configurations within the 'internal' table."""

    def __init__(self, generated: List[str] | None = None) -> None:
        """
        Parameters
        ----------
        generated : list[str] (default `None`)
            A list of generated files.
        """
        self.generated: Set[str] = set(generated) if generated is not None else set()

    def clear_generated_files(self) -> None:
        """Clears all generated files from the config."""
        self.generated.clear()

    def add_generated_file(self, path: str) -> None:
        """Adds a generated file to the list of generated files.

        Parameters
        ----------
        path : str
            The path of the generated file.
        """
        self.generated.add(path)

    def encode_toml(self) -> Table:
        """Encodes the 'internal' config into a table.

        Returns
        -------
        Table
            The encoded 'internal' config.
        """
        internal: Table = table()
        internal.comment('Internal data for current project (DO NOT MODIFY)')

        generated: Array = array()
        generated.comment('Files generated by the project')
        for file in self.generated:
            generated.add_line(file)
        internal.append('generated', generated)

        return internal

    @classmethod
    def decode_toml(cls, obj: DictObject) -> 'JammiesInternalConfig':
        """Decodes the 'internal' table.

        Parameters
        ----------
        obj : dict[str, any]
            The encoded 'internal' table.
        
        Returns
        -------
        JammiesInternalConfig
            The decoded 'internal' table.
        """
        return JammiesInternalConfig(**obj)

class JammiesConfig:
    """Configurations for jammies."""

    def __init__(self, project: JammiesProjectConfig = JammiesProjectConfig(),
            internal: JammiesInternalConfig = JammiesInternalConfig(),
            dirpath: str = os.curdir) -> None:
        """
        Parameters
        ----------
        project : JammiesProjectConfig (default 'JammiesProjectConfig()')
            The 'project' table within the configuration.
        dirpath : str (default '.')
            The root directory of the project.
        """
        self.project: JammiesProjectConfig = project
        self.internal: JammiesInternalConfig = internal
        self.dirpath: str = dirpath

    def list_vals(self) -> Tuple[bool, str]:
        """Lists all configuration options.
        
        Returns
        -------
        list[str]
            A list of all config options.
        """

        output: List[str] = []
        output += map(lambda s: f'project.{s}', self.project.list_vals())
        return output

    def get_val(self, name: str) -> Tuple[bool, str]:
        """Gets the value associated with the config name.
        
        Parameters
        ----------
        name : str
            The key associated with the config value.
        
        Returns
        -------
        (bool, str)
            A tuple containing whether the operation was successful
            and the associated message.
        """
        # Do not allow access to internal params
        if 'internal' in name:
            return (False, 'Accessing internal options is not allowed.')

        val: Any = self
        for key in name.split('.'):
            if not hasattr(val, key):
                return (False, f'\'{name}\' is not a valid config option.')
            val = getattr(val, key)
        return (True, str(val))

    def set_val(self, name: str, new_value: Any) -> Tuple[bool, str]:
        """Sets the value for the associated config name.
        
        Parameters
        ----------
        name : str
            The key associated with the config value.
        
        Returns
        -------
        (bool, str)
            A tuple containing whether the operation was successful
            and the associated message.
        """
        # Do not allow access to internal params
        if 'internal' in name:
            return (False, 'Accessing internal options is not allowed.')

        name_path: List[str] = name.split('.')
        # Get second to last attribute
        val: Any = self
        for key in name_path[:-1]:
            if not hasattr(val, key):
                return (False, f'\'{name}\' is not a valid config option.')
            val = getattr(val, key)

        if not hasattr(val, final_name := name_path[-1]):
            return (False, f'\'{name}\' is not a valid config option.')

        # Store previous value for update and cast type
        prev: Any = getattr(val, final_name)
        setattr(val, final_name,
            new_value := (str(new_value).casefold() == 'True'.casefold()
                if isinstance(prev, bool)
                else type(prev)(new_value))
        )

        return (True, f'{str(prev)} -> {str(new_value)}')

    def encode_toml(self, write_internal: bool = False) -> TOMLDocument:
        """Encodes the configuration.

        Returns
        -------
        TOMLDocument
            The encoded configuration.
        """
        doc: TOMLDocument = document()
        doc.add(comment('The configuration file for jammies'))
        doc.add('project', self.project.encode_toml())

        if write_internal:
            doc.add('internal', self.internal.encode_toml())
        return doc

    @classmethod
    def decode_toml(cls, obj: DictObject) -> 'JammiesConfig':
        """Decodes the configuration.

        Parameters
        ----------
        obj : dict[str, any]
            The encoded configuration.
        
        Returns
        -------
        JammiesConfig
            The decoded configuration.
        """
        return JammiesConfig(project = JammiesProjectConfig.decode_toml(
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
        output_path: str = config_loc(dirpath = self.dirpath, scope = scope)

        # Create directories that are missing
        os.makedirs(os.path.dirname(output_path), exist_ok = True)

        # Write config to file
        with open(output_path, mode = 'w', encoding = 'UTF-8') as file:
            dump(self.encode_toml(write_internal = scope == 0), file)

    def update_and_write(self, setter: Callable[['JammiesConfig'], Any],
            save: bool = False) -> None:
        """Updates and writes the value to the project configuration.
        
        Parameter
        ---------
        setter : (JammiesConfig) -> None
            A consumer which sets a configuration property.
        save : bool (default 'False')
            When 'True', save the configuration to the project scope.
        """
        setter(self)
        if save:
            self.write_config()

    def load_dynamic_scripts(self, logger: Logger, registrar: JammiesRegistrar) -> int:
        """Loads all scripts within the 'scripts' directories defined by the configuration.
        All scripts with the appropriate 'setup' method will be ran.

        Parameters
        ----------
        logger : Logger
            A logger for reporting on information.
        registrar : `JammiesRegistrar`
            The registrar used to register the components for the project.
        
        Returns
        -------
        int
            The number of loaded scripts.
        """

        def import_scripts(script_dir: str) -> int:
            """Imports all scripts from the current directory and executes the 'setup'
            method if present. No recursion is done.
            
            Parameters
            ----------
            script_dir : str
                The directory to look for scripts
                
            Returns
            -------
            int
                The number of loaded scripts.
            """

            scripts: int = 0

            for script in iglob(os.sep.join([script_dir, '**.py'])):
                module: ModuleType = dynamic_import(
                    _SCRIPT_DIR,
                    os.path.basename(script).rsplit(os.extsep, maxsplit = 1)[0],
                    script
                )
                if (setup_method := getattr(module, 'setup', None)) is not None:
                    logger.debug(f'Registering script: {script}')
                    setup_method(registrar)
                    scripts += 1

            return scripts

        loaded_scripts: int = 0

        # Check config locations for 'scripts' directory
        if (script_dir := _project_config(self.dirpath, _SCRIPT_DIR)) and os.path.isdir(script_dir):
            logger.debug(f'Script directory detected: {script_dir}')
            loaded_scripts += import_scripts(script_dir)
        if (script_dir := _env_var_config(_SCRIPT_DIR)) and os.path.isdir(script_dir):
            logger.debug(f'Script directory detected: {script_dir}')
            loaded_scripts += import_scripts(script_dir)
        if (script_dir := _site_config(_SCRIPT_DIR)) and os.path.isdir(script_dir):
            logger.debug(f'Script directory detected: {script_dir}')
            loaded_scripts += import_scripts(script_dir)
        if (script_dir := _user_config(_SCRIPT_DIR)) and os.path.isdir(script_dir):
            logger.debug(f'Script directory detected: {script_dir}')
            loaded_scripts += import_scripts(script_dir)
        if (script_dir := _global_config(_SCRIPT_DIR)) and os.path.isdir(script_dir):
            logger.debug(f'Script directory detected: {script_dir}')
            loaded_scripts += import_scripts(script_dir)

        return loaded_scripts

    # TODO: Deprecate for removal
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
        if module == 'internal':
            return getattr(load_module(f'jammies.{module}.{module_type}'), method)

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
        # Check if key isn't already present
        if key not in original:
             # Check if value is a dictionary
            if isinstance(value, dict):
                # If so, add key and update dict
                original[key] = {}
                _update_dict(original[key], merging[key])
            else:
                # Otherwise, merge key
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

def load_config(dirpath: str = os.curdir) -> JammiesConfig:
    """Loads the configuration for the project. Any settings that are not
    overridden by the project gets merged from the environment variable,
    virtual environment if present, user, and finally the global scope.

    Parameters
    ----------
    dirpath : str
        The root directory of the current project.
    
    Returns
    -------
    JammiesConfig
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
    return JammiesConfig.decode_toml(config)

def config_loc(dirpath: str = os.curdir, scope: int = 0) -> str:
    """Gets the location of the configuration in the specified scope.

    Parameters
    ----------
    dirpath : str
        The directory of the loaded project.
    scope : int (default '0')
        A number [0, 3] representing the project, site, user, or global config, respectively.
    
    Returns
    -------
    str
        The location of the configuration.
    """
    output_path: str | None = None

    match scope:
        case 0:
            # Project config
            output_path: str = _project_config(dirpath, f'.{_CONFIG_FILE}')
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

    return output_path

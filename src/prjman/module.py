"""A script which holds all lazy references to a given
class."""

import sys
from types import ModuleType
from typing import Callable
from importlib.machinery import ModuleSpec
from importlib.util import find_spec, LazyLoader, module_from_spec, spec_from_file_location

def _load_module(module_name: str,
        spec_getter: Callable[[str], ModuleSpec] = find_spec) -> ModuleType:
    """Loads a module based on its name and getter for the spec.
    If the module is already loaded, it will be used instead.

    Parameters
    ----------
    module_name : str
        The name of the module to load.
    spec_getter : (str) -> ModuleSpec (default 'importlib.util.find_spec')
        Determines how to load the spec with the specified module name.
    
    Returns
    -------
    ModuleType
        The loaded module.
    """
    # If already loaded, just return the module
    if module_name in sys.modules:
        return sys.modules[module_name]

    # Load module if not present
    spec: ModuleSpec = spec_getter(module_name)
    module: ModuleType = module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

def _lazy_import(name: str) -> ModuleType:
    """Sets up the module to be lazily imported if it is not already loaded.

    Parameters
    ----------
    name : str
        The name of the module to lazily load.
    
    Returns
    -------
    types.ModuleType
        The module which will be loaded on first execution.
    """

    def _set_lazy(module_name: str) -> ModuleSpec:
        """Sets the spec loader to load the module lazily.

        Parameters
        ----------
        module_name : str
            The name of the module to lazily load.
        
        Returns
        -------
        ModuleSpec
            The lazily loaded spec.
        """

        # Make spec lazily loaded
        spec: ModuleSpec | None = find_spec(module_name)
        loader: LazyLoader = LazyLoader(spec.loader)
        spec.loader = loader
        return spec

    return _load_module(name, spec_getter = _set_lazy)

SINGLETON: ModuleType = _lazy_import('prjman.singleton')
"""The prjman.singleton module added as a lazy import."""

def dynamic_import(module_type: str, name: str, path: str) -> ModuleType:
    """Dynamically imports a module into the current Python executable.
    Modules dynamically imported will be prefixed with `prjman.dynamic`,
    followed by the module type and the associated name.

    Parameters
    ----------
    module_type : str
        The type of module being dynamically imported.
    name : str
        The name of the module to import.
    path : str
        The location of the module to import.
    
    Returns
    -------
    ModuleType
        The dynamically loaded module.
    """
    module_name: str = f'prjman.dynamic.{module_type}.{name}'

    return _load_module(module_name,
        spec_getter = lambda mdn: spec_from_file_location(mdn, location = path))

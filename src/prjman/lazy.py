"""A script which holds all lazy references to a given
class."""

import sys
from types import ModuleType
from typing import Dict
from importlib.machinery import ModuleSpec
from importlib.util import find_spec, LazyLoader, module_from_spec, spec_from_file_location

_LAZY_IMPORTS: Dict[str, ModuleType] = {}
"""A dictionary containing all the modules that were lazily imported."""

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

    # If already loaded, just return the module
    if name in sys.modules:
        return sys.modules[name]

    # Otherwise, if the import is already lazy, return the module
    if name in _LAZY_IMPORTS:
        return _LAZY_IMPORTS[name]

    # Otherwise, make import lazy and return module
    spec: ModuleSpec | None = find_spec(name)
    loader: LazyLoader = LazyLoader(spec.loader)
    spec.loader = loader
    module: ModuleType = module_from_spec(spec)
    sys.modules[name] = module
    loader.exec_module(module)
    _LAZY_IMPORTS[name] = module
    return module

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
    spec: ModuleSpec | None = spec_from_file_location(module_name, location = path)
    module: ModuleType = module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

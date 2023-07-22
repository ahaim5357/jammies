"""A script containing the implemented registrar used within the project."""

from typing import Dict, Any

from jammies.log import Logger
from jammies.config import JammiesConfig
from jammies.struct.registry import Registry
from jammies.registrar import JammiesRegistrar, ProjectFileBuilder
from jammies.defn.file import ProjectFileCodec, PostProcessor
from jammies.defn.metadata import METADATA_CODEC

import jammies.internal.file.osf as file_osf
import jammies.internal.file.url as file_url
import jammies.internal.file.gitrepo as file_git
import jammies.internal.postprocessor.unpack as post_unpack
import jammies.internal.postprocessor.notebook as post_notebook

class RegistryError(Exception):
    """Raised when an error occurs when operating on a registry."""

class JammiesRegistrarImpl(JammiesRegistrar):
    """An implementation of the registrar class used to hold
    the registered instances of the project.
    """

    def __init__(self) -> None:
        """"""

        # Initialize Stager
        # 0: Internal Logic
        # 1: Dynamic Script Logic
        # 2: Frozen
        self.__stager: int = 0

        # Project File Handlers
        self.file_codecs: Registry[ProjectFileCodec] = Registry()
        self.file_builders: Registry[ProjectFileBuilder] = Registry()
        self.file_handler_exceptions: Registry[str] = Registry()

        # Post Processors
        self.post_processors: Registry[PostProcessor] = Registry()
        self.post_processor_exceptions: Registry[str] = Registry()

    def __check_preconditions(self, name: str, registry: Dict[str, Any],
            registry_type: str) -> None:
        """Checks the preconditions necessary to access a registry method.
        
        Parameters
        ----------
        name : str
            The name of the object to register.
        registry : dict
            The registry to registry the object to.
        registry_type : str
            A string representation of the registry data.
        """

        if self.__stager > 1:
            raise RegistryError(f'{name} could not be registered; the registry has been frozen.')
        if self.__stager > 0 and ':' not in name:
            raise ValueError(f'{name} must contain a \':\', '\
                + 'where the prefix represents a unique identifier for the group of scripts.')
        if name in registry:
            raise ValueError(f'{name} already has a registered {registry_type}.')

    def register_file_handler(self, name: str, codec: ProjectFileCodec,
            builder: ProjectFileBuilder) -> None:
        self.__check_preconditions(name, self.file_codecs, 'file handler')

        self.file_codecs[name] = codec
        self.file_builders[name] = builder

    def add_file_handler_missing_message(self, name: str, message: str) -> None:
        self.__check_preconditions(name, self.file_handler_exceptions, 'message')
        if name in self.file_codecs:
            raise ValueError(f'{name} is registered, a message handler is not needed.')

        self.file_handler_exceptions[name] = message

    def register_post_processor(self, name: str, post_processor: PostProcessor) -> None:
        self.__check_preconditions(name, self.post_processors, 'post processor')

        self.post_processors[name] = post_processor

    def add_post_processor_missing_message(self, name: str, message: str) -> None:
        self.__check_preconditions(name, self.post_processor_exceptions, 'message')
        if name in self.post_processors:
            raise ValueError(f'{name} is registered, a message handler is not needed.')

        self.post_processor_exceptions[name] = message

    def get_project_file_codec(self, name: str) -> ProjectFileCodec:
        return self.file_codecs[name]

    def get_project_file_builder(self, name: str) -> ProjectFileBuilder:
        return self.file_builders[name]

    def get_post_processor(self, name: str) -> PostProcessor:
        return self.post_processors[name]

    def get_available_builders(self) -> list[str]:
        return self.file_builders.keys()

    def stage(self) -> None:
        """Stages the registrar into its next state.
        """
        self.__stager += 1

REGISTRAR: JammiesRegistrar = JammiesRegistrarImpl()

def setup(logger: Logger, config: JammiesConfig) -> None:
    """Initializes the information within the registrar.

    Parameters
    ----------
    logger : `Logger`
        A logger for reporting on information.
    config : `JammiesConfig`
        The configuration settings.
    """

    # Setup basic values
    METADATA_CODEC.registrar = REGISTRAR

    # Register internal implementations
    logger.debug('Registering internal implementations...')
    file_osf.setup(REGISTRAR)
    file_url.setup(REGISTRAR)
    file_git.setup(REGISTRAR)
    post_unpack.setup(REGISTRAR)
    post_notebook.setup(REGISTRAR)

    REGISTRAR.stage()

    # Register dynamic implementations
    logger.debug('Registering dynamic implementations...')
    loaded_scripts: int = config.load_dynamic_scripts(logger, REGISTRAR)
    if loaded_scripts > 0:
        logger.debug(f'Successfully loaded {loaded_scripts} scripts')

    REGISTRAR.stage()

"""A script containing the definition of a registrar used to register
the necessary components of the project.
"""
from typing import TypeAlias, Callable
from abc import ABC, abstractmethod
from jammies.defn.file import ProjectFileCodec, ProjectFile, PostProcessor

ProjectFileBuilder: TypeAlias = Callable[['JammiesRegistrar'], ProjectFile]
"""A supplier used to construct a ProjectFile from an user's input."""

class JammiesRegistrar(ABC):
    """A registrar for the project. Provides endpoints to register file
    handlers and post processors.
    """

    def __init__(self) -> None:
        """"""

    @abstractmethod
    def register_file_handler(self, name: str, codec: ProjectFileCodec,
            builder: ProjectFileBuilder) -> None:
        """Registers a `ProjectFile` handler. A handler is used to pull file
        from a given location.
        
        Parameters
        ----------
        name : str
            The name of the file handler to register.
        codec : `ProjectFileCodec`
            The codec used to encode and decode the `ProjectFile`.
        builder : `ProjectFileBuilder`
            The builder used to construct the project file within a
            shell.
        """

    @abstractmethod
    def add_file_handler_missing_message(self, name: str, message: str) -> None:
        """Adds a message for a file handler if it is referenced without
        being registered. A message should be registered as an alternative
        to a file handler.
        
        Parameters
        ----------
        name : str
            The name of the file handler to register.
        message : str
            The message to display when not present.
        """

    @abstractmethod
    def register_post_processor(self, name: str, post_processor: PostProcessor) -> None:
        """Registers a post processor. A post processor is used to apply
        additional changes to a `ProjectFile` after it has been pulled.
        
        Parameters
        ----------
        name : str
            The name of the post processor to register.
        post_processor : `PostProcessor`
            The post processor to apply to a project file.
        """

    @abstractmethod
    def add_post_processor_missing_message(self, name: str, message: str) -> None:
        """Adds a message for a post processor if it is referenced without
        being registered. A message should be registered as an alternative
        to a post processor.
        
        Parameters
        ----------
        name : str
            The name of the post processor to register.
        message : str
            The message to display when not present.
        """

    @abstractmethod
    def get_project_file_codec(self, name: str) -> ProjectFileCodec:
        """Gets a `ProjectFileCodec` for the associated name.

        Parameters
        ----------
        name : str
            The name of the codec.

        Returns
        -------
        `ProjectFileCodec`
            The registered codec.
        """

    @abstractmethod
    def get_project_file_builder(self, name: str) -> ProjectFileBuilder:
        """Gets a `ProjectFileBuilder` for the associated name.

        Parameters
        ----------
        name : str
            The name of the builder.

        Returns
        -------
        `ProjectFileBuilder`
            The registered builder.
        """

    @abstractmethod
    def get_post_processor(self, name: str) -> PostProcessor:
        """Gets a `PostProcessor` for the associated name.

        Parameters
        ----------
        name : str
            The name of the post processor.

        Returns
        -------
        `PostProcessor`
            The registered post processor.
        """

    @abstractmethod
    def get_available_builders(self) -> list[str]:
        """Returns a list of the available project file builders.
        
        Returns
        -------
        list of str
            A list of project file builder names.
        """

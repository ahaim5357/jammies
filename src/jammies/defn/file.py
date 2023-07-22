"""A script containing information about handing a project file read
from the metadata.
"""

import os
from typing import TypeVar, List, Callable, Tuple, TypeAlias
from abc import ABC, abstractmethod
from jammies.log import Logger
from jammies.utils import get_default, get_or_default
from jammies.struct.codec import DictObject, DictCodec

PostProcessor: TypeAlias = Callable[[Logger, str], bool]
"""A method which takes in the directory to execute within and returns
a boolean represent whether the execution was successful.
"""

class ProjectFile(ABC):
    """An abstract class containing information about a file associated with the project.
    """

    @abstractmethod
    def __init__(self, codec: 'ProjectFileCodec',
            name: str = "", rel_dir: str = os.curdir,
            post_processor: Tuple[PostProcessor, DictObject] | None = None,
            extra: DictObject | None = None) -> None:
        """
        Parameters
        ----------
        name : str (default '')
            The name of the project file.
        rel_dir : str (default '.')
            The directory the project file is located.
        post_processor : `PostProcessor`, `DictObject` (default `None`)
            The post processor to apply to the project file with any additional metadata.
        extra : dict[str, Any] (default `None`)
            Extra data defined by the user.
        """
        super().__init__()
        self._codec: 'ProjectFileCodec' = codec
        self.name: str = name
        self.dir: str = rel_dir
        self.post_processor: Tuple[PostProcessor, DictObject] = post_processor
        self.extra: DictObject = {} if extra is None else extra

    @abstractmethod
    def registry_name(self) -> str:
        """Returns the registered name of the project file.

        Returns
        -------
        str
            The registered name of the project file.
        """

    def codec(self) -> 'ProjectFileCodec':
        """Returns the codec used to encode and decode this project file.

        Returns
        -------
        ProjectFileCodec
            The codec used to encode and decode this project file.
        """
        return self._codec

    @abstractmethod
    def setup(self, root_dir: str) -> bool:
        """Sets up the project file for usage.

        Parameters
        ----------
        root_dir : str
            The root directory to set up the project file in.
        """
        os.makedirs(self._create_path(root_dir), exist_ok = True)
        return False

    def _create_path(self, root_dir: str, *paths: str) -> str:
        """Constructs a path from the root directory through the relative
        directory and any additional paths specified.

        Parameters
        ----------
        root_dir : str
            The root directory to create the path from.
        *paths : str
            The paths after the project file's relative directory.

        Returns
        -------
        str
            The newly created path.
        """
        fpath: List[str] = [root_dir, self.dir]
        fpath += paths
        return os.sep.join(fpath)

PF = TypeVar('PF', bound = ProjectFile)
"""The type of the project file."""

class ProjectFileCodec(DictCodec[PF]):
    """An abstract, generic encoder and decoder between a dictionary and a ProjectFile.

    Types
    -----
    PF
        The type of the project file to be encoded or decoded to.
    """

    def __init__(self, registrar) -> None:
        """Initializes a codec for a `ProjectFile`.

        Parameters
        ----------
        registrar : `JammiesRegistrar`
            The registrar used to register the components for the project.
        """
        self.registrar = registrar

    def decode(self, obj: DictObject) -> PF:
        return self.decode_type(obj,
            name = get_or_default(obj, 'name', ProjectFile),
            rel_dir = get_or_default(obj, 'dir', ProjectFile, param = 'rel_dir'),
            post_processor = self.__decode_post_processor(
                get_or_default(obj, 'post_processor', ProjectFile)
            ),
            extra = get_or_default(obj, 'extra', ProjectFile)
        )

    def __decode_post_processor(self,
            post_processor: DictObject | None) -> Tuple[PostProcessor, DictObject]:
        """Decodes a post processor from its object.

        Parameters
        ----------
        post_processor : `DictObject`
            The encoded post processor.
        
        Returns
        -------
        (`PostProcessor`, `DictObject`)
            The post processor and its additional parameters.
        """
        return (self.registrar.get_post_processor(post_processor['type']), post_processor) \
            if post_processor is not None else None

    @abstractmethod
    def decode_type(self, obj: DictObject, **kwargs: DictObject) -> PF:
        """Decodes a dictionary to the specific ProjectFile type.

        Parameters
        ----------
        obj : Dict[str, Any]
            The dictionary containing the data for the ProjectFile.

        Returns
        -------
        PF
            The decoded ProjectFile.
        """

    def encode(self, obj: PF) -> DictObject:
        dict_obj: DictObject = {}
        dict_obj['type'] = obj.registry_name()
        if obj.name:
            dict_obj['name'] = obj.name
        if obj.dir != get_default(ProjectFile, 'rel_dir'):
            dict_obj['dir'] = obj.dir
        if obj.post_processor:
            dict_obj['post_processor'] = obj.post_processor[1]
        if obj.extra:
            dict_obj['extra'] = obj.extra

        return self.encode_type(obj, dict_obj)

    @abstractmethod
    def encode_type(self, obj: PF, dict_obj: DictObject) -> DictObject:
        """Encodes a specific ProjectFile type to the dictionary.

        Parameters
        ----------
        obj : PF
            The ProjectFile containing the data.
        dict_obj : Dict[str, Any]
            The dictionary containing some common encoded data.

        Returns
        -------
        Dict[str, Any]
            The encoded ProjectFile in a dictionary.
        """

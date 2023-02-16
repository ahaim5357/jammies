import os
from typing import TypeVar
from abc import ABC, abstractmethod
from project_patcher.struct.codec import DictObject, DictCodec
from project_patcher.utils import get_default, get_or_default

class ProjectFile(ABC):
    """An abstract class containing information about a file associated with the project.
    """

    @abstractmethod
    def __init__(self, dir: str = os.curdir) -> None:
        """
        Parameters
        ----------
        dir : str (default '.')
            The directory the project file is located.
        """
        super().__init__()
        self.dir: str = dir
    
    @abstractmethod
    def codec(self) -> 'ProjectFileCodec':
        """Returns the codec used to encode and decode this project file.

        Returns
        -------
        ProjectFileCodec
            The codec used to encode and decode this project file.
        """
        pass

PF = TypeVar('PF', bound = ProjectFile)
"""The type of the project file."""

class ProjectFileCodec(DictCodec[PF]):
    """An abstract, generic encoder and decoder between a dictionary and a ProjectFile.

    Types
    -----
    PF
        The type of the project file to be encoded or decoded to.
    """
    
    def decode(self, obj: DictObject) -> PF:
        return self.decode_type(get_or_default(obj, 'dir', ProjectFile), obj)

    @abstractmethod
    def decode_type(self, dir: str, obj: DictObject) -> PF:
        """Decodes a dictionary to the specific ProjectFile type.

        Parameters
        ----------
        dir : str
            The directory the ProjectFile is located.
        obj : Dict[str, Any]
            The dictionary containing the data for the ProjectFile.

        Returns
        -------
        PF
            The decoded ProjectFile.
        """
        pass

    def encode(self, obj: PF) -> DictObject:
        # Lazily load registry
        from project_patcher.singleton import _PROJECT_FILE_TYPES

        dict_obj: DictObject = {}
        dict_obj['type'] = _PROJECT_FILE_TYPES.get_key(self)
        if obj.dir != get_default(ProjectFile, 'dir'):
            dict_obj['dir'] = obj.dir

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
        pass

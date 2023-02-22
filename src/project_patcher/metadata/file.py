"""A script containing information about handing a project file read
from the metadata.
"""

import os
from typing import TypeVar, List
from abc import ABC, abstractmethod
from project_patcher.lazy import SINGLETON
from project_patcher.utils import get_default, get_or_default
from project_patcher.struct.codec import DictObject, DictCodec

class ProjectFile(ABC):
    """An abstract class containing information about a file associated with the project.
    """

    @abstractmethod
    def __init__(self, rel_dir: str = os.curdir) -> None:
        """
        Parameters
        ----------
        rel_dir : str (default '.')
            The directory the project file is located.
        """
        super().__init__()
        self.dir: str = rel_dir

    @abstractmethod
    def codec(self) -> 'ProjectFileCodec':
        """Returns the codec used to encode and decode this project file.

        Returns
        -------
        ProjectFileCodec
            The codec used to encode and decode this project file.
        """

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

    def decode(self, obj: DictObject) -> PF:
        return self.decode_type(get_or_default(obj, 'dir', ProjectFile, param = 'rel_dir'), obj)

    @abstractmethod
    def decode_type(self, rel_dir: str, obj: DictObject) -> PF:
        """Decodes a dictionary to the specific ProjectFile type.

        Parameters
        ----------
        rel_dir : str
            The directory the ProjectFile is located.
        obj : Dict[str, Any]
            The dictionary containing the data for the ProjectFile.

        Returns
        -------
        PF
            The decoded ProjectFile.
        """

    def encode(self, obj: PF) -> DictObject:
        dict_obj: DictObject = {}
        dict_obj['type'] = SINGLETON.PROJECT_FILE_TYPES.get_key(self)
        if obj.dir != get_default(ProjectFile, 'rel_dir'):
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

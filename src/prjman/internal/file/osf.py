"""A script obtaining a project file from an Open Science Framework
project.
"""

from prjman.struct.codec import DictObject
from prjman.defn.file import ProjectFile, ProjectFileCodec
from prjman.defn.builder import build_file
from prjman.utils import download_and_write
from prjman.registrar import PrjmanRegistrar

def setup(registrar: PrjmanRegistrar) -> None:
    """A setup method used to register components to the project.
    
    Parameters
    ----------
    registrar : `PrjmanRegistrar`
        The registrar used to register the components for the project.
    """

    # Create codec
    codec: OSFProjectFileCodec = OSFProjectFileCodec(registrar)

    registrar.register_file_handler(_REGISTRY_NAME, codec, build_osf)

_REGISTRY_NAME: str = 'osf'
"""The registry name of the project file handler."""

class OSFProjectFile(ProjectFile):
    """A project file for an Open Science Framework repository."""

    def __init__(self, project_id: str, **kwargs: DictObject) -> None:
        """
        Parameters
        ----------
        project_id : str
            The five character identifier of the repository.
        """
        super().__init__(**kwargs)
        self.project_id: str = project_id
        self.__url: str = \
            f'https://files.osf.io/v1/resources/{project_id}/providers/osfstorage/?zip='

    def registry_name(self) -> str:
        return _REGISTRY_NAME

    def setup(self, root_dir: str) -> bool:
        super().setup(root_dir)
        return download_and_write(self.__url, out_dir = self._create_path(root_dir))

def build_osf(registrar: PrjmanRegistrar) -> OSFProjectFile:
    """Builds an OSFProjectFile from user input.
    
    Parameters
    ----------
    registrar : `PrjmanRegistrar`
        The registrar used to register the components for the project.

    Returns
    -------
    OSFProjectFile
        The built project file.
    """
    project_id: str = input('OSF Project Id: ')
    return build_file(registrar, _REGISTRY_NAME,
        lambda kwargs: OSFProjectFile(project_id, **kwargs)
    )

class OSFProjectFileCodec(ProjectFileCodec[OSFProjectFile]):
    """A codec for encoding and decoding an OSFProjectFile.
    """

    def encode_type(self, obj: OSFProjectFile, dict_obj: DictObject) -> DictObject:
        dict_obj['id'] = obj.project_id
        return dict_obj

    def decode_type(self, obj: DictObject, **kwargs: DictObject) -> OSFProjectFile:
        kwargs['codec'] = self # Set codec
        return OSFProjectFile(obj['id'], **kwargs)

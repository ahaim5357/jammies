"""A script obtaining a project file from an Open Science Framework
project.
"""

from prjman.lazy import SINGLETON
from prjman.struct.codec import DictObject
from prjman.metadata.file import ProjectFile, ProjectFileCodec, build_file
from prjman.utils import download_and_write

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

    def codec(self) -> 'ProjectFileCodec':
        return SINGLETON.OSF_FILE_CODEC

    def setup(self, root_dir: str) -> bool:
        super().setup(root_dir)
        return download_and_write(self.__url, out_dir = self._create_path(root_dir))

def build_osf() -> OSFProjectFile:
    """Builds an OSFProjectFile from user input.
    
    Returns
    -------
    OSFProjectFile
        The built project file.
    """
    project_id: str = input('OSF Project Id: ')
    return build_file(lambda kwargs: OSFProjectFile(project_id, **kwargs))

class OSFProjectFileCodec(ProjectFileCodec[OSFProjectFile]):
    """A codec for encoding and decoding an OSFProjectFile.
    """

    def encode_type(self, obj: OSFProjectFile, dict_obj: DictObject) -> DictObject:
        dict_obj['id'] = obj.project_id
        return dict_obj

    def decode_type(self, obj: DictObject, **kwargs: DictObject) -> OSFProjectFile:
        return OSFProjectFile(obj['id'], **kwargs)

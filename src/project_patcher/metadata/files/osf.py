import os
from project_patcher.struct.codec import DictObject
from project_patcher.metadata.file import ProjectFile, ProjectFileCodec
from project_patcher.integration.i_requests import download_and_write

class OSFProjectFile(ProjectFile):
    """A project file for an Open Science Framework repository."""

    def __init__(self, id: str, dir: str = os.curdir) -> None:
        """
        Parameters
        ----------
        id : str
            The five character identifier of the repository.
        dir : str (default '.')
            The directory the project file is located.
        """
        super().__init__(dir)
        self.id: str = id
        self.__url: str = f'https://files.osf.io/v1/resources/{id}/providers/osfstorage/?zip='
    
    def codec(self) -> 'ProjectFileCodec':
        # Lazily load singletons
        from project_patcher.singleton import OSF_FILE_CODEC
        return OSF_FILE_CODEC

    def setup(self, root_dir: str) -> bool:
        super().setup(root_dir)
        return download_and_write(self.__url, dir = self._create_path(root_dir))

class OSFProjectFileCodec(ProjectFileCodec[OSFProjectFile]):
    """A codec for encoding and decoding an OSFProjectFile.
    """

    def encode_type(self, obj: OSFProjectFile, dict_obj: DictObject) -> DictObject:
        dict_obj['id'] = obj.id
        return dict_obj

    def decode_type(self, dir: str, obj: DictObject) -> OSFProjectFile:
        return OSFProjectFile(obj['id'], dir=dir)

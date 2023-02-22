"""A script obtaining a project file from an Open Science Framework
project.
"""

import os
from project_patcher.lazy import SINGLETON
from project_patcher.struct.codec import DictObject
from project_patcher.metadata.file import ProjectFile, ProjectFileCodec
from project_patcher.integration.i_requests import download_and_write

class OSFProjectFile(ProjectFile):
    """A project file for an Open Science Framework repository."""

    def __init__(self, project_id: str, rel_dir: str = os.curdir) -> None:
        """
        Parameters
        ----------
        project_id : str
            The five character identifier of the repository.
        rel_dir : str (default '.')
            The directory the project file is located.
        """
        super().__init__(rel_dir)
        self.project_id: str = project_id
        self.__url: str = \
            f'https://files.osf.io/v1/resources/{project_id}/providers/osfstorage/?zip='

    def codec(self) -> 'ProjectFileCodec':
        return SINGLETON.OSF_FILE_CODEC

    def setup(self, root_dir: str) -> bool:
        super().setup(root_dir)
        return download_and_write(self.__url, out_dir = self._create_path(root_dir))

class OSFProjectFileCodec(ProjectFileCodec[OSFProjectFile]):
    """A codec for encoding and decoding an OSFProjectFile.
    """

    def encode_type(self, obj: OSFProjectFile, dict_obj: DictObject) -> DictObject:
        dict_obj['id'] = obj.project_id
        return dict_obj

    def decode_type(self, rel_dir: str, obj: DictObject) -> OSFProjectFile:
        return OSFProjectFile(obj['id'], rel_dir = rel_dir)

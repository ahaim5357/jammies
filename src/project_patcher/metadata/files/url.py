"""A script obtaining a project file from a download url.
"""

import os
from typing import Optional
from project_patcher.lazy import SINGLETON
from project_patcher.struct.codec import DictObject
from project_patcher.metadata.file import ProjectFile, ProjectFileCodec, build_file
from project_patcher.utils import download_and_write

class URLProjectFile(ProjectFile):
    """A project file for a file at a downloadable url link.
    The file will be obtained via a GET request."""

    def __init__(self, url: str, rel_dir: str = os.curdir,
            extra: Optional[DictObject] = None) -> None:
        """
        Parameters
        ----------
        url : str
            The downloadable link for the file.
        rel_dir : str (default '.')
            The directory the project file is located.
        extra : dict[str, Any]
            Extra data defined by the user.
        """
        super().__init__(rel_dir, extra)
        self.url: str = url

    def codec(self) -> 'ProjectFileCodec':
        return SINGLETON.URL_FILE_CODEC

    def setup(self, root_dir: str) -> bool:
        super().setup(root_dir)
        return download_and_write(self.url, unzip_file = False,
            out_dir = self._create_path(root_dir))

def build_url() -> URLProjectFile:
    """Builds an URLProjectFile from user input.
    
    Returns
    -------
    URLProjectFile
        The built project file.
    """
    url: str = input('Direct URL Link: ')
    return build_file(lambda rel_dir: URLProjectFile(url, rel_dir = rel_dir))

class URLProjectFileCodec(ProjectFileCodec[URLProjectFile]):
    """A codec for encoding and decoding an URLProjectFile.
    """

    def encode_type(self, obj: URLProjectFile, dict_obj: DictObject) -> DictObject:
        dict_obj['url'] = obj.url
        return dict_obj

    def decode_type(self, rel_dir: str, extra: Optional[DictObject],
            obj: DictObject) -> URLProjectFile:
        return URLProjectFile(obj['url'], rel_dir = rel_dir, extra = extra)

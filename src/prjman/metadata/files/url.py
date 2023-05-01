"""A script obtaining a project file from a download url.
"""

from prjman.lazy import SINGLETON
from prjman.struct.codec import DictObject
from prjman.metadata.file import ProjectFile, ProjectFileCodec, build_file
from prjman.utils import download_and_write

class URLProjectFile(ProjectFile):
    """A project file for a file at a downloadable url link.
    The file will be obtained via a GET request."""

    def __init__(self, url: str, **kwargs) -> None:
        """
        Parameters
        ----------
        url : str
            The downloadable link for the file.
        """
        super().__init__(**kwargs)
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
    url: str = input('Direct URL: ')
    return build_file(lambda kwargs: URLProjectFile(url, **kwargs))

class URLProjectFileCodec(ProjectFileCodec[URLProjectFile]):
    """A codec for encoding and decoding an URLProjectFile.
    """

    def encode_type(self, obj: URLProjectFile, dict_obj: DictObject) -> DictObject:
        dict_obj['url'] = obj.url
        return dict_obj

    def decode_type(self, obj: DictObject, **kwargs: DictObject) -> URLProjectFile:
        return URLProjectFile(obj['url'], **kwargs)

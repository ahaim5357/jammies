"""A script obtaining a project file from a download url.
"""

from jammies.struct.codec import DictObject
from jammies.defn.file import ProjectFile, ProjectFileCodec
from jammies.defn.builder import build_file
from jammies.utils import download_and_write
from jammies.registrar import JammiesRegistrar

def setup(registrar: JammiesRegistrar) -> None:
    """A setup method used to register components to the project.
    
    Parameters
    ----------
    registrar : `JammiesRegistrar`
        The registrar used to register the components for the project.
    """

    # Create codec
    codec: URLProjectFileCodec = URLProjectFileCodec(registrar)

    registrar.register_file_handler(_REGISTRY_NAME, codec, build_url)

_REGISTRY_NAME: str = 'url'
"""The registry name of the project file handler."""

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

    def registry_name(self) -> str:
        return _REGISTRY_NAME

    def setup(self, root_dir: str) -> bool:
        super().setup(root_dir)
        return download_and_write(self.url, unzip_file = False,
            out_dir = self._create_path(root_dir))

def build_url(registrar: JammiesRegistrar) -> URLProjectFile:
    """Builds an URLProjectFile from user input.
    
    Parameters
    ----------
    registrar : `JammiesRegistrar`
        The registrar used to register the components for the project.

    Returns
    -------
    URLProjectFile
        The built project file.
    """
    url: str = input('Direct URL: ')
    return build_file(registrar, _REGISTRY_NAME, lambda kwargs: URLProjectFile(url, **kwargs))

class URLProjectFileCodec(ProjectFileCodec[URLProjectFile]):
    """A codec for encoding and decoding an URLProjectFile.
    """

    def encode_type(self, obj: URLProjectFile, dict_obj: DictObject) -> DictObject:
        dict_obj['url'] = obj.url
        return dict_obj

    def decode_type(self, obj: DictObject, **kwargs: DictObject) -> URLProjectFile:
        kwargs['codec'] = self # Set codec
        return URLProjectFile(obj['url'], **kwargs)

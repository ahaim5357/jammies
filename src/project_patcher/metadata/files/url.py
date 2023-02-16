import os
from project_patcher.struct.codec import DictObject
from project_patcher.metadata.file import ProjectFile, ProjectFileCodec

class URLProjectFile(ProjectFile):
    """A project file for a file at a downloadable url link. The file will be obtained via a GET request."""

    def __init__(self, url: str, dir: str = os.curdir) -> None:
        """
        Parameters
        ----------
        url : str
            The downloadable link for the file.
        dir : str (default '.')
            The directory the project file is located.
        """
        super().__init__(dir)
        self.url: str = url
    
    def codec(self) -> 'ProjectFileCodec':
        # Lazily load singletons
        from project_patcher.singleton import URL_FILE_CODEC
        return URL_FILE_CODEC

class URLProjectFileCodec(ProjectFileCodec[URLProjectFile]):
    """A codec for encoding and decoding an URLProjectFile.
    """

    def encode_type(self, obj: URLProjectFile, dict_obj: DictObject) -> DictObject:
        dict_obj['url'] = obj.url
        return dict_obj

    def decode_type(self, dir: str, obj: DictObject) -> URLProjectFile:
        return URLProjectFile(obj['url'], dir=dir)

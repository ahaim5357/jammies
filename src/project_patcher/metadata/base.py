"""A script containing information about handling the project metadata.
"""

from typing import List
from project_patcher.lazy import SINGLETON
from project_patcher.metadata.file import ProjectFile
from project_patcher.struct.codec import DictCodec, DictObject

class ProjectMetadata:
    """Metadata information associated with the project being patched or ran."""

    def __init__(self, files: List[ProjectFile]) -> None:
        """
        Parameters
        ----------
        files : list of `ProjectFile`s
            The files associated with the project. 
        """
        self.files: List[ProjectFile] = files

    def setup(self, root_dir: str) -> bool:
        """Sets up the project for usage.

        Parameters
        ----------
        root_dir : str
            The root directory to set up the project in.
        """
        failed: List[ProjectFile] = []

        for file in self.files: # type: ProjectFile
            if not file.setup(root_dir):
                failed.append(file)

        return not failed

    def codec(self) -> 'ProjectMetadataCodec':
        """Returns the codec used to encode and decode this metadata.

        Returns
        -------
        ProjectFileCodec
            The codec used to encode and decode this metadata.
        """
        return SINGLETON.METADATA_CODEC

def build_metadata() -> ProjectMetadata:
    """Builds a ProjectMetadata from user input.
    
    Returns
    -------
    ProjectMetadata
        The built project metadata.
    """
    available_file_types: str = ', '.join(SINGLETON.PROJECT_FILE_BUILDERS.keys())
    files: List[ProjectFile] = []
    get_file: bool = True
    while get_file:
        file_type: str = input(f"Add file ({available_file_types}): ").lower()
        files.append(SINGLETON.PROJECT_FILE_BUILDERS[file_type]())
        get_file = input('Would you like to add another file? ').lower()[0] != 'n'
    return ProjectMetadata(files)

class ProjectMetadataCodec(DictCodec[ProjectMetadata]):
    """A codec for encoding and decoding a ProjectMetadata.
    """

    def encode(self, obj: ProjectMetadata) -> DictObject:
        dict_obj: DictObject = {}
        dict_obj['files'] = list(map(lambda file: file.codec().encode(file), obj.files))
        return dict_obj

    def __decode_file(self, file: DictObject) -> ProjectFile:
        """Decodes a project file from its type.

        Parameters
        ----------
        file : Dict[str, Any]
            The encoded project file.
        
        Returns
        -------
        `ProjectFile`
            The decoded project file.
        """
        return SINGLETON.PROJECT_FILE_TYPES[file['type']].decode(file)

    def decode(self, obj: DictObject) -> ProjectMetadata:
        return ProjectMetadata(list(map(self.__decode_file, obj['files'])))

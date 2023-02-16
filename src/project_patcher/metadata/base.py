from typing import List
from project_patcher.metadata.file import ProjectFile
import project_patcher.struct.codec as ppc

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

class ProjectMetadataCodec(ppc.DictCodec[ProjectMetadata]):
    """A codec for encoding and decoding a ProjectMetadata.
    """
    
    def encode(self, obj: ProjectMetadata) -> ppc.DictObject:
        dict_obj: ppc.DictObject = {}
        dict_obj['files'] = list(map(lambda file: file.codec().encode(file), obj.files))
        return dict_obj
    
    def decode(self, obj: ppc.DictObject) -> ProjectMetadata:
        # Lazily load registry
        from project_patcher.singleton import _PROJECT_FILE_TYPES

        return ProjectMetadata(list(map(lambda file: _PROJECT_FILE_TYPES[file['type']].decode(file), obj['files'])))

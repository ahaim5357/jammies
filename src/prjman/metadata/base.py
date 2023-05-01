"""A script containing information about handling the project metadata.
"""

import os
from typing import List, Optional, Tuple, Set
from pathlib import Path
import fnmatch
from prjman.lazy import SINGLETON
from prjman.metadata.file import ProjectFile
from prjman.struct.codec import DictCodec, DictObject
from prjman.utils import get_or_default

class ProjectMetadata:
    """Metadata information associated with the project being patched or ran."""

    def __init__(self, files: List[ProjectFile],
            ignore: Optional[List[str]] = None, overwrite: Optional[List[str]] = None,
            extra: Optional[DictObject] = None) -> None:
        """
        Parameters
        ----------
        files : list of `ProjectFile`s
            The files associated with the project.
        ignore : list of str
            The patterns for files that are ignored for patching.
        overwrite: list of str
            The patterns for files that are overwritten instead of patching.
        extra : dict[str, Any]
            Extra data defined by the user.
        """
        self.files: List[ProjectFile] = files
        self.ignore: List[str] = [] if ignore is None else ignore
        self.overwrite: List[str] = [] if overwrite is None else overwrite
        self.extra: DictObject = {} if extra is None else extra

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

    def ignore_and_overwrite(self, root_dir: str) -> Tuple[Set[str], Set[str]]:
        """Gets the ignored and overwritten files from the specified directory.

        Parameters
        ----------
        root_dir : str
            The root directory to get the files of.
        
        Returns
        -------
        (set of strs, set of strs)
            A tuple of ignored and overwritten files, respectively.
        """

        # Get all files
        files: list[str] = [Path(os.path.relpath(path, root_dir)).as_posix() \
            for path in Path(root_dir).rglob('*') if path.is_file()]

        # Get ignored files
        ignored_files: Set[str] = set()
        for ignore in self.ignore: # type: str
            ignored_files.update(fnmatch.filter(files, ignore))

        # Get overwritten files
        overwritten_files: Set[str] = set()
        for overwrite in self.overwrite: # type: str
            overwritten_files.update(fnmatch.filter(files, overwrite))

        return (ignored_files, overwritten_files)

def build_metadata() -> ProjectMetadata:
    """Builds a ProjectMetadata from user input.
    
    Returns
    -------
    ProjectMetadata
        The built project metadata.
    """

    # Project Files
    available_file_types: str = ', '.join(SINGLETON.PROJECT_FILE_BUILDERS.keys())
    files: List[ProjectFile] = []
    flag: bool = True
    while flag:
        file_type: str = input(f"Add file ({available_file_types}): ").lower()
        files.append(SINGLETON.PROJECT_FILE_BUILDERS[file_type]())
        flag = input('Would you like to add another file (y/n)? ').lower()[0] != 'n'

    # Ignore Patterns
    flag = input('Would you like to ignore any files when patching (y/n)? ').lower()[0] != 'n'
    ignore: List[str] = []
    while flag:
        ignore.append(input('Add pattern to ignore: '))
        flag = input('Would you like to ignore another pattern (y/n)? ').lower()[0] != 'n'

    # Overwrite Patterns
    flag = input('Would you like to overwrite any files when patching (y/n)? ').lower()[0] != 'n'
    overwrite: List[str] = []
    while flag:
        overwrite.append(input('Add pattern to overwrite: '))
        flag = input('Would you like to overwrite another pattern (y/n)? ').lower()[0] != 'n'

    # Create metadata
    return ProjectMetadata(files, ignore = ignore, overwrite = overwrite)

class ProjectMetadataCodec(DictCodec[ProjectMetadata]):
    """A codec for encoding and decoding a ProjectMetadata.
    """

    def encode(self, obj: ProjectMetadata) -> DictObject:
        dict_obj: DictObject = {}
        dict_obj['files'] = list(map(lambda file: file.codec().encode(file), obj.files))
        if obj.ignore:
            dict_obj['ignore'] = obj.ignore
        if obj.overwrite:
            dict_obj['overwrite'] = obj.overwrite
        if obj.extra:
            dict_obj['extra'] = obj.extra
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
        return ProjectMetadata(list(map(self.__decode_file, obj['files'])),
            ignore = get_or_default(obj, 'ignore', ProjectMetadata),
            overwrite = get_or_default(obj, 'overwrite', ProjectMetadata),
            extra = get_or_default(obj, 'extra', ProjectMetadata))

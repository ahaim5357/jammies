"""A script containing information about handling the project metadata.
"""

import os
from typing import List, Tuple, Set, Dict, Callable
from pathlib import Path
import shutil
import fnmatch
from jammies.log import Logger
from jammies.registrar import JammiesRegistrar
from jammies.defn.file import ProjectFile
from jammies.struct.codec import DictCodec, DictObject
from jammies.utils import get_or_default, input_yn_default
from jammies.config import JammiesConfig

_DEFAULT_LOCATIONS: Dict[str, str] = {
    'clean': 'clean',
    'src': 'src',
    'patches': 'patches',
    'out': 'out'
}
"""The default locations used by the project metadata."""

class ProjectMetadata:
    """Metadata information associated with the project being patched or ran."""

    def __init__(self, files: List[ProjectFile],
            ignore: List[str] | None = None, overwrite: List[str] | None = None,
            location: DictObject | None = None, extra: DictObject | None = None) -> None:
        """
        Parameters
        ----------
        files : list of `ProjectFile`s
            The files associated with the project.
        ignore : list of str (default '[]')
            The patterns for files that are ignored for patching.
        overwrite : list of str (default '[]')
            The patterns for files that are overwritten instead of patching.
        location : dict[str, str] | None (default 'None')
            A alias map for directories used by this project.
        extra : dict[str, Any] (default '{}')
            Extra data defined by the user.
        """
        self.files: List[ProjectFile] = files
        self.ignore: List[str] = [] if ignore is None else ignore
        self.overwrite: List[str] = [] if overwrite is None else overwrite
        self.location: Dict[str, str] = {} if location is None else location
        # Add Missing Defaults
        for key, value in _DEFAULT_LOCATIONS.items():
            if key not in self.location:
                self.location[key] = value
        self.extra: DictObject = {} if extra is None else extra

    def __copy_and_log(self, src: str, dst: str, config: JammiesConfig) -> object:
        """Copies and logs a generated file.

        Parameters
        ----------
        src : str
            The source location of the file.
        dst : str
            The destination of the file.
        config : `JammiesConfig`
            The configuration settings.
        """

        output: object = shutil.copy2(src, dst)
        config.internal.add_generated_file(dst)
        return output

    def setup(self, root_dir: str, logger: Logger, config: JammiesConfig | None = None) -> bool:
        """Sets up the project for usage.

        Parameters
        ----------
        root_dir : str
            The root directory to set up the project in.
        logger : `Logger`
            A logger for reporting on information.
        config : JammiesConfig | None (default 'None')
            The configuration settings.
        """

        # Display warning message if no config is present or the warning message is enabled
        if (not config) or config.project.display_warning_message:
            if not input_yn_default('You are about to download project files from third parties. '
                + 'jammies and its maintainers are not liable for anything that happens '
                + 'as a result of downloading or using these files. Would you still like to '
                + 'download these files?', True):
                return False
            # Ask to disable warning message if config is present
            if config:
                def _disable_warning_message(conf: JammiesConfig) -> None:
                    """Disables the warning message within the config.
                    
                    Parameters
                    ----------
                    config : JammiesConfig
                        The configuration settings.
                    """
                    conf.project.display_warning_message = False

                config.update_and_write(_disable_warning_message,
                    save = input_yn_default(
                        'Would you like to hide this warning message from now on?',
                        False
                    )
                )

        # Clear generated files
        if config:
            config.internal.clear_generated_files()

        failed: List[ProjectFile] = []
        tmp_root: str = os.sep.join([root_dir, '.tmp'])

        for file in self.files: # type: ProjectFile
            # Setup file
            if not file.setup(tmp_root):
                logger.error(f'Failed to setup {file.registry_name()}')
                failed.append(file)
                shutil.rmtree(tmp_root)
                continue

            # Apply post processor
            if file.post_processor and not file.post_processor[0](logger, tmp_root):
                pp_name: str = file.post_processor[1]['type']
                logger.error(f'Failed to apply post processor {pp_name} to {file.registry_name()}')
                failed.append(file)
                shutil.rmtree(tmp_root)
                continue

            shutil.copytree(tmp_root, root_dir,
                copy_function=lambda src, dst: self.__copy_and_log(src, dst, config) \
                    if config else shutil.copy2,
                dirs_exist_ok=True
            )
            shutil.rmtree(tmp_root)

        # Write generated files
        if config:
            config.update_and_write(lambda config: None, save = True)

        # Verify no files failed at any point
        return not failed

    def codec(self) -> 'ProjectMetadataCodec':
        """Returns the codec used to encode and decode this metadata.

        Returns
        -------
        ProjectFileCodec
            The codec used to encode and decode this metadata.
        """
        return METADATA_CODEC

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
    available_file_types: str = ', '.join(METADATA_CODEC.registrar.get_available_builders())
    files: List[ProjectFile] = []
    flag: bool = True
    while flag:
        file_type: str = input(f'Add file ({available_file_types}): ').lower()
        files.append(
            METADATA_CODEC.registrar.get_project_file_builder(file_type)(METADATA_CODEC.registrar)
        )
        flag = input_yn_default('Would you like to add another file', True)

    # Ignore Patterns
    flag = input_yn_default('Would you like to ignore any files when patching', False)
    ignore: List[str] = []
    while flag:
        ignore.append(input('Add pattern to ignore: '))
        flag = input_yn_default('Would you like to ignore another pattern', True)

    # Overwrite Patterns
    flag = input_yn_default('Would you like to overwrite any files when patching', False)
    overwrite: List[str] = []
    while flag:
        overwrite.append(input('Add pattern to overwrite: '))
        flag = input_yn_default('Would you like to overwrite another pattern', True)

    # Create metadata
    return ProjectMetadata(files, ignore = ignore, overwrite = overwrite)

class ProjectMetadataCodec(DictCodec[ProjectMetadata]):
    """A codec for encoding and decoding a ProjectMetadata.
    """

    def __init__(self) -> None:
        """
        Parameters
        ----------
        registrar : `JammiesRegistrar`
            The registrar used to register the components for the project.
        """
        self.registrar: JammiesRegistrar = None

    def encode(self, obj: ProjectMetadata) -> DictObject:
        dict_obj: DictObject = {}
        dict_obj['files'] = list(map(lambda file: file.codec().encode(file), obj.files))
        if obj.ignore:
            dict_obj['ignore'] = obj.ignore
        if obj.overwrite:
            dict_obj['overwrite'] = obj.overwrite

        location: DictObject = {}
        for key, value in obj.location.items():
            # If the key does not have a default or is not the default value
            if key not in _DEFAULT_LOCATIONS or _DEFAULT_LOCATIONS[key] != value:
                location[key] = value
        if location:
            dict_obj['location'] = location

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
        return self.registrar.get_project_file_codec(file['type']).decode(file)

    def decode(self, obj: DictObject) -> ProjectMetadata:
        return ProjectMetadata(list(map(self.__decode_file, obj['files'])),
            ignore = get_or_default(obj, 'ignore', ProjectMetadata),
            overwrite = get_or_default(obj, 'overwrite', ProjectMetadata),
            location = get_or_default(obj, 'location', ProjectMetadata),
            extra = get_or_default(obj, 'extra', ProjectMetadata))

METADATA_CODEC: ProjectMetadataCodec = ProjectMetadataCodec()
"""The codec for :class:`jammies.metadata.base.ProjectMetadata`."""

"""TODO: Document"""

from typing import Dict
from project_patcher.struct.registry import Registry
from project_patcher.metadata.file import ProjectFileCodec
from project_patcher.metadata.base import ProjectMetadataCodec
from project_patcher.utils import has_module

# Add registries

_PROJECT_FILE_TYPES: Registry['ProjectFileCodec'] = Registry()
"""A registry containing the codecs for :class:`project_patcher.metadata.file.ProjectFileCodec`s."""

_OPTIONAL_DEPENDENCIES: Dict[str, bool] = {}
"""A registry containing the loaded optional dependencies."""

# Register optional dependencies

_OPTIONAL_DEPENDENCIES['requests'] = has_module('requests')
_OPTIONAL_DEPENDENCIES['git'] = has_module('git')

# Register Codecs

if _OPTIONAL_DEPENDENCIES['requests']:
    from project_patcher.metadata.files.osf import OSFProjectFileCodec

    OSF_FILE_CODEC: OSFProjectFileCodec = OSFProjectFileCodec()
    """The codec for :class:`project_patcher.metadata.files.osf.OSFProjectFile`s."""

    _PROJECT_FILE_TYPES['osf'] = OSF_FILE_CODEC

    from project_patcher.metadata.files.url import URLProjectFileCodec

    URL_FILE_CODEC: URLProjectFileCodec = URLProjectFileCodec()
    """The codec for :class:`project_patcher.metadata.files.url.URLProjectFile`s."""

    _PROJECT_FILE_TYPES['url'] = URL_FILE_CODEC

if _OPTIONAL_DEPENDENCIES['git']:
    from project_patcher.metadata.files.git import GitProjectFileCodec

    GIT_FILE_CODEC: GitProjectFileCodec = GitProjectFileCodec()
    """The codec for :class:`project_patcher.metadata.files.git.GitProjectFile`s."""

    _PROJECT_FILE_TYPES['git'] = GIT_FILE_CODEC

METADATA_CODEC: 'ProjectMetadataCodec' = ProjectMetadataCodec()
"""The codec for :class:`project_patcher.metadata.base.ProjectMetadata`."""

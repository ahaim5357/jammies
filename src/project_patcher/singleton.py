"""A script dedicated to setting up any registries or singleton
objects used within this package.
"""

from typing import Dict
from project_patcher.struct.registry import Registry
from project_patcher.metadata.file import ProjectFileCodec
from project_patcher.metadata.base import ProjectMetadataCodec
from project_patcher.utils import has_module

# Add registries

PROJECT_FILE_TYPES: Registry['ProjectFileCodec'] = Registry()
"""A registry containing the codecs for :class:`project_patcher.metadata.file.ProjectFileCodec`s."""

OPTIONAL_DEPENDENCIES: Dict[str, bool] = {}
"""A registry containing the loaded optional dependencies."""

# Register optional dependencies

# TODO: Might want to make requests actual dependency
OPTIONAL_DEPENDENCIES['requests'] = has_module('requests')
OPTIONAL_DEPENDENCIES['git'] = has_module('git')

# Register Codecs

if OPTIONAL_DEPENDENCIES['requests']:
    from project_patcher.metadata.files.osf import OSFProjectFileCodec

    OSF_FILE_CODEC: OSFProjectFileCodec = OSFProjectFileCodec()
    """The codec for :class:`project_patcher.metadata.files.osf.OSFProjectFile`s."""

    PROJECT_FILE_TYPES['osf'] = OSF_FILE_CODEC

    from project_patcher.metadata.files.url import URLProjectFileCodec

    URL_FILE_CODEC: URLProjectFileCodec = URLProjectFileCodec()
    """The codec for :class:`project_patcher.metadata.files.url.URLProjectFile`s."""

    PROJECT_FILE_TYPES['url'] = URL_FILE_CODEC

if OPTIONAL_DEPENDENCIES['git']:
    from project_patcher.metadata.files.gitrepo import GitProjectFileCodec

    GIT_FILE_CODEC: GitProjectFileCodec = GitProjectFileCodec()
    """The codec for :class:`project_patcher.metadata.files.git.GitProjectFile`s."""

    PROJECT_FILE_TYPES['git'] = GIT_FILE_CODEC

METADATA_CODEC: 'ProjectMetadataCodec' = ProjectMetadataCodec()
"""The codec for :class:`project_patcher.metadata.base.ProjectMetadata`."""

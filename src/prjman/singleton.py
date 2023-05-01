"""A script dedicated to setting up any registries or singleton
objects used within this package.
"""

from typing import Set, Callable
from prjman.struct.registry import Registry
from prjman.metadata.file import ProjectFileCodec, ProjectFile
from prjman.metadata.base import ProjectMetadataCodec, ProjectMetadata, build_metadata
from prjman.utils import has_module
from prjman.metadata.files.osf import OSFProjectFileCodec, build_osf
from prjman.metadata.files.url import URLProjectFileCodec, build_url

# Add registries

PROJECT_FILE_TYPES: Registry['ProjectFileCodec'] = Registry()
"""A registry containing the codecs for :class:`prjman.metadata.file.ProjectFileCodec`s."""

PROJECT_FILE_BUILDERS: Registry[Callable[[], ProjectFile]] = Registry()
"""A registry containing the builders for :class:`prjman.metadata.file.ProjectFile`s."""

OPTIONAL_DEPENDENCIES: Set[str] = set()
"""A set containing the loaded optional dependencies."""

# Register optional dependencies

if has_module('git'):
    OPTIONAL_DEPENDENCIES.add('git')

# Register Codecs

OSF_FILE_CODEC: OSFProjectFileCodec = OSFProjectFileCodec()
"""The codec for :class:`prjman.metadata.files.osf.OSFProjectFile`s."""
PROJECT_FILE_TYPES['osf'] = OSF_FILE_CODEC
PROJECT_FILE_BUILDERS['osf'] = build_osf

URL_FILE_CODEC: URLProjectFileCodec = URLProjectFileCodec()
"""The codec for :class:`prjman.metadata.files.url.URLProjectFile`s."""
PROJECT_FILE_TYPES['url'] = URL_FILE_CODEC
PROJECT_FILE_BUILDERS['url'] = build_url

if 'git' in OPTIONAL_DEPENDENCIES:
    from prjman.metadata.files.gitrepo import GitProjectFileCodec, build_git

    GIT_FILE_CODEC: GitProjectFileCodec = GitProjectFileCodec()
    """The codec for :class:`prjman.metadata.files.git.GitProjectFile`s."""

    PROJECT_FILE_TYPES['git'] = GIT_FILE_CODEC
    PROJECT_FILE_BUILDERS['git'] = build_git

METADATA_CODEC: 'ProjectMetadataCodec' = ProjectMetadataCodec()
"""The codec for :class:`prjman.metadata.base.ProjectMetadata`."""
METADATA_BUILDER: Callable[[], ProjectMetadata] = build_metadata
"""The builder for a :class:`prjman.metadata.base.ProjectMetadata`."""

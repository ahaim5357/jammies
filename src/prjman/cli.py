"""A script containing the methods needed for command line integration.
"""

import click
import prjman.workspace.project as wspc
from prjman.metadata.base import ProjectMetadata

@click.group()
def main() -> None:
    """A command line interface to construct,
    manage, and patch projects.
    """

@main.group()
def patch() -> None:
    """Helpers to patch an existing project.
    """

@patch.command(name = 'init')
@click.option(
    '--import_metadata', '-I',
    type = str,
    default = None,
    help = 'A path or URL to the metadata JSON.'
)
@click.option(
    '-a', '-A', 'include_hidden',
    is_flag = True,
    help = 'When added, copies hidden files to the working directory.'
)
def init(import_metadata: str | None = None, include_hidden: bool = False) -> None:
    """Initializes a new project or an existing project from the
    metadata JSON in the executing directory, an import, or from
    the metadata builder if neither are present.
    """

    # Get metadata
    metadata: ProjectMetadata = wspc.read_metadata(import_loc = import_metadata)

    # Setup workspace
    wspc.setup_clean(metadata)
    wspc.setup_working(include_hidden = include_hidden)

    print('Initialized patching environment!')

@patch.command(name = 'output')
def output() -> None:
    """Generates any patches and clones the new files to an output
    directory."""

    # Get metadata
    metadata: ProjectMetadata = wspc.read_metadata()

    # Output working and generate patches
    wspc.output_working(metadata)

    print('Generated patches and output files!')

@patch.command(name = 'clean')
@click.option(
    '--import_metadata', '-I',
    type = str,
    default = None,
    help = 'A path or URL to the metadata JSON.'
)
def clean(import_metadata: str | None = None) -> None:
    """Initializes a clean workspace from the
    metadata JSON in the executing directory, an import, or from
    the metadata builder if neither are present.
    """

    # Get metadata
    metadata: ProjectMetadata = wspc.read_metadata(import_loc = import_metadata)

    # Setup workspace
    wspc.setup_clean(metadata)

    print('Setup clean workspace!')

@patch.command(name = 'src')
@click.option(
    '--import_metadata', '-I',
    type = str,
    default = None,
    help = 'A path or URL to the metadata JSON.'
)
def source(import_metadata: str | None = None) -> None:
    """Initializes a patched workspace from the
    metadata JSON in the executing directory, an import, or from
    the metadata builder if neither are present.
    """

    # Get metadata
    metadata: ProjectMetadata = wspc.read_metadata(import_loc = import_metadata)

    # Setup workspace
    wspc.setup_clean(metadata, '_src', invalidate_cache = True)
    wspc.setup_working_raw()

    print('Setup patched workspace!')

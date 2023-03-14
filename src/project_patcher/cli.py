"""A script containing the methods needed for command line integration.
"""

from typing import Optional
import click
import project_patcher.workspace.project as wspc
from project_patcher.metadata.base import ProjectMetadata

@click.group()
def main() -> None:
    """A command line interface to construct projects,
    generated diffs, and patch multiple files in one
    implementation.
    """

@main.command(name = 'init')
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
def init(import_metadata: Optional[str] = None, include_hidden: bool = False) -> None:
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

@main.command(name = 'output')
def output() -> None:
    """Generates any patches and clones the new files to an output
    directory."""

    # Get metadata
    metadata: ProjectMetadata = wspc.read_metadata()

    # Output working and generate patches
    wspc.output_working(metadata)

    print('Generated patches and output files!')

@main.command(name = 'clean')
@click.option(
    '--import_metadata', '-I',
    type = str,
    default = None,
    help = 'A path or URL to the metadata JSON.'
)
def clean(import_metadata: Optional[str] = None) -> None:
    """Initializes a clean workspace from the
    metadata JSON in the executing directory, an import, or from
    the metadata builder if neither are present.
    """

    # Get metadata
    metadata: ProjectMetadata = wspc.read_metadata(import_loc = import_metadata)

    # Setup workspace
    wspc.setup_clean(metadata)

    print('Setup clean workspace!')

@main.command(name = 'src')
@click.option(
    '--import_metadata', '-I',
    type = str,
    default = None,
    help = 'A path or URL to the metadata JSON.'
)
def source(import_metadata: Optional[str] = None) -> None:
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

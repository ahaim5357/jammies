"""TODO: Document"""

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

# TODO: Create clean workspace
# TODO: Generate working directory
# TODO: Generate patches
# TODO: Push to output directory

@main.command(name = 'init')
@click.option(
    '--import_metadata', '-I',
    type = str,
    default = None,
    help = "A path or URL to the metadata JSON."
)
def init(import_metadata: Optional[str] = None) -> None:
    """Initializes a new project or an existing project from the
    metadata JSON in the executing directory, an import, or from
    the metadata builder if neither are present.
    """

    # Get metadata
    metadata: ProjectMetadata = wspc.read_metadata(import_loc = import_metadata)

    # Setup workspace
    wspc.setup_clean(metadata)
    wspc.setup_working()

    print('Success!')

@main.command(name = 'output')
def output() -> None:
    """Generates any patches and clones the new files to an output
    directory."""

    # Output working and generate patches
    wspc.output_working()

    print('Success!')

"""A script containing the methods needed for command line integration.
"""

import click
import prjman.workspace.project as wspc
from prjman.metadata.base import ProjectMetadata
from prjman.config import PrjmanConfig, load_config

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

    # Read config
    config: PrjmanConfig = load_config()

    # Get metadata
    metadata: ProjectMetadata = wspc.read_metadata(dirpath = config.dirpath,
        import_loc = import_metadata)
    clean_dir = metadata.location['clean']
    working_dir = metadata.location['src']
    patch_dir = metadata.location['patches']
    out_dir = metadata.location['out']

    # Setup workspace
    if wspc.setup_clean(metadata, config = config, clean_dir = clean_dir):
        wspc.setup_working(clean_dir = clean_dir, working_dir = working_dir,
            patch_dir = patch_dir, out_dir = out_dir, include_hidden = include_hidden)
        print('Initialized patching environment!')
    else:
        print('Could not generate clean workspace.')

@patch.command(name = 'output')
def output() -> None:
    """Generates any patches and clones the new files to an output
    directory."""

    # Read config
    config: PrjmanConfig = load_config()

    # Get metadata
    metadata: ProjectMetadata = wspc.read_metadata(dirpath = config.dirpath)
    clean_dir = metadata.location['clean']
    working_dir = metadata.location['src']
    patch_dir = metadata.location['patches']
    out_dir = metadata.location['out']

    # Output working and generate patches
    wspc.output_working(metadata, clean_dir = clean_dir, working_dir = working_dir,
        patch_dir = patch_dir, out_dir = out_dir)

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

    # Read config
    config: PrjmanConfig = load_config()

    # Get metadata
    metadata: ProjectMetadata = wspc.read_metadata(dirpath = config.dirpath,
        import_loc = import_metadata)
    clean_dir = metadata.location['clean']

    # Setup workspace
    if wspc.setup_clean(metadata, config = config, clean_dir = clean_dir):
        print('Setup clean workspace!')
    else:
        print('Could not generate clean workspace.')

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

    # Read config
    config: PrjmanConfig = load_config()

    # Get metadata
    metadata: ProjectMetadata = wspc.read_metadata(dirpath = config.dirpath,
        import_loc = import_metadata)
    working_dir = metadata.location['src']
    patch_dir = metadata.location['patches']
    out_dir = metadata.location['out']

    # Setup workspace
    if wspc.setup_clean(metadata, config = config, clean_dir = working_dir,
            invalidate_cache = True):
        wspc.setup_working_raw(working_dir = working_dir,
            patch_dir = patch_dir, out_dir = out_dir)
        print('Setup patched workspace!')
    else:
        print('Could not generate clean workspace.')

"""A script containing the methods needed for command line integration.
"""

import os
from typing import List
import click
from tomlkit import load as load_toml
import jammies.workspace.project as wspc
from jammies.defn.registrar import setup as setup_registrar
from jammies.defn.metadata import ProjectMetadata
from jammies.config import JammiesConfig, load_config, config_loc as cloc
from jammies.log import Logger

# TODO: REDO

@click.group()
def main() -> None:
    """A command line interface to construct,
    manage, and patch projects.
    """

@main.group()
def config() -> None:
    """Helpers to generate, read, and write to a config.
    """

def _check_project_config(logger: Logger, dirpath: str) -> bool:
    """Returns whether a project exists in the current location.
    
    Parameters
    ----------
    logger : Logger
        A logger for reporting on information.
    dirpath : str
        The current directory to check the path for.
    
    Returns
    -------
    bool
        `True`, if a project exists in the current location.
    """
    # If project doesn't exist, throw an error
    if not os.path.exists(
        prj_path := os.sep.join([dirpath, wspc.PROJECT_METADATA_NAME])
    ):
        logger.error(
            f'No project exists at \'{prj_path}\'. ' \
            + 'Create a project using one of the following commands:',
            '-> jammies project init',
            '-> jammies patch   init',
            sep = '\n'
        )
        return False
    
    return True

@config.command(name = 'create')
@click.option('--project', '-p', is_flag = True,
    help = 'Generates a config for the current project.')
@click.option('--site', '-s', is_flag = True,
    help = 'Generates a config for the set environment variable, ' \
    + 'virtual environment, or user if neither are specified.')
@click.option('--user', '-u', is_flag = True, help = 'Generates a config for the current user.')
@click.option('--global', '-g', '_global', is_flag = True, help = 'Generates a global config.')
@click.option('--verbose', '-v', is_flag = True, help = 'When \'true\', displays debug messages.')
def config_create(project: bool = False, site: bool = False,
        user: bool = False, _global: bool = False, verbose: bool = False) -> None:
    """Creates a configuration for the specified scope if it doesn't already
    exist. If no scope is specified, a config will be generated for the project
    scope.
    """
    # Create config object to write
    logger: Logger = Logger(verbose = verbose)
    prj_config: JammiesConfig = JammiesConfig()
    setup_registrar(logger, prj_config)

    configs_written: bool = False

    # Check if project is wanted or no config option is specified
    if project or not (project or site or user or _global):
        # If project doesn't exist, throw an error
        if not _check_project_config(logger, prj_config.dirpath):
            return

        # Otherwise check if a config does not already exist
        if os.path.exists(config_path := cloc(dirpath = prj_config.dirpath, scope = 0)):
            logger.skip(f'Config exists within project \'{config_path}\'')
        else:
            logger.debug(f'Creating config at project \'{config_path}\'')
            prj_config.write_config(scope = 0)
            configs_written = True

    # Check if site
    if site:
        # Check if a config does not already exist
        if os.path.exists(config_path := cloc(dirpath = prj_config.dirpath, scope = 1)):
            logger.skip(f'Config exists within site \'{config_path}\'')
        else:
            logger.debug(f'Creating config at site \'{config_path}\'')
            prj_config.write_config(scope = 1)
            configs_written = True

    # Check if user
    if user:
        # Check if a config does not already exist
        if os.path.exists(config_path := cloc(dirpath = prj_config.dirpath, scope = 2)):
            logger.skip(f'Config exists within user \'{config_path}\'')
        else:
            logger.debug(f'Creating config at user \'{config_path}\'')
            prj_config.write_config(scope = 2)
            configs_written = True

    # Check if global
    if _global:
        # Check if a config does not already exist
        if os.path.exists(config_path := cloc(dirpath = prj_config.dirpath, scope = 3)):
            logger.skip(f'Skip: Config exists within global \'{config_path}\'')
        else:
            logger.debug(f'Creating config at global \'{config_path}\'')
            prj_config.write_config(scope = 3)
            configs_written = True

    if configs_written:
        logger.success('Configs have been generated!')
    else:
        logger.skip('Configs are already generated!')

@config.command(name = 'loc')
@click.option('--open', '-o', 'open_dir', is_flag = True,
    help = 'If the config is found, the directory will be opened in the native file system.')
@click.option('--scope', '-s',
    type = click.Choice(['project', 'site', 'user', 'global'],
        case_sensitive = False
    ),
    default = 'project',
    help = 'The configuration to look for. If none is specified, ' \
    + 'it will default to the project config.'
)
def config_loc(open_dir: bool = False, scope: str = 'project') -> None:
    """Returns the location of the config file, if it exists."""

    logger: Logger = Logger()
    scope_val: int = int(scope == 'project') * 0 \
        + int(scope == 'site') * 1 \
        + int(scope == 'user') * 2 \
        + int(scope == 'global') * 3

    # Skip execution if an error is thrown
    if scope_val == 0 and not _check_project_config(logger, os.curdir):
        return

    # Check if the current config path exists
    if os.path.exists(config_path := cloc(scope = scope_val)):
        logger.success(config_path)

        # Open file location if available
        if open_dir:
            os.startfile(os.path.dirname(config_path))
    else:
        logger.error(
            f'No config for {scope}. Create the config using:',
            f'-> jammies config create --{scope}',
            sep = '\n'
        )

@config.command(name = 'list')
def config_list() -> None:
    """Lists all available configuration options."""
    logger: Logger = Logger()
    prj_config: JammiesConfig = JammiesConfig()
    top_message: List[str] = ['Available config options']
    top_message += map(lambda s: f'-> {s}', prj_config.list_vals())
    logger.success(
        *top_message,
        sep = '\n'
    )

@config.command(name = 'value')
@click.argument('name')
@click.argument('value', required = False)
@click.option('--scope', '-s',
    type = click.Choice(['project', 'site', 'user', 'global'],
        case_sensitive = False
    ),
    default = 'project',
    help = 'The configuration to look for. If none is specified, ' \
    + 'it will default to the project config.'
)
def config_value(name: str, value: str | None = None, scope: str = 'project') -> None:
    """Gets the configuration value associated with the name in the
    specified scope. If the value is specified, the name will be updated
    to hold that value.
    """
    logger: Logger = Logger()
    scope_val: int = int(scope == 'project') * 0 \
        + int(scope == 'site') * 1 \
        + int(scope == 'user') * 2 \
        + int(scope == 'global') * 3

    # Skip execution if project doesn't exist
    if scope_val == 0 and not _check_project_config(logger, os.curdir):
        return

    # Otherwise check if config exists
    if not os.path.exists(config_path := cloc(scope = scope_val)):
        logger.error(
            f'No config for {scope}. Create the config using:',
            f'-> jammies config create --{scope}',
            sep = '\n'
        )
        return

    # Load config scope
    prj_config: JammiesConfig = None
    with open(config_path, mode = 'r', encoding = 'UTF-8') as file:
        prj_config = load_toml(file)
        prj_config['dirpath'] = os.curdir
        prj_config = JammiesConfig.decode_toml(prj_config)

    # If a value is present, set it within the config
    if value:
        success, val = prj_config.set_val(name, value)
        if success:
            prj_config.write_config(scope = scope_val)
            logger.success(f'[{scope}] {name}: {val}')
        else:
            logger.error(f'[{scope}] {val}')
    else:
        # Otherwise, read the value
        success, val = prj_config.get_val(name)
        if success:
            logger.success(f'[{scope}] {name} -> {val}')
        else:
            logger.error(f'[{scope}] {val}')

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
    logger: Logger = Logger()
    prj_config: JammiesConfig = load_config()
    setup_registrar(logger, prj_config)

    # Get metadata
    metadata: ProjectMetadata = wspc.read_metadata(dirpath = prj_config.dirpath,
        import_loc = import_metadata)
    clean_dir = metadata.location['clean']
    working_dir = metadata.location['src']
    patch_dir = metadata.location['patches']
    out_dir = metadata.location['out']

    # Setup workspace
    if wspc.setup_clean(metadata, logger, config = prj_config, clean_dir = clean_dir):
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
    logger: Logger = Logger()
    prj_config: JammiesConfig = load_config()
    setup_registrar(logger, prj_config)

    # Get metadata
    metadata: ProjectMetadata = wspc.read_metadata(dirpath = prj_config.dirpath)
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
    logger: Logger = Logger()
    prj_config: JammiesConfig = load_config()
    setup_registrar(logger, prj_config)

    # Get metadata
    metadata: ProjectMetadata = wspc.read_metadata(dirpath = prj_config.dirpath,
        import_loc = import_metadata)
    clean_dir = metadata.location['clean']

    # Setup workspace
    if wspc.setup_clean(metadata, logger, config = prj_config, clean_dir = clean_dir):
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
    logger: Logger = Logger()
    prj_config: JammiesConfig = load_config()
    setup_registrar(logger, prj_config)

    # Get metadata
    metadata: ProjectMetadata = wspc.read_metadata(dirpath = prj_config.dirpath,
        import_loc = import_metadata)
    working_dir = metadata.location['src']
    patch_dir = metadata.location['patches']
    out_dir = metadata.location['out']

    # Setup workspace
    if wspc.setup_clean(metadata, logger, config = prj_config, clean_dir = working_dir,
            invalidate_cache = True):
        wspc.setup_working_raw(working_dir = working_dir,
            patch_dir = patch_dir, out_dir = out_dir)
        print('Setup patched workspace!')
    else:
        print('Could not generate clean workspace.')

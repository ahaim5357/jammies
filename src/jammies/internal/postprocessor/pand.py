"""A script containing the post processor which can execute multiple
and AND together the results.
"""

from jammies.log import Logger
from jammies.registrar import JammiesRegistrar
from jammies.defn.file import PostProcessor

_REGISTRY_NAME: str = 'and'
"""The registry name of the post processor."""

def setup(registrar: JammiesRegistrar) -> None:
    """A setup method used to register components to the project.
    
    Parameters
    ----------
    registrar : `JammiesRegistrar`
        The registrar used to register the components for the project.
    """
    registrar.register_post_processor(
        _REGISTRY_NAME,
        lambda logger, current_dir, **kwargs: post_and(registrar, logger, current_dir, **kwargs)
    )

def post_and(registrar: JammiesRegistrar, logger: Logger, current_dir: str, **kwargs) -> bool:
    """Executes multiple post processors and ANDs the results together.
    
    Parameters
    ----------
    logger : Logger
        A logger for reporting on information.
    current_dir : str
        The current directory to execute the processor within.
    processors : list of objects
        A list of post processors to run on the codebase.
    quick_fail : bool
        When `True`, stops executing post processors after one fails.
    
    Returns
    -------
    bool
        `True` if the operation is successful.
    """

    if len(kwargs['processors']) == 0:
        logger.error('No processors to run.')
        return False

    success: bool = True
    quick_fail: bool = kwargs['quick_fail'] if 'quick_fail' in kwargs else False

    for processor_data in kwargs['processors']:
        # Get post processor
        post_processor: PostProcessor = registrar.get_post_processor(processor_data['type'])
        pp_name: str = processor_data['type']

        # Run checker
        logger.debug(f'Running {pp_name} in ANDed processor')
        if not post_processor(logger, current_dir, **processor_data):
            logger.error(f'Failed to apply post processor \'{pp_name}\' ' \
                + 'in ANDed post processor.')
            success = False

            # Quick fail if enabled
            if quick_fail:
                break

    return success

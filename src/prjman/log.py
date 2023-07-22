"""A script holding logger methods for the module.
"""

from typing import List

def _log(header: str, *args, **kwargs) -> None:
    """A general logger which applies a header
    to the first message. All other parameters
    are the same as `print`.
    
    Parameters
    ----------
    header : str
        The header to prefix to the first message.
    """
    args: List = list(args)
    args[0] = f'{header}: {args[0]}'
    print(*args, **kwargs)

class Logger:
    """A general logger for messages in the module."""

    def __init__(self, verbose: bool = True) -> None:
        """
        Parameters
        ----------
        verbose : bool
            Whether debug messages should be logged.
        """
        self.verbose: bool = verbose

    def skip(self, *args, **kwargs) -> None:
        """Prefixes 'Skip' in front of a message."""
        _log('Skip', *args, **kwargs)

    def error(self, *args, **kwargs) -> bool:
        """Prefixes 'Error' in front of a message."""
        _log('Error', *args, **kwargs)
        return False

    def success(self, *args, **kwargs) -> bool:
        """Prefixes 'Success' in front of a message."""
        _log('Success', *args, **kwargs)
        return True

    def debug(self, *args, **kwargs) -> None:
        """Prefixes 'Debug' in front of a message if
        verbose is enabled."""
        if self.verbose:
            _log('Debug', *args, **kwargs)

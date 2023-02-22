"""A script containing a generic implementation of a registry system.
"""

from typing import TypeVar, Dict, Generic

RegistryObject = TypeVar('RegistryObject')
"""The type of the values in a registry."""

class Registry(Dict[str, RegistryObject], Generic[RegistryObject]):
    """A string key to value bidirectional dictionary.
    
    Types
    -----
    RegistryObject
        The type of the values in the registry.
    """

    def __init__(self) -> None:
        super().__init__()
        self.__inverse: Dict[RegistryObject, str] = {}

    def __setitem__(self, __key: str, __value: RegistryObject) -> None:
        # Make sure the value isn't already assigned to a given key
        if __value in self.__inverse:
            raise ValueError(f'{__value} cannot be assigned to {__key} \
                as it already exists for {self.get_key(__value)}.')

        super().__setitem__(__key, __value)
        self.__inverse[__value] = __key

    def __delitem__(self, __key: str) -> None:
        del self.__inverse[self[__key]]
        super().__delitem__(__key)

    def get_key(self, __value: RegistryObject) -> str:
        """Gets the key from the value.

        Parameters
        ----------
        __value : RegistryObject
            The value to get the key of.

        Return
        ------
        str
            The key of the value.
        """
        return self.__inverse[__value]

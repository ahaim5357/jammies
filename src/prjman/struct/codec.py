"""A script containing a generic implementation of an encoder and decoder
for an object and a dictionary.
"""

from abc import ABC, abstractmethod
from typing import TypeVar, Type, Dict, Any, Generic

DataObject = TypeVar('DataObject')
"""The type of the object holding data."""

DictObject: Type[Dict[str, Any]] = Dict[str, Any]
"""A generic intermediate object for reading or writing to a file."""

class DictCodec(ABC, Generic[DataObject]):
    """An abstract, generic encoder and decoder between a dictionary and a data object.

    Types
    -----
    DataObject
        The type of the data object to be encoded or decoded to.
    """

    @abstractmethod
    def decode(self, obj: DictObject) -> DataObject:
        """Decodes a dictionary to the data object.
        
        Parameters
        ----------
        obj : Dict[str, Any]
            The dictionary containing the data for the object.
        
        Returns
        -------
        DataObject
            The decoded data object.
        """

    @abstractmethod
    def encode(self, obj: DataObject) -> DictObject:
        """Encodes a data object to a dictionary.
        
        Parameters
        ----------
        obj : DataObject
            The object containing the data.
        
        Returns
        -------
        Dict[str, Any]
            The encoded data object in a dictionary.
        """

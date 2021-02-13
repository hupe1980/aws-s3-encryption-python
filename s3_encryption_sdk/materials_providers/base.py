from typing import Dict, Tuple
from abc import ABC, abstractmethod

from ..data_key import DataKey
from ..envelope import Envelope


class MaterialsProvider(ABC):
    """Base class for all cryptographic materials providers."""

    @abstractmethod
    def decryption_materials(self, encryption_context: Dict[str, any]) -> DataKey:
        """Provide decryption materials."""
        pass

    @abstractmethod
    def encryption_materials(self, encryption_context: Dict[str, any]) -> Tuple[DataKey, Envelope]:
        """Provide encryption materials."""
        pass

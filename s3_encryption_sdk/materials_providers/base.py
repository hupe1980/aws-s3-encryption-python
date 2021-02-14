"""Base cryptographic materials provider for all cryptographic materials providers."""

from abc import ABC, abstractmethod

from ..materials import EncryptionMaterials
from .context import EncryptionContext


class MaterialsProvider(ABC):
    """Base class for all cryptographic materials providers."""

    @abstractmethod
    def decryption_materials(self, encryption_context: EncryptionContext) -> EncryptionMaterials:
        """Provide decryption materials."""

    @abstractmethod
    def encryption_materials(self, encryption_context: EncryptionContext) -> EncryptionMaterials:
        """Provide encryption materials."""

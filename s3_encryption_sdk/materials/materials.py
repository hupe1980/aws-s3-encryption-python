from ..keys import DataKey
from .metadata import Metadata


class EncryptionMaterials(object):
    """Encryption materials."""

    def __init__(
        self,
        data_key: DataKey,
        metadata: Metadata,
    ) -> None:
        self._data_key = data_key
        self._metadata = metadata

    @property
    def data_key(self) -> DataKey:
        """Data key for content encrypting."""
        return self._data_key

    @property
    def metadata(self) -> Metadata:
        """Metadata that describes these cryptographic materials."""
        return self._metadata

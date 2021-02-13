from typing import Dict, Tuple

from ..envelope import Envelope
from ..data_key import DataKeyAlgorithms, DataKey
from ..wrapping_key import WrappingKey
from .base import MaterialsProvider


class WrappedMaterialsProvider(MaterialsProvider):
    def __init__(
        self,
        wrapping_key: WrappingKey,
        algorithm: DataKeyAlgorithms = DataKeyAlgorithms.AES_256_GCM_IV12_TAG16,
    ) -> None:
        self._wrapping_key = wrapping_key
        self._algorithm = algorithm

    def decryption_materials(self, encryption_context: Dict[str, any]) -> DataKey:
        """Provide decryption materials."""
        envelope = encryption_context.get("envelope")

        initial_material = self._decrypt_data_key(encryption_context=encryption_context)

        encryption_key = DataKey(
            algorithm=self._algorithm,
            key=initial_material,
            iv=envelope.iv,
        )

        return encryption_key

    def encryption_materials(self, encryption_context: Dict[str, any]) -> Tuple[DataKey, Envelope]:
        """Provide encryption materials."""
        initial_material, encrypted_initial_material = self._generate_data_key(encryption_context)
        encryption_material_description = encryption_context.get("material_description", {}).copy()

        iv = self._algorithm.generate_iv()

        envelope = Envelope(
            iv=iv,
            material_description=encryption_material_description,
            key_wrapping_algorithm=self._wrapping_key.algorithm_name,
            content_encryption_algorithm=self._algorithm.name,
            wrapped_data_key=encrypted_initial_material,
            tag_length=self._algorithm.tag_len * 8,
        )

        encryption_key = DataKey(
            algorithm=self._algorithm,
            key=initial_material,
            iv=iv,
        )

        return encryption_key, envelope

    def _decrypt_data_key(self, encryption_context: Dict[str, any]) -> bytes:
        envelope = encryption_context.get("envelope")
        data_key = self._wrapping_key.unwrap_data_key(envelope.wrapped_data_key)

        return data_key

    def _generate_data_key(self, encryption_context: Dict[str, any]) -> Tuple[bytes, bytes]:
        data_key = self._algorithm.generate_data_key()
        wrapped_data_key = self._wrapping_key.wrap_data_key(data_key)

        return data_key, wrapped_data_key

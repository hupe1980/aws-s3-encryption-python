"""Cryptographic materials provider to use wrapped content encryption keys."""
from typing import Tuple

from ..keys import WrappingKey, DataKeyAlgorithms, DataKey
from ..materials import EncryptionMaterials, Metadata
from .base import MaterialsProvider
from .context import EncryptionContext


class WrappedMaterialsProvider(MaterialsProvider):
    """Cryptographic materials provider to use wrapped content encryption keys."""

    def __init__(
        self,
        wrapping_key: WrappingKey,
        algorithm: DataKeyAlgorithms = DataKeyAlgorithms.AES_256_GCM_IV12_TAG16,
    ) -> None:
        self._wrapping_key = wrapping_key
        self._algorithm = algorithm

    def decryption_materials(self, encryption_context: EncryptionContext) -> EncryptionMaterials:
        """Provide decryption materials."""
        metadata = Metadata.from_s3_metatdata(encryption_context.s3_metadata)

        initial_material = self._decrypt_data_key_material(encryption_context=encryption_context)

        data_key = DataKey(
            algorithm=self._algorithm,
            key=initial_material,
            iv=metadata.iv,
        )

        encryption_materials = EncryptionMaterials(data_key=data_key, metadata=metadata)

        return encryption_materials

    def encryption_materials(self, encryption_context: EncryptionContext) -> EncryptionMaterials:
        """Provide encryption materials."""
        initial_material, encrypted_initial_material = self._generate_data_key_material()
        material_description = encryption_context.material_description

        iv = self._algorithm.generate_iv()

        metadata = Metadata(
            iv=iv,
            material_description=material_description,
            key_wrapping_algorithm=self._wrapping_key.algorithm_name,
            content_encryption_algorithm=self._algorithm.name,
            wrapped_data_key=encrypted_initial_material,
            tag_length=self._algorithm.tag_len * 8,
            unencrypted_content_length=encryption_context.unencrypted_content_length,
        )

        data_key = DataKey(
            algorithm=self._algorithm,
            key=initial_material,
            iv=iv,
        )

        encryption_materials = EncryptionMaterials(data_key=data_key, metadata=metadata)

        return encryption_materials

    def _decrypt_data_key_material(self, encryption_context: EncryptionContext) -> bytes:
        """Decrypt an encrypted data key."""
        metadata = Metadata.from_s3_metatdata(encryption_context.s3_metadata)
        initial_material = self._wrapping_key.unwrap_data_key(metadata.wrapped_data_key)

        return initial_material

    def _generate_data_key_material(self) -> Tuple[bytes, bytes]:
        """Generate the data key material"""
        initial_material = self._algorithm.generate_data_key()
        encrypted_initial_material = self._wrapping_key.wrap_data_key(initial_material)

        return initial_material, encrypted_initial_material

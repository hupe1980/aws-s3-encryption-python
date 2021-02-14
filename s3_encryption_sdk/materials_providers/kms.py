"""Cryptographic materials provider for use with the AWS Key Management Service (KMS)."""
from typing import Tuple
import botocore

from ..keys import DataKeyAlgorithms, DataKey
from ..materials import EncryptionMaterials, Metadata
from .base import MaterialsProvider
from .context import EncryptionContext


def _kms_encryption_context(encryption_context: EncryptionContext):
    """Build the KMS encryption context from the encryption context."""
    kms_encryption_context = dict(
        s3_bucket_name=encryption_context.bucket_name,
        s3_object_key=encryption_context.object_key,
    )
    return kms_encryption_context


class KmsMaterialsProvider(MaterialsProvider):
    """Cryptographic materials provider for use with the AWS Key Management Service (KMS)."""

    def __init__(
        self,
        key_id: str,
        client: botocore.client.BaseClient,
        grant_tokens=None,
        algorithm: DataKeyAlgorithms = DataKeyAlgorithms.AES_256_GCM_IV12_TAG16,
    ) -> None:
        self._key_id = key_id
        self._client = client
        self._grant_tokens = grant_tokens
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
        initial_material, encrypted_initial_material = self._generate_data_key_material(encryption_context)
        material_description = encryption_context.material_description

        iv = self._algorithm.generate_iv()

        data_key = DataKey(
            algorithm=self._algorithm,
            key=initial_material,
            iv=iv,
        )

        material_description["aws:x-amz-cek-alg"] = "AES/GCM/NoPadding"

        metadata = Metadata(
            iv=iv,
            material_description=material_description,
            key_wrapping_algorithm="kms",
            content_encryption_algorithm=self._algorithm.name,
            wrapped_data_key=encrypted_initial_material,
            tag_length=self._algorithm.tag_len * 8,
            unencrypted_content_length=encryption_context.unencrypted_content_length,
        )

        encryption_materials = EncryptionMaterials(data_key=data_key, metadata=metadata)

        return encryption_materials

    def _decrypt_data_key_material(self, encryption_context: EncryptionContext) -> bytes:
        """Decrypt an encrypted data key."""
        kms_encryption_context = _kms_encryption_context(encryption_context)
        metadata = Metadata.from_s3_metatdata(encryption_context.s3_metadata)

        encrypted_initial_material = metadata.wrapped_data_key

        kms_params = dict(
            CiphertextBlob=encrypted_initial_material,
            EncryptionContext=kms_encryption_context,
        )

        if self._grant_tokens:
            kms_params["GrantTokens"] = self._grant_tokens

        try:
            response = self._client.decrypt(**kms_params)
            return response["Plaintext"]
        except (botocore.exceptions.ClientError, KeyError):
            message = "Failed to unwrap AWS KMS protected materials"
            raise Exception(message)

    def _generate_data_key_material(self, encryption_context: EncryptionContext) -> Tuple[bytes, bytes]:
        """Generate the data key material"""
        key_id = self._key_id
        key_length = self._algorithm.data_key_length
        kms_params = dict(
            KeyId=key_id,
            NumberOfBytes=key_length,
            EncryptionContext=_kms_encryption_context(encryption_context),
        )

        if self._grant_tokens:
            kms_params["GrantTokens"] = self._grant_tokens

        try:
            response = self._client.generate_data_key(**kms_params)
            return response["Plaintext"], response["CiphertextBlob"]
        except (botocore.exceptions.ClientError, KeyError):
            message = "Failed to generate materials using AWS KMS"
            raise Exception(message)

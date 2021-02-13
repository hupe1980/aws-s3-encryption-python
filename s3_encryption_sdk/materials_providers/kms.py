from typing import Dict, Tuple
import botocore

from ..envelope import Envelope
from ..data_key import DataKeyAlgorithms, DataKey
from .base import MaterialsProvider


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
            key_wrapping_algorithm="kms",
            content_encryption_algorithm=self._algorithm.name,
            wrapped_data_key=encrypted_initial_material,
            tag_length=self._algorithm.tag_len * 8,
        )

        envelope.add_kms_data_key_encryption_algorithm()

        encryption_key = DataKey(
            algorithm=self._algorithm,
            key=initial_material,
            iv=iv,
        )

        return encryption_key, envelope

    def _kms_encryption_context(self, encryption_context: Dict[str, any]):
        """Build the KMS encryption context from the encryption context."""
        kms_encryption_context = {}

        bucket_name = encryption_context.get("bucket_name", None)
        object_key = encryption_context.get("object_key", None)

        if bucket_name is not None:
            kms_encryption_context["s3_bucket_name"] = bucket_name

        if object_key is not None:
            kms_encryption_context["s3_object_key"] = object_key

        return kms_encryption_context

    def _decrypt_data_key(self, encryption_context: Dict[str, any]) -> bytes:
        """Decrypt an encrypted data key."""
        kms_encryption_context = self._kms_encryption_context(encryption_context)
        envelope = encryption_context.get("envelope")

        encrypted_initial_material = envelope.wrapped_data_key

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

    def _generate_data_key(self, encryption_context: Dict[str, any]) -> Tuple[bytes, bytes]:
        """Generate the data key"""
        key_id = self._key_id
        key_length = self._algorithm.data_key_length
        kms_params = dict(
            KeyId=key_id,
            NumberOfBytes=key_length,
            EncryptionContext=self._kms_encryption_context(encryption_context),
        )

        if self._grant_tokens:
            kms_params["GrantTokens"] = self._grant_tokens

        try:
            response = self._client.generate_data_key(**kms_params)
            return response["Plaintext"], response["CiphertextBlob"]
        except (botocore.exceptions.ClientError, KeyError):
            message = "Failed to generate materials using AWS KMS"
            raise Exception(message)

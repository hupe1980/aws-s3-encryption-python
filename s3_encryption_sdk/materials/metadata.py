import base64
import json
from typing import Dict, Optional


class Metadata(object):
    """Encryption material metadata"""

    def __init__(
        self,
        wrapped_data_key: bytes,
        iv: bytes,
        material_description: Optional[Dict[str, str]] = None,
        key_wrapping_algorithm: Optional[str] = None,
        content_encryption_algorithm: str = "AES/GCM/NoPadding",
        tag_length: int = 128,
        unencrypted_content_length: Optional[int] = None,
    ) -> None:
        self._wrapped_data_key = wrapped_data_key
        self._iv = iv
        self._material_description = material_description
        self._key_wrapping_algorithm = key_wrapping_algorithm
        self._content_encryption_algorithm = content_encryption_algorithm
        self._tag_length = tag_length
        self._unencrypted_content_length = unencrypted_content_length

    @classmethod
    def from_s3_metatdata(cls, s3_metadata: Dict[str, str]):
        unencrypted_content_length = s3_metadata.get("x-amz-unencrypted-content-length")
        if unencrypted_content_length is not None:
            unencrypted_content_length = int(unencrypted_content_length)

        material_description = s3_metadata.get("x-amz-matdesc")
        if material_description is not None:
            material_description = json.loads(material_description)

        return cls(
            wrapped_data_key=base64.b64decode(s3_metadata["x-amz-key-v2"]),
            iv=base64.b64decode(s3_metadata["x-amz-iv"]),
            material_description=material_description,
            key_wrapping_algorithm=s3_metadata["x-amz-wrap-alg"],
            content_encryption_algorithm=s3_metadata["x-amz-cek-alg"],
            tag_length=int(s3_metadata["x-amz-tag-len"]),
            unencrypted_content_length=unencrypted_content_length,
        )

    def generate(self) -> Dict[str, str]:
        metadata = {}

        # CEK in key wrapped form.
        metadata["x-amz-key-v2"] = base64.b64encode(self._wrapped_data_key).decode()

        # Randomly generated IV(per S3 object), base64 encoded.
        metadata["x-amz-iv"] = base64.b64encode(self._iv).decode()

        # Customer provided material description in JSON format.
        if self._material_description:
            metadata["x-amz-matdesc"] = json.dumps(self._material_description)

        # Key wrapping algorithm used.
        if self._key_wrapping_algorithm:
            metadata["x-amz-wrap-alg"] = self._key_wrapping_algorithm

        # Content encryption algorithm used.
        if self._content_encryption_algorithm:
            metadata["x-amz-cek-alg"] = self._content_encryption_algorithm

        # Tag length (in bits) when AEAD is in use.
        if self._tag_length:
            metadata["x-amz-tag-len"] = str(self._tag_length)

        if self._unencrypted_content_length:
            metadata["x-amz-unencrypted-content-length"] = str(self._unencrypted_content_length)

        return metadata

    @property
    def wrapped_data_key(self) -> bytes:
        return self._wrapped_data_key

    @property
    def iv(self) -> bytes:
        return self._iv

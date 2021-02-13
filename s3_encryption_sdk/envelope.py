from typing import Dict, Optional
import base64
import json


class Envelope(object):
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
        self._metadata = {}

        # CEK in key wrapped form.
        self._metadata["x-amz-key-v2"] = base64.b64encode(wrapped_data_key).decode()

        # Randomly generated IV(per S3 object), base64 encoded.
        self._metadata["x-amz-iv"] = base64.b64encode(iv).decode()

        # Customer provided material description in JSON format.
        if material_description:
            self._metadata["x-amz-matdesc"] = json.dumps(material_description)

        # Key wrapping algorithm used.
        if key_wrapping_algorithm:
            self._metadata["x-amz-wrap-alg"] = key_wrapping_algorithm

        # Content encryption algorithm used.
        if content_encryption_algorithm:
            self._metadata["x-amz-cek-alg"] = content_encryption_algorithm

        # Tag length (in bits) when AEAD is in use.
        if tag_length:
            self._metadata["x-amz-tag-len"] = str(tag_length)

        if unencrypted_content_length:
            self._metadata["x-amz-unencrypted-content-length"] = str(unencrypted_content_length)

    @classmethod
    def from_metatdata(cls, metadata: Dict[str, str]):
        return cls(
            wrapped_data_key=base64.b64decode(metadata["x-amz-key-v2"]),
            iv=base64.b64decode(metadata["x-amz-iv"]),
            material_description=json.loads(metadata["x-amz-matdesc"]),
            key_wrapping_algorithm=metadata["x-amz-wrap-alg"],
            content_encryption_algorithm=metadata["x-amz-cek-alg"],
            tag_length=int(metadata["x-amz-tag-len"]),
            unencrypted_content_length=int(metadata["x-amz-unencrypted-content-length"]),
        )

    @classmethod
    def from_encryption_material(cls, encryption_material):
        return cls(**encryption_material)

    def update_unencrypted_content_length(self, content_length: int) -> None:
        self._metadata["x-amz-unencrypted-content-length"] = str(content_length)

    def add_kms_data_key_encryption_algorithm(self) -> None:
        material_description = json.loads(self._metadata.get("x-amz-matdesc", "{}"))
        material_description["aws:x-amz-cek-alg"] = "AES/GCM/NoPadding"
        self._metadata["x-amz-matdesc"] = json.dumps(material_description)

    @property
    def wrapped_data_key(self) -> bytes:
        return base64.b64decode(self._metadata.get("x-amz-key-v2"))

    @property
    def iv(self) -> bytes:
        return base64.b64decode(self._metadata.get("x-amz-iv"))

    @property
    def metadata(self) -> Dict[str, str]:
        return self._metadata

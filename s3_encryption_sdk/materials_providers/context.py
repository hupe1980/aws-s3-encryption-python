from typing import Dict, Optional


class EncryptionContext(object):
    """Additional information about an encryption request."""

    def __init__(
        self,
        bucket_name: str,
        object_key: str,
        material_description: Optional[Dict[str, str]] = None,
        s3_metadata: Optional[Dict[str, str]] = None,
        unencrypted_content_length: Optional[int] = None,
    ) -> None:
        if material_description is None:
            material_description = {}

        self._bucket_name = bucket_name
        self._object_key = object_key
        self._material_description = material_description
        self._s3_metadata = s3_metadata
        self._unencrypted_content_length = unencrypted_content_length

    @property
    def bucket_name(self) -> str:
        return self._bucket_name

    @property
    def object_key(self) -> str:
        return self._object_key

    @property
    def material_description(self) -> Dict[str, str]:
        return self._material_description

    @property
    def s3_metadata(self) -> Optional[Dict[str, str]]:
        return self._s3_metadata

    @property
    def unencrypted_content_length(self) -> Optional[int]:
        return self._unencrypted_content_length

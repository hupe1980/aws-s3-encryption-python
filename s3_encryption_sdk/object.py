import base64
from botocore.response import StreamingBody

from .keys import DataKey
from .materials_providers import EncryptionContext, MaterialsProvider


class DecryptionStreamingBodyWrapper(object):
    def __init__(self, streaming_body: StreamingBody, data_key: DataKey) -> None:
        self._streaming_body = streaming_body
        self._data_key = data_key

    def read(self):
        ciphertext = base64.b64decode(self._streaming_body.read())
        return self._data_key.decrypt(ciphertext)

    def __getattr__(self, name: str):
        """Catch any method/attribute lookups that are not defined in this class and try
        to find them on the provided bridge object.
        :param str name: Attribute name
        :returns: Result of asking the provided streaming object for that attribute name
        :raises AttributeError: if attribute is not found on provided bridge object
        """
        return getattr(self._streaming_body, name)


class EncryptedObject(object):
    def __init__(
        self,
        materials_provider: MaterialsProvider,
        obj,
    ) -> None:
        self._materials_provider = materials_provider
        self._object = obj

    def put(self, Body, **kwargs):
        encryption_context = EncryptionContext(
            bucket_name=self._object.bucket_name,
            object_key=self._object.key,
            unencrypted_content_length=len(Body),
        )

        materials = self._materials_provider.encryption_materials(encryption_context)

        metadata = kwargs.pop("Metadata", {})

        metadata.update(**materials.metadata.generate())

        encrypted_body = materials.data_key.encrypt(Body.encode())

        return self._object.put(Body=base64.b64encode(encrypted_body).decode(), Metadata=metadata, **kwargs)

    def get(self):
        obj = self._object.get()

        encryption_context = EncryptionContext(
            bucket_name=self._object.bucket_name,
            object_key=self._object.key,
            s3_metadata=obj["Metadata"],
        )

        materials = self._materials_provider.decryption_materials(encryption_context)

        obj["Body"] = DecryptionStreamingBodyWrapper(
            streaming_body=obj["Body"],
            data_key=materials.data_key,
        )

        return obj

    def __getattr__(self, name: str):
        """Catch any method/attribute lookups that are not defined in this class and try
        to find them on the provided bridge object.
        :param str name: Attribute name
        :returns: Result of asking the provided object object for that attribute name
        :raises AttributeError: if attribute is not found on provided bridge object
        """
        return getattr(self._object, name)

import base64
from botocore.response import StreamingBody

from .data_key import DataKey
from .envelope import Envelope
from .materials_providers import MaterialsProvider


class DecryptionStreamingBodyWrapper(object):
    def __init__(self, streaming_body: StreamingBody, data_key: DataKey) -> None:
        self._streaming_body = streaming_body
        self._data_key = data_key

    def read(self):
        bytes = base64.b64decode(self._streaming_body.read())
        return self._data_key.decrypt(bytes)

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
        object,
    ) -> None:
        self._materials_provider = materials_provider
        self._object = object

    def put(self, Body, **kwargs):
        data_key, envelope = self._materials_provider.encryption_materials(
            encryption_context=dict(
                object_key=self._object.key,
                bucket_name=self._object.bucket_name,
            )
        )

        metadata = kwargs.pop("Metadata", {})

        envelope.update_unencrypted_content_length(len(Body))

        metadata.update(**envelope.metadata)

        encrypted_body = data_key.encrypt(Body.encode())

        return self._object.put(Body=base64.b64encode(encrypted_body).decode(), Metadata=metadata, **kwargs)

    def get(self):
        obj = self._object.get()

        data_key = self._materials_provider.decryption_materials(
            encryption_context=dict(
                object_key=self._object.key,
                bucket_name=self._object.bucket_name,
                envelope=Envelope.from_metatdata(obj["Metadata"]),
            )
        )

        obj["Body"] = DecryptionStreamingBodyWrapper(
            streaming_body=obj["Body"],
            data_key=data_key,
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

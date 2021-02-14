import boto3
from botocore.client import BaseClient

from .materials_providers import MaterialsProvider
from .object import EncryptedObject


class EncryptedClient(object):
    def __init__(
        self,
        client: BaseClient,
        materials_provider: MaterialsProvider,
    ) -> None:
        self._client = client
        self._materials_provider = materials_provider

    def put_object(self, Bucket: str, Key: str, **kwargs):
        obj = EncryptedObject(
            materials_provider=self._materials_provider,
            object=boto3.resource("s3").Object(Bucket, Key),
        )
        return obj.put(**kwargs)

    def get_object(self, Bucket: str, Key: str, **kwargs):
        obj = EncryptedObject(
            materials_provider=self._materials_provider,
            object=boto3.resource("s3").Object(Bucket, Key),
        )
        return obj.get(**kwargs)

    def __getattr__(self, name: str):
        """Catch any method/attribute lookups that are not defined in this class and try
        to find them on the provided bridge object.
        :param str name: Attribute name
        :returns: Result of asking the provided client object for that attribute name
        :raises AttributeError: if attribute is not found on provided bridge object
        """
        return getattr(self._client, name)

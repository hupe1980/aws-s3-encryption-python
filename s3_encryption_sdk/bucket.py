from boto3.resources.base import ServiceResource

from .materials_providers import MaterialsProvider
from .object import EncryptedObject


class EncryptedBucket(object):
    def __init__(
        self,
        bucket: ServiceResource,
        materials_provider: MaterialsProvider,
    ) -> None:
        self._bucket = bucket
        self._materials_provider = materials_provider

    def put_object(self, Key: str, **kwargs):
        obj = EncryptedObject(
            materials_provider=self._materials_provider,
            obj=self._bucket.Object(Key),
        )
        return obj.put(**kwargs)

    def Object(self, key: str) -> EncryptedObject:
        return EncryptedObject(
            materials_provider=self._materials_provider,
            obj=self._bucket.Object(key),
        )

    def __getattr__(self, name: str):
        """Catch any method/attribute lookups that are not defined in this class and try
        to find them on the provided bridge object.
        :param str name: Attribute name
        :returns: Result of asking the provided bucket object for that attribute name
        :raises AttributeError: if attribute is not found on provided bridge object
        """
        return getattr(self._bucket, name)

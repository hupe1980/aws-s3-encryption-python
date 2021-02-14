from abc import ABC, abstractmethod, abstractproperty
from cryptography.hazmat.primitives.keywrap import aes_key_wrap, aes_key_unwrap


class WrappingKey(ABC):
    @abstractmethod
    def wrap_data_key(self, data_key: bytes) -> bytes:
        pass

    @abstractmethod
    def unwrap_data_key(self, wrapped_data_key: bytes) -> bytes:
        pass

    @abstractproperty
    def algorithm_name(self) -> str:
        pass


class AesWrappingKey(WrappingKey):
    def __init__(
        self,
        wrapping_key: bytes,
    ):
        self._wrapping_key = wrapping_key

    def wrap_data_key(self, data_key: bytes) -> bytes:
        return aes_key_wrap(
            wrapping_key=self._wrapping_key,
            key_to_wrap=data_key,
        )

    def unwrap_data_key(self, wrapped_data_key: bytes) -> bytes:
        return aes_key_unwrap(
            wrapping_key=self._wrapping_key,
            wrapped_key=wrapped_data_key,
        )

    @property
    def algorithm_name(self) -> str:
        return "AESWrap"

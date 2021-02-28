import secrets
from enum import Enum
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


class DataKeyAlgorithms(Enum):
    AES_128_GCM_IV12_TAG16 = ("AES/GCM/NoPadding", algorithms.AES, modes.GCM, 16, 12, 16)
    AES_192_GCM_IV12_TAG16 = ("AES/GCM/NoPadding", algorithms.AES, modes.GCM, 24, 12, 16)
    AES_256_GCM_IV12_TAG16 = ("AES/GCM/NoPadding", algorithms.AES, modes.GCM, 32, 12, 16)

    def __init__(
        self,
        name: str,
        algorithm: algorithms,
        mode: modes,
        data_key_length: int,
        iv_length: int,
        tag_len: int,
    ) -> None:
        self._name = name
        self._algorithm = algorithm
        self._mode = mode
        self._data_key_length = data_key_length
        self._iv_length = iv_length
        self._tag_len = tag_len

    def generate_data_key(self) -> bytes:
        return secrets.token_bytes(self._data_key_length)

    def generate_iv(self) -> bytes:
        return secrets.token_bytes(self.iv_length)

    @property
    def name(self) -> str:
        return self._name

    @property
    def algorithm(self) -> algorithms:
        return self._algorithm

    @property
    def mode(self) -> modes:
        return self._mode

    @property
    def data_key_length(self) -> int:
        return self._data_key_length

    @property
    def iv_length(self) -> int:
        return self._iv_length

    @property
    def tag_len(self) -> int:
        return self._tag_len


class DataKey(object):
    def __init__(
        self,
        algorithm: DataKeyAlgorithms,
        key: bytes,
        iv: bytes,
    ) -> None:
        self._algorithm = algorithm
        self._key = key
        self._iv = iv

    def encrypt(self, plaintext: bytes) -> bytes:
        """Encrypt data."""
        encryptor = Cipher(
            algorithm=self._algorithm.algorithm(self._key),
            mode=self._algorithm.mode(self._iv),
            backend=default_backend(),
        ).encryptor()

        ciphertext = encryptor.update(plaintext) + encryptor.finalize()

        return ciphertext + encryptor.tag

    def decrypt(self, ciphertext: bytes) -> bytes:
        """Decrypt data."""
        tag = ciphertext[-self._algorithm.tag_len:]
        ciphertext = ciphertext[:-self._algorithm.tag_len]

        decryptor = Cipher(
            algorithm=self._algorithm.algorithm(self._key),
            mode=self._algorithm.mode(self._iv, tag),
            backend=default_backend(),
        ).decryptor()

        plaintext = decryptor.update(ciphertext) + decryptor.finalize()

        return plaintext

    @property
    def algorithm(self) -> DataKeyAlgorithms:
        return self._algorithm

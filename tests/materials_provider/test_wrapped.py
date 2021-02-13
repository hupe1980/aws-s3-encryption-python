import secrets
from s3_encryption_sdk import AesWrappingKey
from s3_encryption_sdk.materials_providers import WrappedMaterialsProvider


def test_encryption_materials():
    secret_key = secrets.token_bytes(32)

    materials_provider = WrappedMaterialsProvider(
        wrapping_key=AesWrappingKey(secret_key),
    )

    plaintext = b"foo bar"

    encryption_key, envelope = materials_provider.encryption_materials(encryption_context=dict())

    ciphertext = encryption_key.encrypt(plaintext)

    decryption_key = materials_provider.decryption_materials(
        encryption_context=dict(
            envelope=envelope,
        )
    )

    decrypted_ciphertext = decryption_key.decrypt(ciphertext)

    assert plaintext != ciphertext
    assert plaintext == decrypted_ciphertext

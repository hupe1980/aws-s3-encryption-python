import secrets
from s3_encryption_sdk.keys import AesWrappingKey
from s3_encryption_sdk.materials_providers import EncryptionContext, WrappedMaterialsProvider


def test_encryption_materials():
    secret_key = secrets.token_bytes(32)

    materials_provider = WrappedMaterialsProvider(
        wrapping_key=AesWrappingKey(secret_key),
    )

    plaintext = b"foo bar"

    encryption_context = EncryptionContext(bucket_name="dummy", object_key="dummy")

    materials = materials_provider.encryption_materials(encryption_context)

    ciphertext = materials.data_key.encrypt(plaintext)

    encryption_context = EncryptionContext(
        bucket_name="dummy",
        object_key="dummy",
        s3_metadata=materials.metadata.generate(),
    )

    materials = materials_provider.decryption_materials(encryption_context)

    decrypted_ciphertext = materials.data_key.decrypt(ciphertext)

    assert plaintext != ciphertext
    assert plaintext == decrypted_ciphertext

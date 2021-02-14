from s3_encryption_sdk.keys import DataKeyAlgorithms
from s3_encryption_sdk.materials_providers import EncryptionContext, KmsMaterialsProvider


def test_encryption_materials(kms, key):
    materials_provider = KmsMaterialsProvider(
        key_id=key["KeyMetadata"]["Arn"],
        client=kms,
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


def test_aes128_encryption_materials(kms, key):
    aes128 = DataKeyAlgorithms.AES_128_GCM_IV12_TAG16

    materials_provider = KmsMaterialsProvider(
        key_id=key["KeyMetadata"]["Arn"],
        client=kms,
        algorithm=aes128,
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

    assert aes128.data_key_length == materials.data_key.algorithm.data_key_length == (128 // 8)


def test_aes192_encryption_materials(kms, key):
    aes192 = DataKeyAlgorithms.AES_192_GCM_IV12_TAG16

    materials_provider = KmsMaterialsProvider(
        key_id=key["KeyMetadata"]["Arn"],
        client=kms,
        algorithm=aes192,
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

    assert aes192.data_key_length == materials.data_key.algorithm.data_key_length == (192 // 8)

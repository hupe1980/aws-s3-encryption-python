from s3_encryption_sdk import DataKeyAlgorithms
from s3_encryption_sdk.materials_providers import KmsMaterialsProvider


def test_encryption_materials(kms, key):
    materials_provider = KmsMaterialsProvider(
        key_id=key["KeyMetadata"]["Arn"],
        client=kms,
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


def test_aes128_encryption_materials(kms, key):
    aes128 = DataKeyAlgorithms.AES_128_GCM_IV12_TAG16

    materials_provider = KmsMaterialsProvider(
        key_id=key["KeyMetadata"]["Arn"],
        client=kms,
        algorithm=aes128,
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

    assert aes128.data_key_length == encryption_key.algorithm.data_key_length == (128 // 8)

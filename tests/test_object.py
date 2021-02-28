from s3_encryption_sdk import EncryptedObject


def test_get(materials_provider, bucket):
    obj = bucket.Object("object")

    crypto_obj = EncryptedObject(
        obj=obj,
        materials_provider=materials_provider,
    )

    body = "foo bar 4711"

    crypto_obj.put(
        Body=body,
    )

    encrypted_obj = obj.get()
    decrypted_obj = crypto_obj.get()

    assert body != encrypted_obj["Body"].read().decode()
    assert body == decrypted_obj["Body"].read().decode()

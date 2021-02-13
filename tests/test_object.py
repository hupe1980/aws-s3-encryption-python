from s3_encryption_sdk import CryptoObject


def test_get(materials_provider, bucket):
    object = bucket.Object("object")

    crypto_object = CryptoObject(
        object=object,
        materials_provider=materials_provider,
    )

    body = "foo bar 4711"

    crypto_object.put(
        Body=body,
    )

    encrypted_obj = object.get()
    decrypted_obj = crypto_object.get()

    assert body != encrypted_obj["Body"].read().decode("utf8")
    assert body == decrypted_obj["Body"].read().decode("utf8")

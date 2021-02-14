from s3_encryption_sdk import EncryptedBucket


def test_object_get(materials_provider, bucket):
    crypto_bucket = EncryptedBucket(
        bucket=bucket,
        materials_provider=materials_provider,
    )

    body = "foo bar 4711"

    crypto_bucket.put_object(
        Key="object",
        Body=body,
    )

    encrypted_obj = bucket.Object("object").get()
    decrypted_obj = crypto_bucket.Object("object").get()

    assert body != encrypted_obj["Body"].read().decode("utf8")
    assert body == decrypted_obj["Body"].read().decode("utf8")

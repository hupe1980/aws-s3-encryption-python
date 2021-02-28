from s3_encryption_sdk import EncryptedClient


def test_get_object(materials_provider, s3, bucket):
    crypto_s3 = EncryptedClient(
        client=s3,
        materials_provider=materials_provider,
    )

    body = "foo bar"

    crypto_s3.put_object(
        Bucket=bucket.name,
        Key="object",
        Body=body,
    )

    encrypted_obj = s3.get_object(
        Bucket=bucket.name,
        Key="object",
    )

    decrypted_obj = crypto_s3.get_object(
        Bucket=bucket.name,
        Key="object",
    )

    assert body != encrypted_obj["Body"].read().decode()
    assert body == decrypted_obj["Body"].read().decode()

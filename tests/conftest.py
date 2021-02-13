import boto3
import pytest
from moto import mock_kms, mock_s3

from s3_encryption_sdk.materials_providers import KmsMaterialsProvider


@pytest.fixture(scope="module")
def kms():
    with mock_kms():
        kms = boto3.client("kms", region_name="us-east-1")
        yield kms


@pytest.fixture(scope="module")
def key(kms):
    key = kms.create_key(
        Policy="my policy",
        Description="my key",
        KeyUsage="ENCRYPT_DECRYPT",
        Tags=[{"TagKey": "project", "TagValue": "moto"}],
    )
    return key


@pytest.fixture(scope="module")
def materials_provider(kms, key):
    materials_provider = KmsMaterialsProvider(
        key_id=key["KeyMetadata"]["Arn"],
        client=kms,
    )
    return materials_provider


@pytest.fixture(scope="module")
def s3():
    with mock_s3():
        s3 = boto3.client("s3", region_name="us-east-1")
        yield s3


@pytest.fixture(scope="module")
def bucket(s3):
    name = "dummy"
    s3.create_bucket(Bucket=name)
    return boto3.resource("s3").Bucket(name)

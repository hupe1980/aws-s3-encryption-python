############################
S3 Encryption SDK for Python
############################

.. image:: https://img.shields.io/pypi/v/s3-encryption-sdk.svg
   :target: https://pypi.python.org/pypi/s3-encryption-sdk
   :alt: Latest Version

.. image:: https://img.shields.io/pypi/pyversions/s3-encryption-sdk.svg
   :target: https://pypi.org/project/s3-encryption-sdk
   :alt: Supported Python Versions

.. image:: https://github.com/hupe1980/aws-s3-encryption-python/workflows/ci/badge.svg
   :target: https://github.com/hupe1980/aws-s3-encryption-python/actions?query=workflow%3Aci
   :alt: ci

Client-side encryption for S3

You can find the source on `GitHub`_.

***************
Getting Started
***************

Required Prerequisites
======================

* Python 3.6+

Installation
============

.. note::

   If you have not already installed `cryptography`_, you might need to install additional
   prerequisites as detailed in the `cryptography installation guide`_ for your operating
   system.

   .. code::

       $ pip install s3-encryption-sdk

*****
Usage
*****

.. code-block:: python

   import boto3
   from s3_encryption_sdk import CryptoS3
   from s3_encryption_sdk.materials_providers import KmsMaterialsProvider


   materials_provider = KmsMaterialsProvider(
      key_id="",
      client=boto3.client("kms", region_name="us-east-1"),
   )
   
   s3 = boto3.client("s3", region_name="us-east-1")
   
   crypto_s3 = CryptoS3(
      client=s3,
      materials_provider=materials_provider,
   )

   key = "4711"
   plaintext = "foo bar"
   
   crypto_s3.put_object(
      Bucket=bucket.name,
      Key=key,
      Body=plaintext,
   )
   
   encrypted_obj = s3.get_object(
      Bucket=bucket.name,
      Key="object",
   )
    
   decrypted_obj = crypto_s3.get_object(
      Bucket=bucket.name,
      Key="object",
   )

   assert plaintext != encrypted_obj["Body"].read().decode("utf8")
   assert plaintext == decrypted_obj["Body"].read().decode("utf8")


.. _cryptography: https://cryptography.io/en/latest/
.. _cryptography installation guide: https://cryptography.io/en/latest/installation.html
.. _GitHub: https://github.com/hupe1980/cryptoshredding/
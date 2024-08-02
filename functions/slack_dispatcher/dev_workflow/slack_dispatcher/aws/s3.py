"""Aws S3 module interacting with S3 buckets."""

import logging
import os

logger = logging.getLogger()
logger.setLevel(os.environ.get("LOGGING_LEVEL", logging.INFO))


def upload(s3_client, bucket: str, key: str, payload: str) -> None:
    """
    Put data into an S3 bucket object.
    """
    try:
        s3_client.put_object(Bucket=bucket, Key=key, Body=payload.encode("utf-8"))
        logger.info(f"Uploaded to S3: {key}")
    except Exception as e:
        logger.error(f"Error uploading payload to S3: {e}")
        raise e

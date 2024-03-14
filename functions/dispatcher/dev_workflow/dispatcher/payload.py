import logging
import os

logger = logging.getLogger()
logger.setLevel(os.environ.get("LOGGING_LEVEL", logging.INFO))


def upload(s3_client, bucket, key, payload):
    logger.debug(s3_client, bucket, key, payload)
    s3_client.put_object(
        Bucket=bucket,
        Key=key,
        Body=payload.encode('utf-8')
    )

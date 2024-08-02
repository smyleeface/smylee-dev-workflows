import logging
import os

logger = logging.getLogger()
logger.setLevel(os.environ.get("LOGGING_LEVEL", logging.INFO))


def upload(s3_client, bucket, key, payload):
    try:
        s3_client.put_object(
            Bucket=bucket,
            Key=key,
            Body=payload.encode('utf-8')
        )
    except Exception as e:
        logger.error(f"Error uploading payload to S3: {e}")
        raise e

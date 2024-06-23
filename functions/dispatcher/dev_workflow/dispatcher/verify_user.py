import logging
import os

logger = logging.getLogger()
logger.setLevel(os.environ.get("LOGGING_LEVEL", logging.INFO))


def verify_user(event_user: str, s3_client, bucket, key):
    response = s3_client.get_object(Bucket=bucket, Key=key)
    response_body = response["Body"].read().decode("utf-8")
    list_of_users = response_body.split("\n")
    if event_user in list_of_users:
        logger.info(f"User {event_user} is in the list")
        return True
    logger.info(f"User {event_user} is not in the list")
    return False

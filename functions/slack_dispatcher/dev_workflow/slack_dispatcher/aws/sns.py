"""Aws SNS module for interacting with sns."""

import logging
import os

logger = logging.getLogger()
logger.setLevel(os.environ.get("LOGGING_LEVEL", logging.INFO))


def publish(sns_client, topic_arn: str, message: str) -> None:
    """Publish a message to an SNS topic."""
    try:
        sns_client.publish(
            TopicArn=topic_arn,
            Message=message,
        )
        logger.info(f"Published to SNS: {message}")
    except Exception as e:
        print(f"Error: {e}")
        exit(1)

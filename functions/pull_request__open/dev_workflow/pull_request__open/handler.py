import logging
import os

logger = logging.getLogger()
logger.setLevel(os.environ.get("LOGGING_LEVEL", logging.INFO))


def lambda_handler(event, context):

    logger.debug(event)
    return "done"

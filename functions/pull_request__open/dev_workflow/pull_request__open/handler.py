import logging
import os

import json

logger = logging.getLogger()
logger.setLevel(os.environ.get("LOGGING_LEVEL", logging.INFO))


def lambda_handler(event, context):
    logger.debug(event)
    message_string = event['Records'][0]['Sns']['Message']
    message = json.loads(json.dumps(message_string))
    logger.info(message)
    return "done"

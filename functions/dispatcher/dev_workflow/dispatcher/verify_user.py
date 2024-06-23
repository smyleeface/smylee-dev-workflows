import logging
import os

logger = logging.getLogger()
logger.setLevel(os.environ.get("LOGGING_LEVEL", logging.INFO))


def verify_user(event_user: str) -> bool:
    list_of_users = ["smyleeface", "pattyr"]
    if event_user in list_of_users:
        logger.info(f"User {event_user} is in the list")
        return True
    logger.info(f"User {event_user} is not in the list")
    return False

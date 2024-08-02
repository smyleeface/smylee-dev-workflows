import logging
import os

import dev_workflow.slack_dispatcher.routes as routes
import dev_workflow.slack_dispatcher.slack.utils as slack_utils

logger = logging.getLogger()
logger.setLevel(os.environ.get("LOGGING_LEVEL", logging.DEBUG))


def run(ctx):
    """"This function will parse the command arguments send to the requested command route"""
    response_url = ctx.get("response_url")
    command_text = ctx.get("text")

    slack_utils.send_command_received_message(response_url)
    action_requested = command_text.split(' ', 1)[0]
    command_arguments, missing_values = slack_utils.get_command_arguments(command_text)

    if action_requested == "hugo-cover-image":
        routes.hugo_cover.start(ctx, command_arguments, missing_values)
    else:
        routes.unknown_command.start(response_url, action_requested)

    return {
        "isBase64Encoded": False,
        "statusCode": 200,
        "headers": {},
        "body": "completed",
    }

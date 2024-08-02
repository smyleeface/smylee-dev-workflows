"""Dispatcher routes for the Slack dispatcher"""

import logging
import os

import dev_workflow.slack_dispatcher.routes.hugo_cover as route_hugo_cover
import dev_workflow.slack_dispatcher.routes.unknown_command as route_unknown_command
import dev_workflow.slack_dispatcher.slack.utils as slack_utils

logger = logging.getLogger()
logger.setLevel(os.environ.get("LOGGING_LEVEL", logging.INFO))


def run(ctx):
    """
    This receives a context payload from the entry point.
    It figures out the action requested, converts the arguments
    into a key-value pair, and any arguments without values.
    It then sends this information along with the contexts
    needed to the appropriate action requested.
    """
    response_url = ctx.get("response_url")
    command_text = ctx.get("text")

    slack_utils.send_command_received_message(response_url, command_text)
    action_requested = command_text.split(" ", 1)[0]
    command_arguments, missing_values = slack_utils.get_command_arguments(command_text)

    if action_requested == "hugo-cover-image":
        route_hugo_cover.start(ctx, command_arguments, missing_values)
    else:
        route_unknown_command.start(response_url, action_requested)

    return {
        "isBase64Encoded": False,
        "statusCode": 200,
        "headers": {},
        "body": "completed",
    }

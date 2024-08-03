"""This function contains logic when a command is not recognized"""

import dev_workflow.slack_dispatcher.slack.utils as slack_utils


def start(response_url: str, action_requested: str) -> None:
    """Send message to Slack that command is not recognized"""
    payload_to_send = {
        "text": f"Command `{action_requested}` not recognized",
        "response_type": "in_channel",
    }
    slack_utils.post_message(response_url, payload_to_send)

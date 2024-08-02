"""Slack utility functions"""

import json
import logging
import os
import shlex
import urllib.parse

import requests

logger = logging.getLogger()
logger.setLevel(os.environ.get("LOGGING_LEVEL", logging.INFO))


def parse_query_string(query_string: str) -> dict:
    """Parse the query string from the slack payload"""
    parsed_query = urllib.parse.parse_qs(query_string)
    parsed_query_single_values = {k: v[0] for k, v in parsed_query.items()}
    return parsed_query_single_values


def get_action(parsed_json: dict) -> str:
    """Get the action requested from the slack payload"""
    requested_text = parsed_json.get("text", "")
    return requested_text.split(" ", 1)[0]


def post_message(url: str, data: dict) -> int:
    """Post a message to Slack"""
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        logger.info(
            f"Response {response.status_code} from Slack for message: {json.dumps(data)}"
        )
        return response.status_code
    except Exception as e:
        print(f"Error sending message to Slack: {e}")
        exit(1)


def get_command_arguments(command_text: str) -> dict:
    """Get the command arguments from the users input"""
    parts = shlex.split(command_text)
    result_dict = {}
    i = 0
    while i < len(parts):
        if parts[i].startswith("--"):
            key = parts[i][2:]  # Remove '--' prefix to get the key
            # Collect all non-parameter parts as a single value
            value_parts = []
            i += 1
            while i < len(parts) and not parts[i].startswith("--"):
                value_parts.append(parts[i])
                i += 1
            # Join the collected value parts with a space
            value = " ".join(value_parts)

            # Convert value to integer if possible, otherwise keep it as a string
            if value.isdigit():
                value = int(value)

            # Assign the collected value or True for flags
            result_dict[key] = value if value_parts else True
        else:
            i += 1
    return result_dict


def send_command_received_message(response_url: str, command_text: str) -> None:
    """Send a message to Slack for the user that the command was received"""
    payload_to_send = {
        "text": f"Request `{command_text}` received. Processing...",
        "response_type": "in_channel",
    }
    post_message(response_url, payload_to_send)

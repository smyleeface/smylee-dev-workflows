"""
This module contains the logic to start the process to
generate a cover image for a hugo post
"""

import json

import dev_workflow.slack_dispatcher.aws.sns as sns
import dev_workflow.slack_dispatcher.slack.utils as slack_utils


def missing_values_slack_message(missing_values: list) -> dict:
    """Generate a Slack message to tell user about missing values"""
    formatted_values = [f"`--{name}`" for name in missing_values]
    return {
        "text": f"Missing values for {', '.join(formatted_values)}",
        "response_type": "in_channel",
    }


def missing_key_slack_message(missing_values: list) -> dict:
    """Generate a Slack message to tell user about missing keys"""
    formatted_values = [f"`--{name}`" for name in missing_values]
    return {
        "text": f"Missing keys for {', '.join(formatted_values)}",
        "response_type": "in_channel",
    }


def trigger_image_generator_sns_message(
    command_arguments: dict, response_url: str
) -> dict:
    """Generate the SNS message to trigger the image generator"""
    return {
        "github": {
            "repository_name": command_arguments.get("repository-name"),
            "pull_request_number": command_arguments.get("pull-request-number"),
            "branch_name": command_arguments.get("branch-name"),
        },
        "slack": {"response_url": response_url},
    }


def missing_values_list(ctx: dict) -> list:
    """Check for missing values in the command arguments"""
    missing_values = []
    for key, value in ctx.items():
        if value is None or value == "" or not value:
            missing_values.append(key)
    return missing_values


def missing_keys_list(ctx: dict) -> list:
    """Check for missing key in the command arguments"""
    missing_keys = ["repository-name", "pull-request-number", "branch-name"]
    return [key for key in missing_keys if key not in ctx.keys()]


def start(ctx: dict, command_arguments: dict) -> None:
    """This function will start the process to generate a cover image for a hugo post"""
    response_url = ctx.get("response_url")
    missing_keys = missing_keys_list(command_arguments)
    missing_values = missing_values_list(command_arguments)
    if missing_keys:
        slack_message = missing_key_slack_message(missing_keys)
        slack_utils.post_message(response_url, slack_message)
    elif missing_values:
        slack_message = missing_values_slack_message(missing_values)
        slack_utils.post_message(response_url, slack_message)
    else:
        sns_client = ctx.get("sns_client")
        cover_image_topic_arn = ctx.get("topic_arn")
        sns_message = trigger_image_generator_sns_message(
            command_arguments, response_url
        )
        sns.publish(sns_client, cover_image_topic_arn, json.dumps(sns_message))

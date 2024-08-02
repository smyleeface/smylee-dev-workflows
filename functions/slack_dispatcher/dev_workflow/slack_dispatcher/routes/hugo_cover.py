import dev_workflow.slack_dispatcher.aws.sns as sns
import dev_workflow.slack_dispatcher.slack.utils as slack_utils


def missing_values_slack_message(missing_values):
    return {
        "text": f"Missing values for {', '.join(missing_values)}",
        "response_type": "in_channel"
    }


def trigger_generator_sns_message(command_arguments, response_url):
    return {
        "github": {
            "repository_name": command_arguments.get("repository-name"),
            "pull_request_number": command_arguments.get("pr-number"),
            "branch_name": command_arguments.get("branch-name")
        },
        "slack": {
            "response_url": response_url
        }
    }


def start(ctx, command_arguments, missing_values):
    """This function will start the process to generate a cover image for a hugo post"""
    response_url = ctx.get("response_url")
    if missing_values:
        slack_message = missing_values_slack_message(missing_values)
        slack_utils.post_message(response_url, slack_message)
    else:
        sns_client = ctx.get("sns_client")
        cover_image_topic_arn = ctx.get("topic_arn")
        sns_message = trigger_generator_sns_message(command_arguments, response_url)
        sns.publish(sns_client, cover_image_topic_arn, sns_message)

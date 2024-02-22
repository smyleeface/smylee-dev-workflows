from .pr__open import (message as pr__open_message,
                       sns_topic_arn as pr__open_sns_topic_arn)


def dispatch(sns_client, action, github_event_type, payload):

    if github_event_type == "pull_request" and action in ["opened", "reopened"]:
        print("pull request opened")
        message = pr__open_message(payload)
        sns_client.publish(
            TopicArn=pr__open_sns_topic_arn,
            Message=message,
        )

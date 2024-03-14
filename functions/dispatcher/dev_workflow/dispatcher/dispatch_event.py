import os


def dispatch(sns_client, action, github_event_type, message):

    if github_event_type == "pull_request" and action in ["opened", "reopened"]:
        print("pull request opened")
        sns_topic_arn = os.environ.get("PR__OPEN_SNS_TOPIC_ARN", "")
        sns_client.publish(
            TopicArn=sns_topic_arn,
            Message=message,
        )

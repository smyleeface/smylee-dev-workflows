import os


def dispatch(sns_client, action, github_event_type, message):

    if github_event_type == "pull_request":
        if action in ["opened", "reopened"]:
            print("pull request opened")
            sns_topic_arn = os.environ.get("PR__OPEN_SNS_TOPIC_ARN", "")
            try:
                sns_client.publish(
                    TopicArn=sns_topic_arn,
                    Message=message,
                )
            except Exception as e:
                print(f"Error: {e}")
                exit(1)
        elif action in ["merged"]:
            print("pull request merged")
            sns_topic_arn = os.environ.get("PR__MERGED_SNS_TOPIC_ARN", "")
            try:
                sns_client.publish(
                    TopicArn=sns_topic_arn,
                    Message=message,
                )
            except Exception as e:
                print(f"Error: {e}")
                exit(1)

import json
import os

sns_topic_arn = os.environ.get("PR__OPEN_SNS_TOPIC_ARN", "")


def message(payload):
    message_json = {
        "pull_request_number": payload["pull_request"]["number"],
    }
    return json.dumps(message_json)

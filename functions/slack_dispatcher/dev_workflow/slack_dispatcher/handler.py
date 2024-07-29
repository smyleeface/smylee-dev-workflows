import json
import logging
import os
import requests
import urllib.parse

import boto3
from botocore.exceptions import ClientError


logger = logging.getLogger()
logger.setLevel(os.environ.get("LOGGING_LEVEL", logging.DEBUG))
#
# client = boto3.client("lambda")
# boto3_session = boto3.session.Session()
# ssm_client = boto3_session.client(service_name="ssm", region_name="us-west-2")
#
# try:
#     app_parameters = ssm_client.get_parameters(
#         Names=["/SmyleeDevWorkflows/GitHubApp/WebhookSecret"], WithDecryption=True
#     )
# except ClientError as e:
#     raise e
#
# gh_webhook_secret = app_parameters["Parameters"][0]["Value"]
#
# sns_client = boto3_session.client(service_name="sns", region_name="us-west-2")
# s3_client = boto3_session.client(service_name="s3", region_name="us-west-2")
#
# payload_upload_bucket = os.environ.get("S3_BUCKET_FOR_PAYLOADS", "")


def post_message(url, data):
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    return response.status_code


def parse_query_string(query_string):
    parsed_query = urllib.parse.parse_qs(query_string)
    parsed_query_single_values = {k: v[0] for k, v in parsed_query.items()}
    return parsed_query_single_values


def determine_action(requested_text):
    action = requested_text.split(' ', 1)[0]
    if action == "hugo-cover-image":
        message = {
            "text": "Generating cover image for Hugo please wait",
            "response_type": "in_channel"
        }
    else:
        message = {
            "text": f"Unknown command `{action}`. Please try again.",
            "response_type": "ephemeral"
        }
    return message


def lambda_handler(event, context):
    logger.debug(event)
    query_string = event.get("body", "")
    parsed_json = parse_query_string(query_string)
    print(json.dumps(parsed_json, indent=2))
    requested_text = parsed_json.get("text", "")
    message = determine_action(requested_text)
    status_code = post_message(parsed_json.get("response_url", None), message)

    return {
        "isBase64Encoded": False,
        "statusCode": status_code,
        "headers": {},
        "body": "completed",
    }

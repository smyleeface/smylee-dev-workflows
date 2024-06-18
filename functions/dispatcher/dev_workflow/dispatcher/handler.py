import json
import logging
import os

import boto3
from botocore.exceptions import ClientError
from .dispatch_event import dispatch
from .payload import upload

import dev_workflow.utils.github.payload_validator as payload_validator

logger = logging.getLogger()
logger.setLevel(os.environ.get("LOGGING_LEVEL", logging.INFO))

client = boto3.client("lambda")

boto3_session = boto3.session.Session()

ssm_client = boto3_session.client(service_name="ssm", region_name="us-west-2")

try:
    app_parameters = ssm_client.get_parameters(
        Names=["/SmyleeDevWorkflows/GitHubApp/WebhookSecret"], WithDecryption=True
    )
except ClientError as e:
    raise e

gh_webhook_secret = app_parameters["Parameters"][0]["Value"]

sns_client = boto3_session.client(service_name="sns", region_name="us-west-2")
s3_client = boto3_session.client(service_name="s3", region_name="us-west-2")

payload_upload_bucket = os.environ.get("S3_BUCKET_FOR_PAYLOADS", "")


def lambda_handler(event, context):
    logger.debug(event)
    payload_string = event.get("body", "{}")
    payload = json.loads(payload_string)
    headers = (event.get("params", {})).get("header", {})
    logger.debug(payload)
    logger.debug(payload_string)
    logger.debug(headers)
    signature = headers.get("X-Hub-Signature-256", "")
    signature_sha = signature.replace('sha256=', '')
    payload_validator.verify_signature(payload_string, gh_webhook_secret, signature)
    logger.info("Signature verified!")

    github_event_type = headers.get("X-GitHub-Event", "")
    action = payload.get("action", None)

    payload_filename = f"{github_event_type}/{action}_{signature_sha}.json"
    upload(s3_client, payload_upload_bucket, payload_filename, json.dumps(payload))

    dispatch_message = {
        "message_sha": signature_sha,
        "bucket": payload_upload_bucket,
        "key": payload_filename
    }

    dispatch(sns_client, payload, github_event_type, json.dumps(dispatch_message))

    return {
        "isBase64Encoded": False,
        "statusCode": 200,
        "headers": {},
        "body": "completed",
    }

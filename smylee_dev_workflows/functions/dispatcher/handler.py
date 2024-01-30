import logging
import os

import boto3
from botocore.exceptions import ClientError

import shared.github.payload_validator as payload_validator
from dispatch_event import dispatch


logger = logging.getLogger()
logger.setLevel(logging.INFO)

client = boto3.client('lambda')

boto3_session = boto3.session.Session()

ssm_client = boto3_session.client(
    service_name='ssm',
    region_name='us-west-2'
)

try:
    app_parameters = ssm_client.get_parameters(
        Names=[
            '/SmyleeDevWorkflows/GitHubApp/WebhookSecret'
        ],
        WithDecryption=True
    )
except ClientError as e:
    raise e

gh_webhook_secret = app_parameters['Parameters'][0]['Value']


def lambda_handler(event, context):
    payload = event['body']
    headers = event.get('headers', {})
    signature = headers.get('X-Hub-Signature-256', '')
    payload_validator.verify_signature(payload, gh_webhook_secret, signature)
    logger.info("Signature verified!")

    github_event_type = headers.get('X-GitHub-Event', '')
    dispatch(payload, github_event_type)

    return {
        "isBase64Encoded": False,
        "statusCode": 200,
        "headers": {},
        "body": "valid"
    }

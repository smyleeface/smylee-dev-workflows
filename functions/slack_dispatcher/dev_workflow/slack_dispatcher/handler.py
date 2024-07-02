import json
import logging
import os

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


def lambda_handler(event, context):
    logger.debug(event)

    return {
        "isBase64Encoded": False,
        "statusCode": 200,
        "headers": {},
        "body": "completed",
    }

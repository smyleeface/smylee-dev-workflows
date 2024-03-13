import logging
import os

import json

import boto3

logger = logging.getLogger()
logger.setLevel(os.environ.get("LOGGING_LEVEL", logging.INFO))

boto3_session = boto3.session.Session()
s3_client = boto3_session.client(service_name="s3", region_name="us-west-2")

payload_upload_bucket = os.environ.get("S3_BUCKET_FOR_PAYLOADS", "")


def lambda_handler(event, context):
    logger.debug(event)
    message_string = event['Records'][0]['Sns']['Message']
    message = json.loads(json.loads(json.dumps(message_string)))
    logger.info(message)
    file_key = message.get('key', '')
    message_sha = message.get('message_sha', '')
    local_file_path = f'/tmp/{message_sha}'
    s3_client.download_file(payload_upload_bucket, file_key, local_file_path)
    with open(local_file_path, 'r') as file:
        dispatch_contents_string = file.read()
    dispatch_contents = json.loads(json.dumps(dispatch_contents_string))
    logger.debug(dispatch_contents)
    return "done"

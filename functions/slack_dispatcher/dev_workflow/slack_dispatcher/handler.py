from datetime import datetime
import logging
import os

import boto3

import dev_workflow.slack_dispatcher.aws.s3 as s3
import dev_workflow.slack_dispatcher.slack.utils as slack_utils
import dev_workflow.slack_dispatcher.dispatcher_routes as dispatcher_routes

logger = logging.getLogger()
logger.setLevel(os.environ.get("LOGGING_LEVEL", logging.DEBUG))

boto3_session = boto3.session.Session()

sns_client = boto3_session.client(service_name="sns", region_name="us-west-2")
s3_client = boto3_session.client(service_name="s3", region_name="us-west-2")
payload_upload_bucket = os.environ.get("S3_BUCKET_FOR_PAYLOADS", "")
image_generator_topic_arn = os.environ.get("IMAGE_GENERATOR_TOPIC_ARN", "")


def lambda_handler(event, context):
    logger.debug(event)
    query_string = event.get("body", "")
    parsed_json = slack_utils.parse_query_string(query_string)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    # save the original request to s3
    original_payload_filename = f"slack/commands/{timestamp}_{parsed_json.get('trigger_id', '')}.json"
    s3.upload(s3_client, payload_upload_bucket, original_payload_filename, parsed_json)

    # run the app
    ctx = {
        "sns_client": sns_client,
        "response_url": parsed_json.get("response_url", ""),
        "text": parsed_json.get("text", ""),
        "topic_arn": image_generator_topic_arn
    }
    dispatcher_routes.run(ctx)

    return {
        "isBase64Encoded": False,
        "statusCode": 200,
        "headers": {},
        "body": "completed",
    }

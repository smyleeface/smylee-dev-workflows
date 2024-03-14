import json
import logging
import os

import boto3
from botocore.exceptions import ClientError

from github import GithubIntegration
from github import Auth

from dev_workflow.utils.split_string import split_string

logger = logging.getLogger()
logger.setLevel(os.environ.get("LOGGING_LEVEL", logging.INFO))

boto3_session = boto3.session.Session()
s3_client = boto3_session.client(service_name="s3", region_name="us-west-2")

payload_upload_bucket = os.environ.get("S3_BUCKET_FOR_PAYLOADS", "")

ssm_client = boto3_session.client(service_name='ssm', region_name='us-west-2')

try:
    app_parameters = ssm_client.get_parameters(
        Names=[
            '/SmyleeDevWorkflows/GitHubApp/Id',
            '/SmyleeDevWorkflows/GitHubApp/PrivateKey'
        ],
        WithDecryption=True
    )
except ClientError as e:
    raise e

gh_app_id = app_parameters['Parameters'][0]['Value']
gh_private_key = app_parameters['Parameters'][1]['Value']

github_auth = Auth.AppAuth(gh_app_id, gh_private_key)
github_integration = GithubIntegration(auth=github_auth)
installation = github_integration.get_installations()[0]
github_client = installation.get_github_for_installation()

bedrock_client = boto3.client('bedrock-runtime')


def lambda_handler(event, context):
    logger.debug(event)
    message_string = event['Records'][0]['Sns']['Message']
    message = json.loads(json.loads(json.dumps(message_string)))
    logger.info(message)

    # download payload from s3
    file_key = message.get('key', '')
    message_sha = message.get('message_sha', '')
    local_file_path = f'/tmp/{message_sha}'
    s3_client.download_file(payload_upload_bucket, file_key, local_file_path)
    with open(local_file_path, 'r') as file:
        dispatch_contents_string = file.read()
    dispatch_contents = json.loads(json.loads(json.dumps(dispatch_contents_string)))
    logger.debug(dispatch_contents)

    # load pull request data
    repo_name = dispatch_contents.get('repository', {}).get('full_name', '')
    pull_request_number = dispatch_contents.get('pull_request', {}).get('number', 0)
    repo = github_client.get_repo(repo_name)
    pull_request = repo.get_pull(pull_request_number)
    commits = pull_request.get_commits()
    list_of_commit_messages = list(commit.commit.message for commit in commits)
    logger.debug(list_of_commit_messages)
    prompt_template = "<s>[INST]Summarize the following commits into a pull request description. Don't list the commit messages in the summary.\n{0}\n[/INST]"
    commit_message_string = '\n'.join(list_of_commit_messages)[:200]
    input_text = {
        "prompt": prompt_template.format(commit_message_string),
        "max_tokens": 200,
        "temperature": 0.7,
        "top_p": 0.7,
        "top_k": 50
    }
    bedrock_response = bedrock_client.invoke_model(
        body=json.dumps(input_text).encode('utf-8'),
        contentType='application/json',
        accept='application/json',
        modelId='mistral.mistral-7b-instruct-v0:2'
    )

    body_contents = json.loads(json.loads(json.dumps(bedrock_response.get('body').read().decode('utf-8'))))
    logger.debug(body_contents)
    pull_request_summary = body_contents.get('outputs', [])[0].get('text', '')
    pull_request_summary_lines = split_string(pull_request_summary)
    pull_request.edit(body='\n'.join(pull_request_summary_lines))

    return "done"

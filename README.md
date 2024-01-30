Smylee Dev Workflows
====================

Use with a GitHub and Slack App to process events and notifications.

![Workflow](images/Main.png)

Prerequisites
=============

- GitHub account
    - Create GitHub App
    - Copy the GitHub App Id and save it to the secrets directory naming it `github_app_id`.
    - Run the command below to add the id to the AWS Parameter Store.
      ```
      aws ssm put-parameter \
        --name '/SmyleeDevWorkflows/GitHubApp/Id' \
        --description 'GitHub App Id used to sign access token requests' \
        --type String \
        --value file://secrets/github_app_id
      ```
    - Create a new private key and save it to the secrets directory naming it `github_app_pk.pem`.
    - Run the command below to add the GitHub private key to the AWS Parameter Store using the KMS Key id ARN in environment variables.
      ```
      aws ssm put-parameter \
        --name '/SmyleeDevWorkflows/GitHubApp/PrivateKey' \
        --description 'GitHub App private key used to sign access token requests' \
        --type SecureString \
        --key-id $KMS_KEY_ID_ARN \
        --value file://secrets/github_app_pk.pem
      ```
    - Run the command below to add the GitHub webhook secret to the AWS Parameter Store using the KMS Key id ARN in environment variables.
      ```
      aws ssm put-parameter \
        --name '/SmyleeDevWorkflows/GitHubApp/WebhookSecret' \
        --description 'GitHub App webhook secert used to verify payload sha' \
        --type SecureString \
        --key-id $KMS_KEY_ID_ARN \
        --value file://secrets/github_webhook_secret
      ```
- Slack account
# TODO add to secrets manager
- AWS account

> Note: Elevated access is required in all accounts.

Tools/Dependencies
==================

- Python 3.11
- Docker

Setup Steps
===========

## Dev Setup

install `requirements-dev.txt`

automatically run python script on save
```bash
watchmedo shell-command \
 --patterns="*.py" \
 --command='python "${watch_src_path}"' \
 .
```

put the python venv in user path
```bash
export PATH=/Users/Path/To/SmyleeDevWorkflows/.venv/bin/:$PATH
```

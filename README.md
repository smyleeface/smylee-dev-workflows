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
        --description "GitHub App Id used to sign access token requests" \
        --type String \
        --value file://secrets/github_app_id
      ```
    - Create a new private key and save it to the secrets directory naming it `github_app_pk.pem`.
    - Run the command below to add the secret to the AWS Secrets Manager.
      ```
      aws secretsmanager create-secret \
        --name '/SmyleeDevWorkflows/GitHubApp/PrivateKey' \
        --description "GitHub App private key used to sign access token requests" \
        --secret-string file://secrets/github_app_pk.pem
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

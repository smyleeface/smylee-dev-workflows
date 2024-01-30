#!/bin/bash

set -e

source ../secrets/env_var

BUILD_DATA_PATH=build_data
BUILD_ID=$(cat $BUILD_DATA_PATH/build_id)
ARTIFACTS=$(cat $BUILD_DATA_PATH/build_artifacts)
SHA=$(git rev-parse --short $(git rev-parse HEAD))
REPO_NAME=$(basename $(git rev-parse --show-toplevel))
S3_BUCKET=$(aws cloudformation list-exports --query "Exports[?Name=='S3::BucketForUploadsUsWest2-Name'].Value" --output text)
DISPATCHER_FUNCTION_ZIP_FILENAME=$(echo $ARTIFACTS | jq -r '.dispatcher_application')
DISPATCHER_FUNCTION_S3_ZIP_PATH="$REPO_NAME/${DISPATCHER_FUNCTION_ZIP_FILENAME}"
TEMPLATE_FILE="$BUILD_DATA_PATH/cloudformation.yaml"

# create cloudformation.yaml
python main.py $TEMPLATE_FILE

aws cloudformation deploy \
  --stack-name SmyleeDevWorkflows \
  --template-file ./$TEMPLATE_FILE \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameter-overrides DispatcherFunctionS3ZipPath=$DISPATCHER_FUNCTION_S3_ZIP_PATH \
                        BucketForUploadsUsWest2=$S3_BUCKET

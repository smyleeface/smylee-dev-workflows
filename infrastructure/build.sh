#!/bin/bash

set -e

source ../secrets/env_var

REPO_ROOT=$(git rev-parse --show-toplevel)
BUILD_DATA_PATH=${REPO_ROOT}/infrastructure/build_data
BUILD_ARTIFACTS=${REPO_ROOT}/infrastructure/build_artifacts
UUID=$(uuidgen)
BUILD_ID=${UUID##*-}
SHA=$(git rev-parse --short $(git rev-parse HEAD))
REPO_NAME=$(basename $(git rev-parse --show-toplevel))
S3_BUCKET=$(aws cloudformation list-exports --query "Exports[?Name=='S3::BucketForUploadsUsWest2-Name'].Value" --output text)
DISPATCHER_FUNCTION_ZIP_FILENAME="dispatcher_application-${SHA}-${BUILD_ID}.zip"

echo "############ BUILD_ID: ${BUILD_ID}"
echo "############ DISPATCHER_FUNCTION_ZIP_FILENAME: ${DISPATCHER_FUNCTION_ZIP_FILENAME}"

# Ensure the build directory exists
mkdir -p build_artifacts/dispatcher

cd ${REPO_ROOT}/functions/dispatcher/

# Install the Python dependencies from requirements.txt into the build directory
pip install --platform manylinux2014_x86_64 --only-binary=:all: --target ${BUILD_ARTIFACTS}/dispatcher -r requirements.txt

## Copy application code to directory
cp -r dev_workflow ${BUILD_ARTIFACTS}/dispatcher

## Change to the build directory
cd ${BUILD_ARTIFACTS}/dispatcher

## Create a ZIP file with the installed dependencies
find . -type d -name "__pycache__" -prune -o -type f -print | zip -r ${BUILD_ARTIFACTS}/${DISPATCHER_FUNCTION_ZIP_FILENAME} -@
#
## Change back to the project's root
cd ${REPO_ROOT}
#
## Upload the ZIP file to S3
S3_FULL_PATH="$S3_BUCKET/$REPO_NAME/${DISPATCHER_FUNCTION_ZIP_FILENAME}"
echo "############ Uploading ${DISPATCHER_FUNCTION_ZIP_FILENAME} to s3://$S3_FULL_PATH"
aws s3 cp ${BUILD_ARTIFACTS}/${DISPATCHER_FUNCTION_ZIP_FILENAME} s3://$S3_FULL_PATH

echo ${BUILD_ID} > ${BUILD_DATA_PATH}/build_id
BUILD_ARTIFACTS="{ \"dispatcher_application\": \"${DISPATCHER_FUNCTION_ZIP_FILENAME}\" }"
echo ${BUILD_ARTIFACTS} | jq > ${BUILD_DATA_PATH}/build_manifest

# # Clean up the build directory if needed
# rm -r ../smylee_dev_workflows/functions/pull_request__open/build
#!/bin/bash

set -e

TEMPLATE_FILE="cloudformation.yaml"

# create cloudformation.yaml
python main.py $TEMPLATE_FILE

aws cloudformation deploy \
  --stack-name SmyleeDevWorkflows \
  --template-file ./$TEMPLATE_FILE \
  --capabilities CAPABILITY_NAMED_IAM

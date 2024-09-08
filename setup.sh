#!/bin/bash

# Run all setup scripts from the bin folder
# These scripts should be run in order
echo "Running S3 setup..."
bash ./bin/s3_setup.sh

echo "Running DynamoDB setup..."
bash ./bin/dynamodb_setup.sh

echo "Running SQS setup..."
bash ./bin/sqs_setup.sh

echo "Running Lambda setup..."
bash ./bin/lambda_setup.sh

echo "Running API Gateway setup..."
bash ./bin/api_gateway_setup.sh

echo "Full setup completed!"

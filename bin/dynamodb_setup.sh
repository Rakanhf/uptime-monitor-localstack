#!/bin/bash

echo "Creating DynamoDB table..."
awslocal dynamodb create-table \
    --table-name Websites \
    --attribute-definitions \
        AttributeName=Url,AttributeType=S \
    --key-schema \
        AttributeName=Url,KeyType=HASH \
    --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5
echo "DynamoDB table created: Websites"

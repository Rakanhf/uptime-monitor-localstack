#!/bin/bash

echo "Creating SQS queue for website ping tasks..."
awslocal sqs create-queue --queue-name websitePingQueue
echo "SQS queue 'websitePingQueue' created"

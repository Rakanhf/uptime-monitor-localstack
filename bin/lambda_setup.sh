#!/bin/bash

# Set up Lambda for getting websites
(cd lambdas/get; rm -f lambda.zip; zip lambda.zip handler.py)
echo "Creating Lambda function for getting websites..."
awslocal lambda create-function \
    --function-name getWebsites \
    --runtime python3.8 \
    --zip-file fileb://lambdas/get/lambda.zip \
    --handler handler.lambda_handler \
    --role arn:aws:iam::000000000000:role/lambda-role
echo "Lambda function created: getWebsites"

# Set up Lambda for adding websites
(cd lambdas/add; rm -f lambda.zip; zip lambda.zip handler.py)
echo "Creating Lambda function for adding websites..."
awslocal lambda create-function \
    --function-name addWebsite \
    --runtime python3.8 \
    --zip-file fileb://lambdas/add/lambda.zip \
    --handler handler.lambda_handler \
    --role arn:aws:iam::000000000000:role/lambda-role
echo "Lambda function created: addWebsite"

# Set up Lambda for removing websites
(cd lambdas/remove; rm -f lambda.zip; zip lambda.zip handler.py)
echo "Creating Lambda function for removing websites..."
awslocal lambda create-function \
    --function-name removeWebsite \
    --runtime python3.8 \
    --zip-file fileb://lambdas/remove/lambda.zip \
    --handler handler.lambda_handler \
    --role arn:aws:iam::000000000000:role/lambda-role
echo "Lambda function created: removeWebsite"

# Set up Lambda for scheduling website checks
(cd lambdas/scheduler; rm -f lambda.zip; zip lambda.zip handler.py)
echo "Creating Lambda function for scheduling website checks..."
awslocal lambda create-function \
    --function-name schedulerLambda \
    --runtime python3.8 \
    --zip-file fileb://lambdas/scheduler/lambda.zip \
    --handler handler.lambda_handler \
    --role arn:aws:iam::000000000000:role/lambda-role
echo "Lambda function created: schedulerLambda"


# Create Worker Lambda for processing websites
echo "Creating Lambda function for processing websites for processing websites..."
os=$(uname -s)
if [ "$os" == "Darwin" ]; then
    (
        cd lambdas/worker
        rm -rf libs lambda.zip
        docker run --platform linux/x86_64 --rm -v "$PWD":/var/task "public.ecr.aws/sam/build-python3.11" /bin/sh -c "pip3 install -r requirements.txt -t libs; exit"

        cd libs && zip -r ../lambda.zip . && cd ..
        zip lambda.zip handler.py
        rm -rf libs
    )
else
    (
        cd lambdas/worker
        rm -rf package lambda.zip
        mkdir package
        pip3 install -r requirements.txt --platform manylinux2014_x86_64 --only-binary=:all: -t package
        zip lambda.zip handler.py
        cd package
        zip -r ../lambda.zip *;
    )
fi

awslocal lambda create-function \
    --function-name workerLambda \
    --runtime python3.8 \
    --zip-file fileb://lambdas/worker/lambda.zip \
    --handler handler.lambda_handler \
    --role arn:aws:iam::000000000000:role/lambda-role
echo "Lambda function created: workerLambda"

# Set up EventBridge rule for scheduling
awdlocal events put-rule \
    --name "FiveMinuteRule" \
    --schedule-expression "rate(5 minutes)"

# Set up EventBridge target for scheduling
awslocal events put-targets \
    --rule "FiveMinuteRule" \
    --targets "Id"="1","Arn"="arn:aws:lambda:eu-central-1:000000000000:function:schedulerLambda"

# Add SQS trigger to Worker Lambda
echo "Adding SQS trigger to Worker Lambda..."
awslocal lambda create-event-source-mapping \
    --function-name workerLambda \
    --batch-size 10 \
    --event-source-arn arn:aws:sqs:eu-central-1:000000000000:websitePingQueue
echo "SQS trigger added to Worker Lambda"
#!/bin/bash

export REST_API_ID="uptime"  # Set your fixed API ID

echo "Creating API Gateway with fixed REST_API_ID..."
awslocal apigateway create-rest-api --name "WebsiteAPI" --tags '{"_custom_id_":"uptime"}'
echo "API Gateway created with REST_API_ID: $REST_API_ID"

# Export Parent and Resource IDs
export PARENT_RESOURCE_ID=$(awslocal apigateway get-resources --rest-api-id $REST_API_ID --query 'items[0].id' --output text)
export RESOURCE_ID=$(awslocal apigateway create-resource --rest-api-id $REST_API_ID --parent-id $PARENT_RESOURCE_ID --path-part website --query 'id' --output text)

# Add POST Method to API Gateway
echo "Adding POST method to API Gateway..."
awslocal apigateway put-method \
    --rest-api-id $REST_API_ID \
    --resource-id $RESOURCE_ID \
    --http-method POST \
    --authorization-type "NONE"

# Add GET Method to API Gateway
echo "Adding GET method to API Gateway..."
awslocal apigateway put-method \
    --rest-api-id $REST_API_ID \
    --resource-id $RESOURCE_ID \
    --http-method GET \
    --authorization-type "NONE"

# Add DELETE Method to API Gateway
echo "Adding DELETE method to API Gateway..."
awslocal apigateway put-method \
    --rest-api-id $REST_API_ID \
    --resource-id $RESOURCE_ID \
    --http-method DELETE \
    --authorization-type "NONE"

# Integrate GET Lambda
echo "Integrating Lambda with API Gateway for GET..."
awslocal apigateway put-integration \
    --rest-api-id $REST_API_ID \
    --resource-id $RESOURCE_ID \
    --http-method GET \
    --type AWS_PROXY \
    --integration-http-method POST \
    --uri arn:aws:apigateway:eu-central-1:lambda:path/2015-03-31/functions/arn:aws:lambda:eu-central-1:000000000000:function:getWebsites/invocations

# Integrate POST Lambda
echo "Integrating Lambda with API Gateway for POST..."
awslocal apigateway put-integration \
    --rest-api-id $REST_API_ID \
    --resource-id $RESOURCE_ID \
    --http-method POST \
    --type AWS_PROXY \
    --integration-http-method POST \
    --uri arn:aws:apigateway:eu-central-1:lambda:path/2015-03-31/functions/arn:aws:lambda:eu-central-1:000000000000:function:addWebsite/invocations

# Integrate DELETE Lambda
echo "Integrating Lambda with API Gateway for DELETE..."
awslocal apigateway put-integration \
    --rest-api-id $REST_API_ID \
    --resource-id $RESOURCE_ID \
    --http-method DELETE \
    --type AWS_PROXY \
    --integration-http-method POST \
    --uri arn:aws:apigateway:eu-central-1:lambda:path/2015-03-31/functions/arn:aws:lambda:eu-central-1:000000000000:function:removeWebsite/invocations

# Deploy API Gateway
echo "Deploying API Gateway..."
awslocal apigateway create-deployment --rest-api-id $REST_API_ID --stage-name dev

# Output fixed API URL and S3 URL
API_URL="http://$REST_API_ID.execute-api.localhost.localstack.cloud:4566/dev/website"
S3_URL="https://my-static-site.s3-website.localhost.localstack.cloud:4566/"
echo "Fixed API URL: $API_URL"
echo "S3 Static Website is available at: $S3_URL"

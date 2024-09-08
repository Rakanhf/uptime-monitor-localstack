#!/bin/bash

echo "Creating S3 bucket..."
awslocal s3 mb s3://my-static-site
echo "S3 bucket created: my-static-site"

echo "Uploading website to S3..."
awslocal s3 sync --delete ./website s3://my-static-site
echo "Website uploaded to S3"

echo "Configuring static website hosting..."
awslocal s3 website s3://my-static-site --index-document index.html
echo "S3 static website configured"

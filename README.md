# Uptime Monitor using LocalStack Demo

| Key          | Value                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
|--------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Services     | S3, API Gateway, Lambda, SQS, Dynamodb, EventBridge                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| Integrations | AWS SDK, AWS CLI                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| Categories   | Serverless, Scheduler Lambda, Worker Lambda, Lambda function URLs, LocalStack developer endpoints, queues JavaScript, Python, htmx                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| Level        | Beginner   


This project demonstrates a simple uptime monitor service using AWS services emulated by LocalStack. The service allows users to add, remove, and monitor the uptime of websites. The system regularly checks the availability of the websites and stores the results in DynamoDB, providing a simple frontend hosted on S3 for interaction.

## Overview
The project architecture consists of several AWS services, emulated locally using LocalStack:

1. **DynamoDB**: Stores URLs and their statuses (UP/DOWN).
2. **SQS** (Simple Queue Service): Queues requests to check website statuses.
3. **AWS Lambda**:
* Uptime Scheduler: Periodically triggers checks for all registered websites.
* **Uptime Worker**: Processes SQS messages and pings websites to determine their status.
* **API Lambdas**: Provide the ability to add, remove, and retrieve URLs via an API.
4. **API Gateway**: Exposes the API to interact with the URLs (add, remove, retrieve) through HTTP requests.
5. **S3**: Hosts the frontend dashboard that interacts with the API to manage URLs.
----
Here's the web application in action:

[uptime-monitor-using-LocalStack-demo.webm](https://github.com/user-attachments/assets/7c8ce596-032a-4a3a-94c3-fed7df368e38)

This project runs entirely in your local environment, using LocalStack to simulate AWS services.

## Architecture
The system works as follows:

1. **Frontend** (hosted on **S3**) allows users to add, remove, and view the status of websites.
2. **API Gateway** routes requests from the frontend to the Lambda functions.
3. **DynamoDB** stores URLs, their statuses, and the last checked timestamp.
4. **Scheduler Lambda** triggers every minute to scan the URLs stored in DynamoDB and sends each URL to an SQS queue.
5. **Worker Lambda** listens to the SQS queue, pings each URL, and updates its status in DynamoDB.

## Getting Started
### **Prerequisites:**
1. **Docker**: Install Docker from [here](https://docs.docker.com/get-docker/).
2. **LocalStack**: Install LocalStack using the instructions [here](https://docs.localstack.cloud/getting-started/installation/).
3. **AWS CLI**: Install the AWS CLI from [here](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html).
4. Python 3.8+ installed locally for running the Lambda functions.

## Installation

1. Clone the repository:

```bash
git clone git@github.com:Rakanhf/uptime-monitor-localstack.git
cd uptime-monitor-localstack
```

Create a virtualenv and install all the development dependencies there:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

#### LocalStack

Start LocalStack Pro with the appropriate CORS configuration for the S3 Website:

```bash
LOCALSTACK_AUTH_TOKEN=... localstack start
```

Set up AWS services (S3, DynamoDB, SQS, API Gateway, Lambda) in LocalStack:
    
```bash
bash setup.sh
```

This script will:

* Create a DynamoDB table for storing URLs.
* Create an SQS queue for website checks.
* Deploy Lambda functions (Scheduler, Worker, API handlers).
* Set up API Gateway to expose the API.
* Upload the frontend to an S3 bucket and configure it for static website hosting.

#### Frontend
```bash
http://my-static-site.s3-website.localhost.localstack.cloud:4566/
```


### References
- [LocalStack Docs](https://docs.localstack.cloud/)
- [sample-serverless-image-resizer-s3-lambda](https://github.com/localstack-samples/sample-serverless-image-resizer-s3-lambda/tree/main)

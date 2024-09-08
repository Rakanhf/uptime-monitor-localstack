import boto3
import math
from typing import Any, Dict, List

# SQS client
sqs = boto3.client("sqs")
queue_url = "http://localhost:4566/000000000000/websitePingQueue"

# DynamoDB client
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("Websites")  # Replace with your DynamoDB table name


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler function that fetches websites from DynamoDB, batches them, and sends them to an SQS queue.

    :param event: The Lambda event data (not used here).
    :param context: Lambda context object (not used here).
    :return: A dictionary containing the status code and response body.
    """
    try:
        # Fetch all websites from DynamoDB
        websites = fetch_websites_from_dynamodb()

        # Batch size for SQS messages
        batch_size = 10

        # Send websites in batches to SQS
        send_websites_in_batches(websites, batch_size)

        return {"statusCode": 200, "body": "Websites have been batched and sent to SQS"}

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return {"statusCode": 500, "body": f"An error occurred: {str(e)}"}


def fetch_websites_from_dynamodb() -> List[Dict[str, Any]]:
    """
    Fetch all websites from the DynamoDB table.

    :return: A list of website items from the DynamoDB table.
    """
    response = table.scan()
    return response.get("Items", [])


def send_websites_in_batches(websites: List[Dict[str, Any]], batch_size: int) -> None:
    """
    Send websites in batches to an SQS queue.

    :param websites: A list of website items to send to the SQS queue.
    :param batch_size: The number of websites to send in each batch.
    """
    num_batches = math.ceil(len(websites) / batch_size)

    for i in range(num_batches):
        # Get the current batch of websites
        batch = websites[i * batch_size : (i + 1) * batch_size]

        # Prepare SQS entries
        entries = [
            {"Id": str(idx), "MessageBody": website["Url"]}
            for idx, website in enumerate(batch)
        ]

        # Send the batch to the SQS queue
        response = sqs.send_message_batch(QueueUrl=queue_url, Entries=entries)

        if "Failed" in response:
            print(f"Failed to send some messages: {response['Failed']}")

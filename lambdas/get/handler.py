import json
import boto3
import logging
from typing import Dict, Any, List

# Initialize the logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# DynamoDB resource
dynamodb = boto3.resource(
    "dynamodb",
    region_name="eu-central-1",
    endpoint_url="https://localhost.localstack.cloud:4566",
)


def create_response(status_code: int, body: Dict[str, Any]) -> Dict[str, Any]:
    """
    Helper function to create standardized HTTP responses.

    :param status_code: HTTP status code to return (e.g., 200, 500).
    :param body: Dictionary containing the response body.
    :return: A dictionary representing an HTTP response.
    """
    return {
        "statusCode": status_code,
        "headers": {
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
        },
        "body": json.dumps(body),
    }


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler function to list all URLs from the DynamoDB Websites table.

    :param event: The Lambda event data (not used here).
    :param context: Lambda context object (not used here).
    :return: A standardized HTTP response containing the list of websites.
    """
    try:
        logger.info("Event received: %s", event)

        # Access the DynamoDB table
        table = dynamodb.Table("Websites")

        # Scan the table to get all items (websites)
        websites = scan_dynamodb_table(table)

        return create_response(200, {"websites": websites})

    except Exception as e:
        logger.error("Error: %s", str(e))
        return create_response(500, {"error": "Internal server error"})


def scan_dynamodb_table(table: Any) -> List[Dict[str, Any]]:
    """
    Scan the DynamoDB table to retrieve all items (websites).

    :param table: The DynamoDB table object.
    :return: A list of items from the table.
    """
    response = table.scan()
    items = response.get("Items", [])

    logger.info(f"Fetched {len(items)} websites from the DynamoDB table.")
    return items

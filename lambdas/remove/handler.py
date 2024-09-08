import json
import boto3
import logging
from typing import Dict, Any

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

    :param status_code: HTTP status code to return (e.g., 200, 404).
    :param body: Dictionary containing the response body.
    :return: A dictionary representing an HTTP response.
    """
    return {
        "statusCode": status_code,
        "headers": {
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "OPTIONS,POST,DELETE",
        },
        "body": json.dumps(body),
    }


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler function that deletes a URL from the DynamoDB Websites table.

    :param event: The Lambda event data.
    :param context: Lambda context object (not used here).
    :return: A standardized HTTP response.
    """
    try:
        logger.info("Event received: %s", event)

        table = dynamodb.Table("Websites")

        # Extract the URL to be deleted from the query string parameters
        url = event.get("queryStringParameters", {}).get("url")

        if not url:
            logger.warning("No URL provided in the request")
            return create_response(400, {"error": "URL is required!"})

        # Delete the URL from DynamoDB
        try:
            table.delete_item(
                Key={"Url": url},
                ConditionExpression="attribute_exists(#url)",  # Ensure the item exists before deleting
                ExpressionAttributeNames={
                    "#url": "Url"
                },  # Escape reserved keyword 'Url'
            )
            logger.info("Successfully deleted URL from DynamoDB: %s", url)
            return create_response(200, {"message": f"URL {url} deleted successfully"})

        except dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
            logger.error("URL not found: %s", url)
            return create_response(404, {"error": "URL not found!"})

    except Exception as e:
        logger.error("Unexpected error: %s", str(e))
        return create_response(500, {"error": "Internal server error"})

import json
import boto3
import logging
import re
from boto3.dynamodb.conditions import Attr
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

# Regular expression for URL validation
URL_REGEX = re.compile(
    r"^(https?:\/\/)?"  # http:// or https:// (optional)
    r"([a-zA-Z0-9\-]+\.)+[a-zA-Z]{2,}"  # domain name
    r"(\/[a-zA-Z0-9\-._~:\/?#\[\]@!$&\'()*+,;=]*)?$"  # URL path (optional)
)


def validate_url(url: str) -> None:
    """
    Validate the provided URL against a regular expression.

    :param url: The URL to validate.
    :raises ValueError: If the URL is not in a valid format.
    """
    if not URL_REGEX.match(url):
        raise ValueError(f"Invalid URL format: {url}")


def create_response(status_code: int, body: Dict[str, Any]) -> Dict[str, Any]:
    """
    Helper function to create standardized HTTP responses.

    :param status_code: The HTTP status code for the response.
    :param body: The body of the response.
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
    Main AWS Lambda handler for adding URLs to DynamoDB.

    This function extracts the URL from the event body, validates it,
    and adds it to the DynamoDB 'Websites' table with a conditional check
    to avoid duplicates.

    :param event: The Lambda event containing the HTTP request.
    :param context: Lambda context object (not used here).
    :return: A standardized HTTP response.
    """
    try:
        logger.info("Event received: %s", event)

        table = dynamodb.Table("Websites")

        # Extract and validate URL from the request body
        body = json.loads(event.get("body", "{}"))
        url = body.get("url")

        if not url:
            logger.warning("URL is missing in the request")
            return create_response(400, {"error": "URL is required!"})

        try:
            validate_url(url)
        except ValueError as ve:
            logger.error("URL validation error: %s", ve)
            return create_response(400, {"error": str(ve)})

        logger.info("Adding URL to DynamoDB: %s", url)

        # Add URL to DynamoDB with a conditional check to avoid duplicates
        try:
            table.put_item(
                Item={"Url": url, "Status": "UNKNOWN", "LastChecked": "NEVER"},
                ConditionExpression=Attr("Url").not_exists(),
            )
        except dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
            logger.error("URL already exists: %s", url)
            return create_response(400, {"error": "URL already exists!"})

        logger.info("Successfully added URL to DynamoDB")
        return create_response(200, {"message": f"{url} added successfully"})

    except json.JSONDecodeError:
        logger.error("Invalid JSON input")
        return create_response(400, {"error": "Invalid JSON input"})

    except Exception as e:
        logger.error("Unexpected error: %s", str(e))
        return create_response(500, {"error": "Internal server error"})

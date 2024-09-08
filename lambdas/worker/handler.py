import re
import requests
import boto3
from datetime import datetime, timezone
from typing import Any, Dict

# DynamoDB client
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("Websites")  # Replace with your DynamoDB table name

# Regular expression for URL validation
URL_REGEX = re.compile(
    r"^(https?:\/\/)?"  # http:// or https:// (optional)
    r"([a-zA-Z0-9\-]+\.)+[a-zA-Z]{2,}"  # domain name
    r"(\/[a-zA-Z0-9\-._~:\/?#\[\]@!$&\'()*+,;=]*)?$"  # URL path (optional)
)


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler function that processes messages from SQS and checks the status of websites.

    :param event: The Lambda event data (SQS messages).
    :param context: Lambda context object (not used here).
    :return: A dictionary containing the status code and response body.
    """
    if "Records" not in event:
        return {"statusCode": 400, "body": "No websites to check"}

    for record in event["Records"]:
        original_url = record["body"]

        try:
            # Validate and format the URL
            formatted_url = validate_and_format_url(original_url)

            # Ping the website and determine its status
            status = check_website_status(formatted_url)

            # Update the status in DynamoDB with the original URL
            update_website_status(original_url, status)

        except ValueError as e:
            print(f"Error processing URL: {e}")
            continue  # Skip invalid URLs

    return {"statusCode": 200, "body": "Website status updated"}


def validate_and_format_url(url: str) -> str:
    """
    Validate and format the URL. If no scheme is provided, prepend 'http://'.

    :param url: The URL to validate and format.
    :return: A properly formatted URL with scheme.
    :raises ValueError: If the URL is not in a valid format.
    """
    if not URL_REGEX.match(url):
        raise ValueError(f"Invalid URL format: {url}")

    # Add http:// if the URL has no scheme
    if not url.startswith(("http://", "https://")):
        url = "http://" + url

    return url


def check_website_status(url: str) -> str:
    """
    Ping the website and check its status.

    :param url: The website URL to check (must be formatted).
    :return: 'UP' if the website is reachable, otherwise 'DOWN'.
    """
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return "UP"
        else:
            return "DOWN"
    except requests.RequestException:
        return "DOWN"


def update_website_status(url: str, status: str) -> None:
    """
    Update the website's status and last checked time in DynamoDB.

    :param url: The original URL of the website (unformatted).
    :param status: The status of the website ('UP' or 'DOWN').
    """
    table.update_item(
        Key={"Url": url},
        UpdateExpression="SET #status = :s, LastChecked = :lc",
        ExpressionAttributeNames={"#status": "Status"},
        ExpressionAttributeValues={
            ":s": status,
            ":lc": datetime.now(timezone.utc).isoformat(),
        },
    )

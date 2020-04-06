import json
import gzip
import base64
import logging
import urllib3
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)

http = urllib3.PoolManager()


def lambda_handler(event, context):
    # Process cloudwatch event logs
    cloudwatch_event = event["awslogs"]["data"]
    decoded = base64.b64decode(cloudwatch_event)
    decompressed = gzip.decompress(decoded)
    data = json.loads(decompressed)

    # Get sources of attack
    sources = []
    log_events = data["logEvents"]
    for log_event in log_events:
        message = log_event["message"]
        if "FATAL:  password authentication failed for user" in message:
            tok = message.split(" ")[2]
            source = tok.split(":")[1]
            sources.append(source)

    # Log to cloudwatch
    print(sources)

    # Send data to slack channel
    message = "IN-AUR-01 Failed login attempts detected! Sources:\n" + "".join(
        [source + "\n" for source in sources]
    )
    webhook_url = os.environ["webhook_url"]
    slack_message = {"channel": "ir-cdk-stacks", "text": message}
    encoded_data = json.dumps(slack_message).encode("utf-8")
    response = http.request(
        "POST",
        webhook_url,
        body=encoded_data,
        headers={"Content-Type": "application/json"},
    )

    # Handle errors
    if response.status == 200:
        print(f"Successfully sent to channel {slack_message['channel']}")
    else:
        print(
            f"Failed to send to Slack channel {slack_message['channel']}. Error: {response.status} - {response.data}."
        )
    return {"statusCode": 200, "body": slack_message}

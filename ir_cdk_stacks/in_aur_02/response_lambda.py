import os
import boto3
import json
import urllib3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

http = urllib3.PoolManager()

iam = boto3.client("iam")


def lambda_handler(event, context):
    detail = event["detail"]
    message = "IN-AUR-02 RDS API calls detected!\n"

    if (
        "responseElements" in detail
        and "dBClusterIdentifier" in detail["responseElements"]
        and detail["responseElements"]["dBClusterIdentifier"]
        == os.environ["cluster_name"]
    ):
        message += f"User ARN: {detail['userIdentity']['arn']}\n"
        message += f"Action: {detail['eventName']}\n"
        message += f"IP: {detail['sourceIPAddress']}\n"
        if "dBInstanceIdentifier" in detail["responseElements"]:
            message += f"Target instance: {detail['responseElements']['dBInstanceIdentifier']}\n"
        print(message)

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
            logger.info(f"Successfully sent to channel {slack_message['channel']}")
        else:
            logger.error(
                f"Failed to send to Slack channel {slack_message['channel']}.\n\
                Error: {response.status} - {response.data}"
            )

        # Check if user is in white list group
        try:
            group = iam.get_group(GroupName=os.environ["white_list_group"])
            users = [user["UserName"] for user in group["Users"]]
            username = detail["userIdentity"]["userName"]
            if username not in users:
                try:
                    iam.attach_user_policy(
                        PolicyArn=os.environ["policy_arn"], UserName=username
                    )
                    logger.info(
                        f"Successfully attached explicit deny policy to user {username}"
                    )
                except Exception as e:
                    logger.error(
                        f"Failed to attach explicit deny policy to user {username}.\n\
                        Error: {e}"
                    )
        except Exception:
            logger.error(
                f"Failed to get IAM group {os.environ['white_list_group']}.\n\
                Error: {e}"
            )

    return {"statusCode": 200, "body": message}

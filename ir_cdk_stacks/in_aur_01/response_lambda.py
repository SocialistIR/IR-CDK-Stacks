import json
import gzip
import base64
import logging
import urllib3
import os
import boto3

waf = boto3.client("wafv2")
sfn = boto3.client("stepfunctions")

logger = logging.getLogger()
logger.setLevel(logging.INFO)

http = urllib3.PoolManager()


def lambda_handler(event, context):
    # Process cloudwatch event logs
    cloudwatch_event = event["awslogs"]["data"]
    print(cloudwatch_event)
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
    attack_sources = [source + "\n" for source in sources[-10:]]
    message = "IN-AUR-01 Failed login attempts detected! Sources:\n" + "".join(
        attack_sources
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

    # Put source IP to blacklist in WAF
    blacklist = waf.get_ip_set(
        Name=os.environ["waf_name"],
        Scope=os.environ["waf_scope"],
        Id=os.environ["waf_id"],
    )
    ipset = set(blacklist["IPSet"]["Addresses"])
    for source in attack_sources:
        source_ip = source.split("(")
        if source_ip:
            ipset.add(source_ip + "/32")
    new_ips = ipset.difference(set(blacklist["IPSet"]["Addresses"]))

    # Ban IP temporarily using stepfunction
    if len(new_ips) > 0:
        response = waf.update_ip_set(
            Name=blacklist["IPSet"]["Name"],
            Scope=os.environ["waf_scope"],
            Id=blacklist["IPSet"]["Id"],
            Addresses=list(ipset),
            LockToken=blacklist["LockToken"],
        )

        jips = {"ips": list(new_ips)}
        response = sfn.start_execution(
            stateMachineArn=os.environ["unban_sm_arn"], input=json.dumps(jips),
        )

    return {"statusCode": 200, "body": slack_message}

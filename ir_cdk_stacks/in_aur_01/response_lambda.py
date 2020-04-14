import json
import logging
import urllib3
import os
import boto3
import random
import datetime

NACL_RULE_NUMBER_MAX = 32766

waf = boto3.client("wafv2")
sfn = boto3.client("stepfunctions")
rds = boto3.client("rds")
clw = boto3.client("cloudwatch")
logs = boto3.client("logs")
ec2 = boto3.client("ec2")
ec2_resource = boto3.resource("ec2")

logger = logging.getLogger()
logger.setLevel(logging.INFO)

http = urllib3.PoolManager()


def lambda_handler(event, context):
    # Get logs from SNS topic's Alarm
    message = json.loads(event["Records"][0]["Sns"]["Message"])

    # Get metric filters
    metric_filters = []
    try:
        metric_filters = logs.describe_metric_filters(
            metricName=message["Trigger"]["MetricName"],
            metricNamespace=message["Trigger"]["Namespace"],
        )
    except Exception as e:
        logger.error(f"Failed to get metric filters from SNS.\t{e}")

    # Get logs from Alarm's evaluation period
    timestamp = int(
        datetime.datetime.strptime(
            message["StateChangeTime"], "%Y-%m-%dT%H:%M:%S.%f%z"
        ).timestamp()
        * 1000
    )
    offset = (
        message["Trigger"]["Period"] * message["Trigger"]["EvaluationPeriods"] * 1000
    )
    metric_filter = metric_filters["metricFilters"][0]

    log_events = []
    try:
        log_events = logs.filter_log_events(
            logGroupName=metric_filter["logGroupName"],
            filterPattern=metric_filter["filterPattern"],
            startTime=(timestamp - offset),
            endTime=timestamp,
        )
    except Exception as e:
        logger.error(f"Failed to get log events.\t{e}")

    # Get unique sources of attack
    sources = set()
    log_events = log_events["events"]
    for log_event in log_events:
        message = log_event["message"]
        if "FATAL:  password authentication failed for user" in message:
            tok = message.split(" ")[2]
            source = tok.split(":")[1]
            source_ip = source.split("(")[0]
            sources.add(source_ip)
    logger.info(f"Attack sources found: {sources}")

    # Send data to slack channel
    attack_sources = [source + "\n" for source in sources]
    attack_sources = set(attack_sources)
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
        logger.info(f"Successfully sent to channel {slack_message['channel']}")
    else:
        logger.error(
            f"Failed to send to Slack channel {slack_message['channel']}.\n\
            Error: {response.status} - {response.data}"
        )

    # Put source IP to blacklist in WAF
    blacklist = waf.get_ip_set(
        Name=os.environ["waf_name"],
        Scope=os.environ["waf_scope"],
        Id=os.environ["waf_id"],
    )
    ipset = set(blacklist["IPSet"]["Addresses"])
    for source in sources:
        ipset.add(source + "/32")
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

        # Handle errors
        if response["NextLockToken"]:
            logger.info(f"Successfully added IPs {sources} to WAF IPSet")
        else:
            logger.error(f"Failed to add IPs to WAF IPSet")

    # Block IP ingress in Cluster's NACL
    # Find cluster
    clusters = rds.describe_db_clusters(DBClusterIdentifier=os.environ["cluster_name"])
    # Get instances
    instances = clusters["DBClusters"][0]["DBClusterMembers"]
    nacls = []
    for instance in instances:
        instance_id = instance["DBInstanceIdentifier"]
        # Get VPC associated with current instance
        vpc_id = rds.describe_db_instances(DBInstanceIdentifier=instance_id)[
            "DBInstances"
        ][0]["DBSubnetGroup"]["VpcId"]
        vpc = ec2_resource.Vpc(vpc_id)
        # Get all NACLs associated with VPC
        network_acls = list(vpc.network_acls.all())
        # Get first NACL
        network_acl = network_acls[0]
        network_acl_id = network_acl.network_acl_id
        # List all entries in current NACL
        entries = network_acl.entries
        for entry in entries:
            # Find entry that allows all traffic
            if entry["CidrBlock"] == "0.0.0.0/0" and entry["RuleAction"] == "allow":
                entry_rule_number = entry["RuleNumber"]
                logger.info(
                    f"Found allow all traffic entry #{entry_rule_number}. Attempting to remove it."
                )
                try:
                    ec2.delete_network_acl_entry(
                        Egress=False,
                        NetworkAclId=network_acl_id,
                        RuleNumber=entry_rule_number,
                    )
                    logger.info(
                        f"Successfully deleted rule {entry_rule_number} \
                            in Network ACL {network_acl_id}"
                    )
                except Exception as e:
                    logger.error(
                        f"Failed to delete rule {entry_rule_number} \
                            in Network ACL {network_acl_id}\t{e}"
                    )
        rule_numbers = []
        # Create new NACL entries to block IPs
        for source in sources:
            source_cidr = source + "/32"
            # If entry for this IP already exists,
            # remove it from NACL table
            for entry in entries:
                if entry["CidrBlock"] == source_cidr:
                    entry_rule_number = entry["RuleNumber"]
                    logger.info(
                        f"Found entry allowing attack IP {source_cidr} (#{entry_rule_number}).\n\
                        Attempting to remove it."
                    )
                    try:
                        ec2.delete_network_acl_entry(
                            Egress=False,
                            NetworkAclId=network_acl_id,
                            RuleNumber=entry_rule_number,
                        )
                        logger.info(
                            f"Successfully deleted rule {entry_rule_number} \
                                in Network ACL {network_acl_id}"
                        )
                    except Exception as e:
                        logger.error(
                            f"Failed to delete rule {entry_rule_number} \
                                in Network ACL {network_acl_id}\t{e}"
                        )
            # Generate unique rule number from current entries
            nacl_rule_numbers = [e["RuleNumber"] for e in entries]
            next_number = random.choice(
                [x for x in range(NACL_RULE_NUMBER_MAX) if x not in nacl_rule_numbers]
            )
            rule_numbers.append(next_number)
            # Block attack IP
            try:
                network_acl.create_entry(
                    CidrBlock=source_cidr,
                    Egress=False,
                    PortRange={"From": 0, "To": 0},
                    Protocol="-1",
                    RuleAction="deny",
                    RuleNumber=next_number,
                )
                logger.info(
                    f"Successfully blocked ingress IP \
                        {source} (#{next_number}) in Network ACL {network_acl_id}"
                )
            except Exception as e:
                logger.error(
                    f"Failed to block ingress IP {source} \
                        (#{next_number}) in Network ACL {network_acl_id}.\n\
                        Error: {e}"
                )

        # Map to list
        nacls.append({"id": network_acl_id, "rule_numbers": rule_numbers})

        # Execute unban lambda using stepfunction
        jips = {"ips": list(new_ips), "network_acls": nacls}
        try:
            response = sfn.start_execution(
                stateMachineArn=os.environ["unban_sm_arn"], input=json.dumps(jips),
            )
            logger.info(
                f"Successfully executed stepfunction {response['executionArn']}"
            )
        except Exception as e:
            logger.error(
                f"Failed to execute stepfunction {os.environ['unban_sm_arn']}\t\
                {e}"
            )

    return {"statusCode": 200, "body": slack_message}

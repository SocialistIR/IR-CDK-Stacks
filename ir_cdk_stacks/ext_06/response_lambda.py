import json
import boto3
import time
import uuid
import logging
import os

s3 = boto3.client('s3')
waf = boto3.client('wafv2')
sfn = boto3.client('stepfunctions')
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    try:
        doslist = waf.get_ip_set(Name=os.environ['doslist_name'], Scope=os.environ['doslist_scope'], Id=os.environ['doslist_id'])
        logger.info(
            f"Successfully found IPset {os.environ['doslist_name']}, id= {os.environ['doslist_id']}"
        )
    except Exception as e:
        logger.error(
            f"Failed to find IPset {os.environ['ipset_name']}, id= {os.environ['ipset_id']}\n{e}"
        )
    try:
        suslist = waf.get_ip_set(Name=os.environ['suslist_name'], Scope=os.environ['suslist_scope'], Id=os.environ['suslist_id'])
        logger.info(
            f"Successfully found IPset {os.environ['suslist_name']}, id= {os.environ['suslist_id']}"
        )
    except Exception as e:
        logger.error(
            f"Failed to find IPset {os.environ['suslist_name']}, id= {os.environ['suslist_id']}\n{e}"
        )
    sus = set(suslist['IPSet']['Addresses'])
    s = set()

    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        try:
            obj = s3.get_object(Bucket=bucket, Key=key)
            logger.info(
                f"Successfully read from s3 bucket {bucket}"
            )
        except Exception as e:
            logger.error(
                f"Failed to read from s3 bucket {bucket}\n{e}"
            )
        body = obj['Body'].read().decode().split("\n")
        for j in body:
            if j != "":
                jbody = json.loads(j)
                if (jbody['terminatingRuleId'] == "Spam"):
                    ip = jbody['httpRequest']['clientIp']
                    ip = ip + "/32"
                    s.add(ip)

    new_ips = s.difference(set(suslist['IPSet']['Addresses']))
    old_ips = s.intersection(set(suslist['IPSet']['Addresses']))

    if len(new_ips) > 0:
        try:
            response = waf.update_ip_set(
                Name=suslist['IPSet']['Name'],
                Scope='REGIONAL',
                Id=suslist['IPSet']['Id'],
                Addresses=list(s.union(set(suslist['IPSet']['Addresses']))),
                LockToken=suslist['LockToken']
            )
            logger.info(
                f"Successfully updated IPset {suslist['IPSet']['Name']}, id= {suslist['IPSet']['Id']}"
            )
        except Exception as e:
            logger.error(
                f"Failed to update IPset {suslist['IPSet']['Name']}, id= {suslist['IPSet']['Id']}\n{e}"
            )
        
        jips = {"ips": list(new_ips)}
        try:
            response = sfn.start_execution(
                stateMachineArn=os.environ['sus_arn'],
                input=json.dumps(jips)
            )
            logger.info(
                f"Successfully started state machine {os.environ['sus_arn']}"
            )
        except Exception as e:
            logger.error(
                f"Failed to start state machine {os.environ['sus_arn']}\n{e}"
            )

    if len(old_ips) > 0:
        try:
            response = waf.update_ip_set(
                Name=doslist['IPSet']['Name'],
                Scope='REGIONAL',
                Id=doslist['IPSet']['Id'],
                Addresses=list(set(doslist['IPSet']['Addresses']).union(old_ips)),
                LockToken=doslist['LockToken']
            )
            logger.info(
                f"Successfully updated IPset {doslist['IPSet']['Name']}, id= {doslist['IPSet']['Id']}"
            )
        except Exception as e:
            logger.error(
                f"Failed to update IPset {doslist['IPSet']['Name']}, id= {doslist['IPSet']['Id']}\n{e}"
            )

        jips = {"ips": list(old_ips)}
        try:
            response = sfn.start_execution(
                stateMachineArn=os.environ['dos_arn'],
                input=json.dumps(jips)
            )
            logger.info(
                f"Successfully started state machine {os.environ['dos_arn']}"
            )
        except Exception as e:
            logger.error(
                f"Failed to start state machine {os.environ['dos_arn']}\n{e}"
            )
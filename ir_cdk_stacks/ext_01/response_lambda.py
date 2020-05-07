import json
import boto3
import time
import uuid
import os
import logging

s3 = boto3.client('s3')
waf = boto3.client('wafv2')
sfn = boto3.client('stepfunctions')
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    try:
        blacklist = waf.get_ip_set(
            Name=os.environ['ipset_name'], Scope=os.environ['ipset_scope'], Id=os.environ['ipset_id'])
        logger.info(
            f"Successfully found IPset {os.environ['ipset_name']}, id= {os.environ['ipset_id']}"
        )
    except Exception as e:
        logger.error(
            f"Failed to find IPset {os.environ['ipset_name']}, id= {os.environ['ipset_id']}\n{e}"
        )
    ipset = set(blacklist['IPSet']['Addresses'])

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
                if (jbody['terminatingRuleId'] == "XSS"):
                    ip = jbody['httpRequest']['clientIp']
                    ip = ip + "/32"
                    ipset.add(ip)
                elif (jbody['terminatingRuleId'] == "SQLI"):
                    ip = jbody['httpRequest']['clientIp']
                    ip = ip + "/32"
                    ipset.add(ip)
                elif (jbody['terminatingRuleId'] == "LPT"):
                    ip = jbody['httpRequest']['clientIp']
                    ip = ip + "/32"
                    ipset.add(ip)

    new_ips = ipset.difference(set(blacklist['IPSet']['Addresses']))

    if len(new_ips) > 0:
        try:
            response = waf.update_ip_set(
                Name=blacklist['IPSet']['Name'],
                Scope='REGIONAL',
                Id=blacklist['IPSet']['Id'],
                Addresses=list(ipset),
                LockToken=blacklist['LockToken']
            )
            logger.info(
                f"Successfully updated IPset {blacklist['IPSet']['Name']}, id= {blacklist['IPSet']['Id']}"
            )
        except Exception as e:
            logger.error(
                f"Failed to update IPset {blacklist['IPSet']['Name']}, id= {blacklist['IPSet']['Id']}\n{e}"
            )

        jips = {"ips": list(new_ips)}
        try:
            response = sfn.start_execution(
                stateMachineArn=os.environ['sfn_arn'],
                input=json.dumps(jips)
            )
            logger.info(
                f"Successfully started state machine {os.environ['sfn_arn']}"
            )
        except Exception as e:
            logger.error(
                f"Failed to start state machine {os.environ['sfn_arn']}\n{e}"
            )

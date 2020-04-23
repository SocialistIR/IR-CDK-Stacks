import json
import boto3
import os
import logging

waf = boto3.client('wafv2')
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    waf = boto3.client('wafv2')
    ips = event["ips"]
    try:
        blacklist = waf.get_ip_set(Name=os.environ['ipset_name'], Scope=os.environ['ipset_scope'], Id=os.environ['ipset_id'])
        logger.info(
            f"Successfully found IPset {os.environ['ipset_name']}, id= {os.environ['ipset_id']}"
        )
    except Exception as e:
        logger.error(
            f"Failed to find IPset {os.environ['ipset_name']}, id= {os.environ['ipset_id']}\n{e}"
        )

    updated = set(blacklist['IPSet']['Addresses']).difference(set(ips))
    try:
        response = waf.update_ip_set(
            Name=blacklist['IPSet']['Name'],
            Scope='REGIONAL',
            Id=blacklist['IPSet']['Id'],
            Addresses=list(updated),
            LockToken=blacklist['LockToken']
        )
        logger.info(
            f"Successfully updated IPset {os.environ['ipset_name']}, id= {os.environ['ipset_id']}"
        )
    except Exception as e:
        logger.error(
            f"Failed to update IPset {os.environ['ipset_name']}, id= {os.environ['ipset_id']}\n{e}"
        )
import json
import boto3
import os

waf = boto3.client("wafv2")


def lambda_handler(event, context):
    ips = event["ips"]
    print(ips)
    blacklist = waf.get_ip_set(
        Name=os.environ["waf_name"],
        Scope=os.environ["waf_scope"],
        Id=os.environ["waf_id"],
    )
    updated = set(blacklist["IPSet"]["Addresses"]).difference(set(ips))
    response = waf.update_ip_set(
        Name=blacklist["IPSet"]["Name"],
        Scope=os.environ["waf_scope"],
        Id=blacklist["IPSet"]["Id"],
        Addresses=list(updated),
        LockToken=blacklist["LockToken"],
    )

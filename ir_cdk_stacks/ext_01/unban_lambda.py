import json
import boto3
import os

waf = boto3.client('wafv2')

def lambda_handler(event, context):
    waf = boto3.client('wafv2')
    blacklist = waf.get_ip_set(Name = os.environ['ipset_name'], Scope = os.environ['ipset_scope'], Id = os.environ['ipset_id'])
    response = waf.update_ip_set(
        Name = blacklist['IPSet']['Name'],
        Scope = 'REGIONAL',
        Id = blacklist['IPSet']['Id'],
        Addresses = [],
        LockToken = blacklist['LockToken']
    )

def unban(input):
    ips = json.loads(input)["ips"]
    print(ips)
    blacklist = waf.get_ip_set(Name = os.environ['ipset_name'], Scope = os.environ['ipset_scope'], Id = os.environ['ipset_id'])
    
    updated = set(blacklist['IPSet']['Addresses']).difference(set(ips))
    response = waf.update_ip_set(
        Name = blacklist['IPSet']['Name'],
        Scope = 'REGIONAL',
        Id = blacklist['IPSet']['Id'],
        Addresses = list(updated),
        LockToken = blacklist['LockToken']
    )
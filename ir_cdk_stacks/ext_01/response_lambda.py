import json
import boto3
import time
import uuid

s3 = boto3.client('s3')
waf = boto3.client('wafv2')
sfn = boto3.client('stepfunctions')

def lambda_handler(event, context):
    blacklist = waf.get_ip_set(Name = os.environ['ipset_name'], Scope = os.environ['ipset_scope'], Id = os.environ['ipset_id'])
    ipset = set(blacklist['IPSet']['Addresses'])
    
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        obj = s3.get_object(Bucket=bucket, Key=key)
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
    print(new_ips)
        
    if len(new_ips) > 0:
        response = waf.update_ip_set(
            Name = blacklist['IPSet']['Name'],
            Scope = 'REGIONAL',
            Id = blacklist['IPSet']['Id'],
            Addresses = list(ipset),
            LockToken = blacklist['LockToken']
        )
        
        
        jips = {"ips": list(new_ips)}
        response = sfn.start_execution(
            stateMachineArn=os.environ['sfn_arn'],
            input = json.dumps(jips)
        )
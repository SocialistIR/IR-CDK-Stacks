import boto3
import os
import logging

waf = boto3.client('wafv2')
events = boto3.client('events')
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    try:
        waf.put_logging_configuration(
            LoggingConfiguration={
                'ResourceArn': os.environ["waf_arn"],
                'LogDestinationConfigs': [
                    os.environ["firehose_arn"]
                ],
            }
        )
        logger.info(
            f"Successfully enabled logging on Web ACL {os.environ['waf_arn']}, with kinesis firehose {os.environ['firehose_arn']}"
        )
    except Exception as e:
        logger.error(
            f"Failed to enable logging on Web ACL {os.environ['waf_arn']}, with kinesis firehose {os.environ['firehose_arn']}\n{e}"
        )
    try:
        wacl = waf.get_web_acl(
            Name=os.environ['waf_name'],
            Scope=os.environ['waf_scope'],
            Id=os.environ['waf_id'],
        )
        logger.info(
            f"Successfully got webacl {os.environ['waf_name']} with id{os.environ['waf_id']}"
        )
    except Exception as e:
        logger.error(
            f"Failed to get Web ACL {os.environ['waf_name']}, with id {os.environ['waf_id']}\n{e}"
        )
    rules = wacl['WebACL']['Rules']
    rbr = {
        'Name': 'Spam',
        'Priority': 3,
        'Statement': {'RateBasedStatement': {'Limit': int(os.environ['rate']), 'AggregateKeyType': 'IP'}},
        'Action': {'Block': {}},
        'VisibilityConfig': {'SampledRequestsEnabled': True, 'CloudWatchMetricsEnabled': True, 'MetricName': 'Spam'}
    }
    doslist = {
        'Name': 'Dos',
        'Priority': 0,
        'Statement': {'IPSetReferenceStatement': {'ARN': os.environ['doslist_arn']}},
        'Action': {'Block': {}},
        'VisibilityConfig': {'SampledRequestsEnabled': True, 'CloudWatchMetricsEnabled': True, 'MetricName': 'Dos'}
    }
    rules.append(doslist)
    rules.append(rbr)

    try:
        waf.update_web_acl(
            Name=os.environ['waf_name'],
            Scope=os.environ['waf_scope'],
            Id=os.environ['waf_id'],
            DefaultAction={'Allow': {}},
            Rules=rules,
            LockToken=wacl['LockToken'],
            VisibilityConfig=wacl['WebACL']['VisibilityConfig']
        )
        logger.info(
            f"Successfully updated webacl {os.environ['waf_name']} with id{os.environ['waf_id']}"
        )
    except Exception as e:
        logger.error(
            f"Failed to update Web ACL {os.environ['waf_name']}, with id {os.environ['waf_id']}\n{e}"
        )

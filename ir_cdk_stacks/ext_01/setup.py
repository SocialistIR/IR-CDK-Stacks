import boto3
import os

waf = boto3.client('wafv2')
events = boto3.client('events')

def lambda_handler(event, context):
    waf.put_logging_configuration(
        LoggingConfiguration={
            'ResourceArn': os.environ["waf_arn"],
            'LogDestinationConfigs': [
                os.environ["firehose_arn"]
            ],
        }
    )

    """target = events.list_targets_by_rule(
        Rule=os.environ["rule_name"],
        Limit=1
    )

    response = events.remove_targets(
        Rule=os.environ["rule_name"],
        Ids=[
            target['Targets'][0]['Id'],
        ]
    )

    response = events.delete_rule(
        Name=os.environ["rule_name"]
    )
"""
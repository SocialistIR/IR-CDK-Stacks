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

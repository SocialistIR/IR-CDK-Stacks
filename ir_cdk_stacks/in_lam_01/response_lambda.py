import json
import boto3
import gzip
import os
import urllib3
import logging as logger
import boto3

restricted = [
    "CreateFunction20150331",
    "DeleteFunction20150331",
    #"GetFunction20150331",
    "UpdateFunctionConfiguration20150331v2",
    "UpdateFunctionCode20150331v2",
    "GetFunction20150331v2"
]

def lambda_handler(event, context):
    # https://docs.aws.amazon.com/lambda/latest/dg/with-cloudtrail-example.html
    record = event['detail']
    print(record)
    eventName = record['eventName']
    try:
        functionName = record['requestParameters']['functionName']
    except:
        return
    if record['userIdentity']['type'] == 'AWSService':
        return
    arn = record['userIdentity']['arn']
    uName = record['userIdentity']['userName']
    if eventName in restricted:
        message = f"IN-LAM-01: '{arn}'\t{eventName}\t{functionName}\n"
        webhook_url = os.environ["webhook_url"]
        slack_message = {"channel" : "ir-cdk-stacks", "text" : message}
        encoded_data = json.dumps(slack_message).encode("utf-8")
        http = urllib3.PoolManager()
        response = http.request(
            "POST",
            webhook_url,
            body=encoded_data,
            headers={"Content-type": "application/json"}
        )
        if response.status == 200:
            logger.info(f"Successfully sent to channel {slack_message['channel']}")
        else:
            logger.info(f"Failed to send to channel {slack_message['channel']}.\n\
                Error: {response.status} - {response.data}"
            )
        
        # Attach explicit deny
        client = boto3.client('iam')
        response = client.attach_user_policy(
            PolicyArn='arn:aws:iam::544820149332:policy/LambdaDeny',
            UserName=uName  
        )
        print(response)
        
'''
# S3 BUCKET CODE - DELAY OF 10-20 minutes
print("~~~FUNCTION CALLED~~~")
    srcBucket = event['Records'][0]['s3']['bucket']['name'];
    srcKey = event['Records'][0]['s3']['object']['key'];
    
    s3 = boto3.client('s3')
    
    try:
        print("Getting compressed log file")    
        file = s3.get_object(
            Bucket=srcBucket,
            Key=srcKey
        )
        with gzip.open(file['Body'], "rb") as f:
        	data = f.read()
        format_data = json.loads(data)
        message = ""
        for record in format_data['Records']:
            eventName = record['eventName']
            try:
                functionName = record['requestParameters']['functionName']
            except:
                continue
            if record['userIdentity']['type'] == 'AWSService':
                continue
            arn = record['userIdentity']['arn']
            if eventName in restricted:
                print(record)
                message += f"IN-LAM-01: '{arn}'\t{eventName}\t{functionName}\n"
        if len(message) > 0:
            webhook_url = os.environ["webhook_url"]
            slack_message = {"channel" : "ir-cdk-stacks", "text" : message}
            encoded_data = json.dumps(slack_message).encode("utf-8")
            http = urllib3.PoolManager()
            response = http.request(
                "POST",
                webhook_url,
                body=encoded_data,
                headers={"Content-type": "application/json"}
            )
            if response.status == 200:
                logger.info(f"Successfully sent to channel {slack_message['channel']}")
            else:
                logger.info(f"Failed to send to channel {slack_message['channel']}.\n\
                    Error: {response.status} - {response.data}"
                )
    except Exception as e:
        print(e)
        pass
'''
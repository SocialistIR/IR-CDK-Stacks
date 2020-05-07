import json
import boto3
import urllib3
import os

iam = boto3.client('iam')
sns = boto3.client('sns')

clTrDenyPolicy = 'CltDenyAccess'
notificationTopic = 'CLTAccessCDK'

http = urllib3.PoolManager()

def hasValidGroup(userName):
    inline_user_groups = iam.list_groups_for_user(UserName=userName)
    cLTGroupName = os.environ["white_list_group"]
    print('Checking Valid Group')

    found = False
    for group in inline_user_groups['Groups']:
        if group['GroupName'] == cLTGroupName:
            found = True

    return found


def hasDenyPolicy(userName):
    inline_user_policies = iam.list_attached_user_policies(UserName=userName)['AttachedPolicies']

    print('Check Deny Policy')

    found = False
    for policy in inline_user_policies:
        if policy['PolicyName'] == clTrDenyPolicy:
            found = True
            break

    return found


def attachDenyPolicy(userName, denyPolicy):
    all_policies = iam.list_policies()
    for _policy in all_policies['Policies']:
        if _policy['PolicyName'] == clTrDenyPolicy:
            policyArn = _policy['Arn']

    response = iam.attach_user_policy(
        UserName=userName,
        PolicyArn=policyArn
    )

    print('attaching Deny policy')
    return response['ResponseMetadata']['HTTPStatusCode'] == 200


def sendNotification(message):
    print('sending notification')

    all_sns_topics = sns.list_topics()
    for topic in all_sns_topics['Topics']:
        if notificationTopic in topic['TopicArn']:
            notificationTopicArn = topic['TopicArn']

    response = sns.publish(
        TopicArn=notificationTopicArn,
        Message=message,
        Subject='Unauthorised access to CloudTrail',
        MessageStructure='string'
    )


def sendSlackNotification(message):
    message = "IN-CLT-01 Unauthorised CloudTrail Access:\n" + message
    webhook_url = os.environ["webhook_url"]

    slack_message = {"channel": "ir-cdk-stacks", "text": message}
    encoded_data = json.dumps(slack_message).encode("utf-8")
    response = http.request(
        "POST",
        webhook_url,
        body=encoded_data,
        headers={"Content-Type": "application/json"},
    )


def lambda_handler(event, context):
    print('lambda_handler')

    userName = event['detail']['userIdentity']['userName']
    sourceIPAddress = event["detail"]['sourceIPAddress']
    eventTime = event["detail"]["eventTime"]
    userAgent = event["detail"]["userAgent"]
    eventName = event["detail"]["eventName"]
    message = f'IN_CLT_01: {userName} tried to perform {eventName} on CLoudTrail at time {eventTime} from userAgent {userAgent} with IP {sourceIPAddress}. '

    if hasDenyPolicy(userName):
        print('User has deny policy. Will send slack notification')

        sendSlackNotification(message)
    else:
        if not hasValidGroup(userName):
            # 1. Attach Deny Policy
            maxReAttempts = 3

            while (maxReAttempts > 0):
                if attachDenyPolicy(userName, clTrDenyPolicy) is False:
                    maxReAttempts -= 1
                else:
                    break

            # 2. Inform developers with source IP Address

            message = message + ' CloudTrailDenyAccess Policy attached to deny access to CloudTrail.'
            sendNotification(message)

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from CloudTrailUnauthAccLambda!')
    }

import json
import boto3
import urllib3
import os

iam = boto3.client('iam')
sns = boto3.client('sns')
clwDenyPolicy = 'arn:aws:iam::544820149332:policy/ClWDenyAccess1'
clwDenyPolicy2 = 'arn:aws:iam::544820149332:policy/ClWDenyAccess2'
clwDenyPolicyName1 = 'ClWDenyAccess1'
clwDenyPolicyName2 = 'ClWDenyAccess2'
#clwGroupName = os.environ["white_list_group"]
clwGroupName = 'CLWAccess'
clwNotificationTopicArn = 'arn:aws:sns:us-east-1:544820149332:CDKCLWAccess'

http = urllib3.PoolManager()


def hasValidGroup(userName):
    response = iam.get_group(GroupName=clwGroupName)

    groupUsernames = []

    for user in response['Users']:
        groupUsernames.append(user['UserName'])

    # groupUsernames.remove('Karan')

    if userName in groupUsernames:
        return True
    else:
        return False


def hasDenyPolicy(userName):
    inline_user_policies = iam.list_attached_user_policies(UserName=userName)['AttachedPolicies']

    print('Check Deny Policy')

    found = False
    for policy in inline_user_policies:
        if policy['PolicyName'] == clwDenyPolicyName1 or policy['PolicyName'] == clwDenyPolicyName2:
            found = True
            break

    return found


def sendNotification(message):
    print('sending notification')
    response = sns.publish(
        TopicArn=clwNotificationTopicArn,
        Message=message,
        Subject='Access to CloudWatch',
        MessageStructure='string'
    )


def sendSlackNotification(message):
    message = "IN-CLW-01 Unauthorised CloudWatch Access:\n" + message
    # webhook_url = os.environ["webhook_url"]
    webhook_url = "https://hooks.slack.com/services/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"
    slack_message = {"channel": "ir-cdk-stacks", "text": message}
    encoded_data = json.dumps(slack_message).encode("utf-8")
    response = http.request(
        "POST",
        webhook_url,
        body=encoded_data,
        headers={"Content-Type": "application/json"},
    )


def lambda_handler(event, context):
    userName = event['detail']['userIdentity']['userName']
    userType = event['detail']['userIdentity']['type']
    sourceIPAddress = event["detail"]['sourceIPAddress']
    eventTime = event["detail"]["eventTime"]
    userAgent = event["detail"]["userAgent"]
    eventName = event["detail"]["eventName"]
    message = f'IN_CLW_01: {userName} tried to perform {eventName} on Cloudwatch at time {eventTime} from userAgent {userAgent} with IP {sourceIPAddress}. '

    validUser = hasValidGroup(userName)

    if hasDenyPolicy(userName):

        message = message + ' CloudWatchDeny Policy is already attached to deny access to CloudWatch.'
        sendNotification(message)

    else:
        if userType == "IAMUser" and not validUser:

            response = iam.attach_user_policy(UserName=userName, PolicyArn=clwDenyPolicy)
            response = iam.attach_user_policy(UserName=userName, PolicyArn=clwDenyPolicy2)

            message = message + ' CloudWatchDeny Policy attached to deny access to CloudWatch.'
            sendNotification(message)

        else:

            message = message + ' Access Granted : CloudWatch Access allowed.'
            sendNotification(message)

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from CloudWatch Lambda!')
    }

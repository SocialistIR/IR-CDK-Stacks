import json
import boto3

iam = boto3.client('iam')
sns = boto3.client('sns')
clTrPolicyArn = 'arn:aws:iam::544820149332:policy/CloudTrailAccess'
clTrDenyPolicyArn = 'arn:aws:iam::544820149332:policy/CloudTrailDenyAccess'
notificationTopicArn = 'arn:aws:sns:us-east-1:544820149332:CloudTrailCRUD'


def hasValidPolicy(userName):
    inline_user_policies = iam.list_attached_user_policies(UserName=userName)['AttachedPolicies']
    print('Check ValidPolicy')

    found = False
    for policy in inline_user_policies:
        if policy['PolicyArn'] == clTrPolicyArn:
            found = True
            break

    return found


def attachDenyPolicy(userName, denyPolicy):
    response = iam.attach_user_policy(
        UserName=userName,
        PolicyArn=denyPolicy
    )

    print('attaching Deny policy')
    return response['ResponseMetadata']['HTTPStatusCode'] == 200


def sendNotification(userName, sourceIPAdrress, eventName, eventTime, userAgent):
    message = userName + ' tried to perform ' + eventName + ' on CloudTrail ' + ' at time ' + eventTime + ' from userAgent ' + userAgent + ' with IP ' + sourceIPAdrress
    print('sending notification')
    response = sns.publish(
        TopicArn=notificationTopicArn,
        Message=message,
        Subject='Unauthorised access to CloudTrail',
        MessageStructure='string'
    )


def lambda_handler(event, context):
    print('lambda_handler')

    userName = event['detail']['userIdentity']['userName']
    sourceIPAddress = event["detail"]['sourceIPAddress']
    eventTime = event["detail"]["eventTime"]
    userAgent = event["detail"]["userAgent"]
    eventName = event["detail"]["eventName"]

    if not hasValidPolicy(userName):
        # 1. Attach Deny Policy
        maxReAttempts = 3

        while (maxReAttempts > 0):
            if attachDenyPolicy(userName, clTrDenyPolicyArn) is False:
                maxReAttempts -= 1
            else:
                break

        # 2. Inform developers with source IP Address
        sendNotification(userName, sourceIPAddress, eventName, eventTime, userAgent)

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from CloudTrailUnauthAccLambda!')
    }

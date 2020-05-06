import json
import boto3
import urllib3

iam = boto3.client('iam')
sns = boto3.client('sns')
IAM_Allow_ModifyPolicyArn = 'arn:aws:iam::544820149332:policy/IAM_Allow_modify'
IAM_Deny_ModifyPolicyArn = 'arn:aws:iam::544820149332:policy/IAM_Deny_modify'
IAM_Deny_ModifyPolic = 'IAM_Deny_modify'
notificationTopicArn = 'arn:aws:sns:us-east-1:544820149332:IAM-test-sns'
IAM_modifyGroupName = 'IAM_Allow_Modify'

# http = urllib3.PoolManager()


def hasValidGroup(userName):
    inline_user_groups = iam.list_groups_for_user(UserName=userName)

    print('Check Valid Group')

    found = False
    for group in inline_user_groups['Groups']:
        if group['GroupName'] == IAM_modifyGroupName:
            found = True

    return found


def attachDenyPolicy(userName, denyPolicy):
    response = iam.attach_user_policy(
        UserName=userName,
        PolicyArn=denyPolicy
    )

    print('attaching Deny policy')
    return response['ResponseMetadata']['HTTPStatusCode'] == 200


def sendNotification(message):
    print('sending notification')
    response = sns.publish(
        TopicArn=notificationTopicArn,
        Message=message,
        Subject='Unauthorised access to modify IAM',
        MessageStructure='string'
    )


def lambda_handler(event, context):
    print('lambda_handler')

    userName = event['detail']['userIdentity']['userName']
    sourceIPAddress = event["detail"]['sourceIPAddress']
    eventTime = event["detail"]["eventTime"]
    userAgent = event["detail"]["userAgent"]
    eventName = event["detail"]["eventName"]
    
    #print(event)
    
    message = f'username: {userName} tried to perform {eventName} on CLoudTrail at time {eventTime} from userAgent {userAgent} with IP {sourceIPAddress}. '
    print('MMMM',message)
    
    if not hasValidGroup(userName):
        # 1. Attach Deny Policy
        maxReAttempts = 3

        while (maxReAttempts > 0):
            if attachDenyPolicy(userName, IAM_Deny_ModifyPolicyArn) is False:
                maxReAttempts -= 1
            else:
                break

        # 2. Inform developers with source IP Address

        message = message + ' IAM-Deny-modify Policy attached to deny access to IAM.'
        sendNotification(message)

    return {
        'statusCode': 200,
        'body': json.dumps('Hello to New World!')
    }


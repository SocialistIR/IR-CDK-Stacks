import json
import boto3

iam = boto3.client('iam')
sns = boto3.client('sns')
IAM_Allow_ModifyPolicyArn = 'arn:aws:iam::544820149332:policy/IAM_Allow_modify'
IAM_Deny_ModifyPolicyArn = 'arn:aws:iam::544820149332:policy/IAM_Deny_modify'
notificationTopicArn = 'arn:aws:sns:us-east-1:544820149332:send-email-no-SNS'
IAM_modifyGroupName = 'IAM_Allow_Modify'

def hasValidPolicy(userName):    
    inline_user_policies = iam.list_attached_user_policies(UserName=userName)['AttachedPolicies']
    inline_user_groups = iam.list_groups_for_user(UserName=userName)

    print('Check ValidPolicy')
    
    found = False
    
    for group in inline_user_groups['Groups']:
        if group['GroupName'] == IAM_modifyGroupName:
            found = True
    return found
    
def attachDenyPolicy(userName, denyPolicy):
    response = iam.attach_user_policy(
        UserName = userName,
        PolicyArn = denyPolicy
    )
    
    print('attach Deny policy')
    return response['ResponseMetadata']['HTTPStatusCode'] == 200

def sendNotification( userName, sourceIPAdrress, eventName, eventTime, userAgent):
   
    message = 'We found:'+userName+'pretending to modify{'+ eventName +'} on IAM '+'at time [' + eventTime + '] and the sourceIP is' + sourceIPAdrress
    print('sending notification')
    response = sns.publish(
        TopicArn= notificationTopicArn,
        Message= message,
        Subject='Unauthorised IAM to Modify',
        MessageStructure='string'
    )
    
    
    
def lambda_handler(event, context):
    print('lambda_handler')
    
    userName = event['detail']['userIdentity']['userName']
    sourceIPAddress = event["detail"]['sourceIPAddress']
    eventTime = event["detail"]["eventTime"]
    eventName = event["detail"]["eventName"]
    
    if not hasValidPolicy(userName) :# if not be assigned a valid policy,trigger the SNS 
        maxReAttempts = 3
        
        while (maxReAttempts > 0) :
            if attachDenyPolicy(userName, IAM_Deny_ModifyPolicyArn) is False:
                maxReAttempts -= 1
            else:
                break
     
        sendNotification(userName , sourceIPAddress , eventTime , eventName)
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from IAM_Modify_Lambda!')
    }

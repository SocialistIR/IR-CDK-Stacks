import json
import boto3
import urllib3

iam = boto3.client('iam')
sns = boto3.client('sns')
clwDenyPolicy='arn:aws:iam::544820149332:policy/ClWDenyAccess1'
clwDenyPolicy2='arn:aws:iam::544820149332:policy/ClWDenyAccess2'
clwGroupName='testgroupclw'
clwNotificationTopicArn = 'arn:aws:sns:us-east-1:544820149332:CDKCLWAccess'

http = urllib3.PoolManager()

def lambda_handler(event, context):
    
    userName = event['detail']['userIdentity']['userName']
    userType = event['detail']['userIdentity']['type']
    
    #if userType=="IAMUser":
        
    # sourceIPAddress = event["detail"]['sourceIPAddress']
    # eventTime = event["detail"]["eventTime"]
    # userAgent = event["detail"]["userAgent"]
    # eventName = event["detail"]["eventName"]
    # message = f'IN_CLW_01: {userName} tried to perform {eventName} on Cloudwatch at time {eventTime} from userAgent {userAgent} with IP {sourceIPAddress}. '

    
    
    print(event)
    print(context)
    # TODO implement
    userName = event['detail']['userIdentity']['userName']
    userType = event['detail']['userIdentity']['type']
    # sourceIPAddress = event["detail"]['sourceIPAddress']
    # eventTime = event["detail"]["eventTime"]
    # userAgent = event["detail"]["userAgent"]
    # eventName = event["detail"]["eventName"]
    
    response = iam.get_group(GroupName='testgroupclw')
    print(response['Group']['GroupName'])
    groupUsernames=[]
    for user in response['Users']:
        groupUsernames.append(user['UserName'])
    groupUsernames.remove('Karan')
    print(groupUsernames)
    # "type": "IAMUser",
    if userName not in groupUsernames and userType=="IAMUser":
        response = iam.attach_user_policy(UserName = userName, PolicyArn = clwDenyPolicy)
        response = iam.attach_user_policy(UserName = userName, PolicyArn = clwDenyPolicy2)
    
    print('attach policy')
    #return response['ResponseMetadata']['HTTPStatusCode'] == 200
    
    #print(userName)
        # print("UserName: {0}\nCreateDate: {1}\n".format(user['UserName'], user['CreateDate']))
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda.hello fellow!')
    }

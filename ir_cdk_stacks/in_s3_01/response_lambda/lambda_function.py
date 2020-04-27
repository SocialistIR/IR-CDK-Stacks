import json
import boto3
from datetime import datetime
from dateutil.tz import tzutc

client = boto3.client('iam')
sns = boto3.client('sns')
s3 = boto3.client('s3')

bucketName = 'socialistir-dev'
sns_topic = 'S3-Notification-Write'
developerGroupName = 'Developer-SocialistIR'
deny_policy_name = 'S3-Custom-Shub-Deny_Write'

def attachDenyPolicy(userName, denyPolicy):
    response = client.attach_user_policy(
        UserName = userName,
        PolicyArn = denyPolicy
    )
    return response['ResponseMetadata']['HTTPStatusCode'] == 200


def lambda_handler(event, context):
    print(event, context, "Lambda Triggered okay take 3 at 2:17 am delete dummy3.txt")
    
    if 'userName' in event['detail']['userIdentity']:
        username = event['detail']['userIdentity']['userName']
    else:
        username = event['detail']['userIdentity']['sessionContext']['sessionIssuer']['userName']
    print("username",username)
    
    response_sns = sns.list_topics()
    sns_topic_arn = ''
    for topic in response['Topics']:
        if 'S3-Notification-Write' in topic['TopicArn']:
            sns_topic_arn = topic['TopicArn']
    
    if 'S3WriteIR' in username:
        response = sns.publish(
                TopicArn=sns_topic_arn, 
                Message= (event['detail']['requestParameters']['key'] + " file has been restored to the "+bucketName+ " S3 bucket."),
                Subject= bucketName + ' Bucket Restored', 
                MessageStructure='string'
            )
        return {
        'statusCode': 200,
        'body': json.dumps('S3WriteIR performed a restore operation')
    }
    
    
    eventName = event['detail']['eventName']
    hostIPAddress = event['detail']['sourceIPAddress']
    hostAgent = event['detail']['userAgent'].replace('[','').replace(']','').split(' ')[0]
    eventTime = event['time']
    
    inline_user_policies = client.list_attached_user_policies(UserName=username)
    inline_user_groups = client.list_groups_for_user(UserName=username)
    
    flag = 1
    denyFlag = 1
    # for policy in inline_user_policies['AttachedPolicies']:
    #     print(policy['PolicyName'])
    #     if policy['PolicyName'] == 'socialistir-custom-shub-write':
    #         flag = 0
    #     if policy['PolicyName'] == 'S3-Custom-Shub-Deny_Write':
    #         denyFlag = 0
    for policy in inline_user_policies['AttachedPolicies']:
        if policy['PolicyName'] == deny_policy_name:
             denyFlag = 0
    
    for group in inline_user_groups['Groups']:
        if group['GroupName'] == developerGroupName:
            flag = 0
    
    fileListModified = []
    
    if(flag):
        if (denyFlag):
            policy_arn = ''
            response_policy = client.list_policies(Scope='Local')
            
            for policy in response['Policies']:
                if deny_policy_name in policy['PolicyName']:
                    policy_arn = policy['Arn']
            
            attachDenyPolicy(username,policy_arn)
            print("Deny user the access policy attached")
           
            if eventName == 'PutObject':
                fileName = event['detail']['requestParameters']['key']
                fileListModified.append(fileName)
                versionHistory = s3.list_object_versions(
                    Bucket=bucketName,
                    Prefix=fileName
                    )
                versionId = ''
                for ver in versionHistory['Versions']:
                    if ver['IsLatest'] == True:
                        versionId = ver['VersionId']
                restoreOld = s3.delete_object(
                    Bucket=bucketName, 
                    Key =fileName, 
                    VersionId = versionId 
                    )
                    
            if eventName == 'DeleteObjects':
                versionHistory = s3.list_object_versions(Bucket=bucketName)
                eventTime = event['detail']['eventTime']
                formatEventTime = datetime.strptime(eventTime, '%Y-%m-%dT%H:%M:%SZ')
                formatEventTime = formatEventTime.replace(tzinfo=tzutc())
                versionHistory = s3.list_object_versions(Bucket=bucketName)
                versionIdList = []
                # fileListModified = []
                for ver in versionHistory['DeleteMarkers']:
                    if ver['LastModified'] > formatEventTime:
                        versionIdList.append(ver['VersionId'])
                        fileListModified.append(ver['Key'])
                for i in range(len(versionIdList)):
                    restoreOld = s3.delete_object(
                        Bucket=bucketName, 
                        Key =fileListModified[i], 
                        VersionId = versionIdList[i] 
                        )
                        
            response = sns.publish(
                TopicArn=sns_topic_arn, 
                Message= (username + ' performed an unauthorised ' + 
                    eventName +' operation to ' + bucketName + 
                    ' Bucket at time ' + eventTime + 
                    ' from user agent '+ hostAgent + 
                    ' with IP: '+ hostIPAddress + 
                    " and modified files: " + ','.join(fileListModified)),
                Subject= bucketName + ' Bucket Modified', 
                MessageStructure='string'
            )
        else:
            print("Access already denied")
            
            if eventName == 'PutObject':
                eventTime = event['detail']['eventTime']
                formatEventTime = datetime.strptime(eventTime, '%Y-%m-%dT%H:%M:%SZ')
                formatEventTime = formatEventTime.replace(tzinfo=tzutc())
                fileName = event['detail']['requestParameters']['key']
                fileListModified.append(fileName)
                versionHistory = s3.list_object_versions(
                    Bucket=bucketName,
                    Prefix=fileName
                    )
                
                versionId = ''
                for ver in versionHistory['Versions']:
                    if ver['IsLatest'] == True and ver['LastModified'] > formatEventTime:
                        versionId = ver['VersionId']
                restoreOld = s3.delete_object(
                    Bucket=bucketName, 
                    Key =fileName, 
                    VersionId = versionId 
                    )
                
                response = sns.publish(
                    TopicArn=sns_topic_arn, 
                    Message= (username + ' performed an unauthorised ' + 
                        eventName +' operation to ' + bucketName + 
                        ' Bucket at time ' + eventTime + 
                        ' from user agent '+ hostAgent + 
                        ' with IP: '+ hostIPAddress + 
                        " and modified files: " + ','.join(fileListModified)),
                    Subject= bucketName + ' Bucket Modified', 
                    MessageStructure='string'
                )
    else:
        print("Access policy is correctly assigned")
 
    return {
        'statusCode': 200,
        'body': json.dumps(username + ' performed an unauthorised ' + 
                    eventName +' operation to ' + bucketName + 
                    ' Bucket at time ' + eventTime + 
                    ' from user agent '+ hostAgent + 
                    ' with IP: '+ hostIPAddress + 
                    " and modified files: " + ','.join(fileListModified))
    }

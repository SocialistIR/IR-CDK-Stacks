from aws_cdk import core
from aws_cdk import aws_sns as sns
from aws_cdk import aws_sns_subscriptions as subs
from aws_cdk import aws_iam as iam
import aws_cdk.aws_cloudtrail as cloudtrail
from aws_cdk import aws_events as events
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_s3 as s3
import aws_cdk.aws_events_targets as event_target


class CdkStackStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        
        custom_allow_policy = iam.ManagedPolicy(self,
                                         "socialistir-custom-shub-write",
                                         managed_policy_name = "socialistir-custom-shub-write",
                                         statements=[
                                             iam.PolicyStatement(
                                                 effect=iam.Effect.ALLOW,
                                                 actions=[
                                                        "s3:PutAnalyticsConfiguration",
                                                        "s3:PutAccelerateConfiguration",
                                                        "s3:DeleteObjectVersion",
                                                        "s3:RestoreObject",
                                                        "s3:CreateBucket",
                                                        "s3:ReplicateObject",
                                                        "s3:PutEncryptionConfiguration",
                                                        "s3:DeleteBucketWebsite",
                                                        "s3:AbortMultipartUpload",
                                                        "s3:PutLifecycleConfiguration",
                                                        "s3:DeleteObject",
                                                        "s3:DeleteBucket",
                                                        "s3:PutBucketVersioning",
                                                        "s3:PutMetricsConfiguration",
                                                        "s3:PutReplicationConfiguration",
                                                        "s3:PutObjectLegalHold",
                                                        "s3:PutBucketCORS",
                                                        "s3:PutInventoryConfiguration",
                                                        "s3:PutObject",
                                                        "s3:PutBucketNotification",
                                                        "s3:PutBucketWebsite",
                                                        "s3:PutBucketRequestPayment",
                                                        "s3:PutObjectRetention",
                                                        "s3:PutBucketLogging",
                                                        "s3:PutBucketObjectLockConfiguration",
                                                        "s3:ReplicateDelete"
                                                    ],
                                                 resources=["arn:aws:s3:::socialistir-preprod",
                                                            "arn:aws:s3:::socialistir-preprod/*"]
                                             )
                                         ])

        custom_deny_policy = iam.ManagedPolicy(self,
                                         "S3-Custom-Shub-Deny_Write",
                                         managed_policy_name = "S3-Custom-Shub-Deny_Write",
                                         statements=[
                                             iam.PolicyStatement(
                                                 effect=iam.Effect.DENY,
                                                 actions=[
                                                        "s3:PutAnalyticsConfiguration",
                                                        "s3:PutAccelerateConfiguration",
                                                        "s3:PutMetricsConfiguration",
                                                        "s3:PutReplicationConfiguration",
                                                        "s3:CreateBucket",
                                                        "s3:PutBucketCORS",
                                                        "s3:PutInventoryConfiguration",
                                                        "s3:PutEncryptionConfiguration",
                                                        "s3:PutBucketNotification",
                                                        "s3:DeleteBucketWebsite",
                                                        "s3:PutBucketWebsite",
                                                        "s3:PutBucketRequestPayment",
                                                        "s3:PutBucketLogging",
                                                        "s3:PutLifecycleConfiguration",
                                                        "s3:PutBucketObjectLockConfiguration",
                                                        "s3:DeleteBucket",
                                                        "s3:PutBucketVersioning",
                                                        "s3:ReplicateObject",
                                                        "s3:PutObject",
                                                        "s3:AbortMultipartUpload",
                                                        "s3:PutObjectRetention",
                                                        "s3:DeleteObjectVersion",
                                                        "s3:RestoreObject",
                                                        "s3:PutObjectLegalHold",
                                                        "s3:DeleteObject",
                                                        "s3:ReplicateDelete"
                                                    ],
                                                 resources=["arn:aws:s3:::socialistir-preprod",
                                                            "arn:aws:s3:::socialistir-preprod/*"]
                                             )
                                         ])

        devgroup1 = iam.Group(self, 
                            "Developer-socialistir", 
                            group_name = "Developer-socialistir", 
                            managed_policies=[custom_allow_policy])

        devgroup2 = iam.Group(self, 
                            "Developer-teamA", 
                            group_name = "Developer-teamA")

        bucket = s3.Bucket(self,
            id = 'socialistir-preprod', 
            bucket_name='socialistir-preprod', 
            versioned=True, 
            website_error_document='index.html', 
            website_index_document='index.html'
        )

        # print(bucket.bucket_arn)

        topic = sns.Topic(self, "S3-Notification-Write", topic_name="S3-Notification-Write")
        # topic.grant_publish(iam.ServicePrincipal("*"))
        topic.add_subscription(subs.EmailSubscription('s.mathur@unsw.edu.au'))

        trail = cloudtrail.Trail(self, "S3-Write-Operation-Trail")

        trail.add_s3_event_selector(["arn:aws:s3:::socialistir-preprod/"],
                                    include_management_events=True,
                                    read_write_type=cloudtrail.ReadWriteType.WRITE_ONLY
                                    )

        ep = {"source": ["aws.s3"],"detail": {"eventSource": ["s3.amazonaws.com"],
            "eventName": [
                "ListObjects",
                "ListObjectVersions",
                "PutObject",
                "GetObject",
                "HeadObject",
                "CopyObject",
                "GetObjectAcl",
                "PutObjectAcl",
                "CreateMultipartUpload",
                "ListParts",
                "UploadPart",
                "CompleteMultipartUpload",
                "AbortMultipartUpload",
                "UploadPartCopy",
                "RestoreObject",
                "DeleteObject",
                "DeleteObjects",
                "GetObjectTorrent",
                "SelectObjectContent",
                "PutObjectLockRetention",
                "PutObjectLockLegalHold",
                "GetObjectLockRetention",
                "GetObjectLockLegalHold"
            ],
            "requestParameters": {
                "bucketName": [
                    "socialistir-preprod"
                ]
            }
        }
        }

        rule = events.Rule(self,
                           "Shub-s3",
                           description='Rule created by CDK for S3 monitoring',
                           enabled=True,
                           rule_name="Shub-s3",
                           event_pattern=ep)

        lambda_dir_path = "D:\\OneDrive - UNSW\\Term 4\\AWS\\Project\\IR-CDK-Stacks\\ir_cdk_stacks\\IN-S3-01\\response_lambda"
        response_lambda = _lambda.Function(
            self,
            "S3WriteIR",
            runtime=_lambda.Runtime.PYTHON_3_8,
            handler="lambda_function.lambda_handler",
            code=_lambda.Code.from_asset(lambda_dir_path),
            function_name="S3WriteIR"
        )

        response_lambda.add_to_role_policy(
            iam.PolicyStatement(
                actions=[
                    "iam:*",
                    "organizations:DescribeAccount",
                    "organizations:DescribeOrganization",
                    "organizations:DescribeOrganizationalUnit",
                    "organizations:DescribePolicy",
                    "organizations:ListChildren",
                    "organizations:ListParents",
                    "organizations:ListPoliciesForTarget",
                    "organizations:ListRoots",
                    "organizations:ListPolicies",
                    "organizations:ListTargetsForPolicy"
                ],
                effect=iam.Effect.ALLOW,
                resources=["*"],
            )
        )

        response_lambda.add_to_role_policy(
            iam.PolicyStatement(
                actions=[
                    "iam:*",
                    "organizations:DescribeAccount",
                    "organizations:DescribeOrganization",
                    "organizations:DescribeOrganizationalUnit",
                    "organizations:DescribePolicy",
                    "organizations:ListChildren",
                    "organizations:ListParents",
                    "organizations:ListPoliciesForTarget",
                    "organizations:ListRoots",
                    "organizations:ListPolicies",
                    "organizations:ListTargetsForPolicy"
                ],
                effect=iam.Effect.ALLOW,
                resources=["*"],
            )
        )

        response_lambda.add_to_role_policy(
            iam.PolicyStatement(
                actions=[
                    "s3:*"
                ],
                effect=iam.Effect.ALLOW,
                resources=["*"],
            )
        )

        response_lambda.add_to_role_policy(
            iam.PolicyStatement(
                actions=[
                    "sns:*"
                ],
                effect=iam.Effect.ALLOW,
                resources=["*"],
            )
        )

        rule.add_target(event_target.LambdaFunction(response_lambda))



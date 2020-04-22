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

        # The code that defines your stack goes here
        topic = sns.Topic(self, "CDKTestSNSTopic", topic_name="CDKTestSNSTopic")
        # topic.grant_publish(iam.ServicePrincipal("*"))
        topic.add_subscription(subs.EmailSubscription('s.mathur@unsw.edu.au'))

        trail = cloudtrail.Trail(self, "MyAmazingCloudTrail2")

        trail.add_s3_event_selector(["arn:aws:s3:::socialistir/"],
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
                    "socialistir-dev"
                ]
            }
        }
        }

        rule = events.Rule(self,
                           "CDK-Shub-s3-TEST",
                           description='Rule created by CDK for testing',
                           enabled=True,
                           rule_name="CDK-Shub-s3-TEST",
                           event_pattern=ep)

        lambda_dir_path = "D:\\OneDrive - UNSW\\Term 4\\AWS\\Project\\IR-CDK-Stacks\\ir_cdk_stacks\\IN-S3-01\\response_lambda"
        response_lambda = _lambda.Function(
            self,
            "CDK-S3WriteIR-TEST",
            runtime=_lambda.Runtime.PYTHON_3_8,
            handler="lambda_function.lambda_handler",
            code=_lambda.Code.from_asset(lambda_dir_path),
            function_name="CDK-S3WriteIR-TEST"
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

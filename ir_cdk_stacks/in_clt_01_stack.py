from aws_cdk import (
    core,
    aws_cloudwatch as cloudwatch,
    aws_events as events,
    aws_lambda as _lambda,
    aws_iam as iam,
    aws_events_targets as event_target,
    aws_sns as sns,
    aws_sns_subscriptions as subs
)

import os
import logging

logger = logging.getLogger(__name__)

class InClt01Stack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        NOTIFY_EMAIL = self.node.try_get_context("notify_email")
        SLACK_WEBHOOK_URL = self.node.try_get_context("webhook_url")
        WHITE_LIST_GROUP = self.node.try_get_context("white_list_group")

        if (
            not NOTIFY_EMAIL
            or not SLACK_WEBHOOK_URL
            or not WHITE_LIST_GROUP
        ):
            logger.error(f"Required context variables for {id} were not provided!")
        else:


            # 1. Create Response Lambda
            lambda_dir_path = os.path.join(os.getcwd(), "ir_cdk_stacks", "in_clt_01")
            response_lambda = _lambda.Function(
                self,
                "InClt01ResponseFunction",
                runtime=_lambda.Runtime.PYTHON_3_8,
                handler="clUnauthAccessResponse.lambda_handler",
                code=_lambda.Code.from_asset(lambda_dir_path),
                function_name="InClt01ResponseFunction",
                environment={
                    "webhook_url": SLACK_WEBHOOK_URL,
                    "white_list_group": WHITE_LIST_GROUP,
                }
            )

            ep = {
                  "source": [
                    "aws.cloudtrail"
                  ]
                }

            # 2. Make that rule Track Cloudtrail events
            rule = events.Rule(self,
                               "cdkRule",
                               description= 'Rule created by CDK for monitoring CloudTrail access',
                               enabled= True,
                               rule_name= "CltAccessRule",
                               event_pattern= ep )

            # 3. Add Permissions and role to Lambda
            action = [
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
                ]

            response_lambda.add_to_role_policy(
                iam.PolicyStatement(
                    actions=action,
                    effect=iam.Effect.ALLOW, resources=["*"],
                )
            )

            # 4. Permission to send SNS notification
            response_lambda.add_to_role_policy(
                iam.PolicyStatement(
                    actions=[
                        "sns:*"
                    ],
                    effect=iam.Effect.ALLOW,
                    resources=["*"],
                )
            )

            # 5. Add Lambda as target of Rule
            rule.add_target(event_target.LambdaFunction(response_lambda))

            # 6. Create SNS topic and subscription
            topic = sns.Topic(self, "CLTAccessCDK", topic_name="CLTAccessCDK")
            # topic.grant_publish(iam.ServicePrincipal("*"))
            topic.add_subscription(subs.EmailSubscription(NOTIFY_EMAIL))

            # 7. Create IAM allow/deny policy
            cltDenyAccessPolicy = iam.ManagedPolicy(self,
                                             "InCLT01DenyPolicy",
                                             managed_policy_name = "CltDenyAccess",
                                             statements=[
                                                 iam.PolicyStatement(
                                                     effect=iam.Effect.DENY,
                                                     actions=["cloudtrail:*"],
                                                     resources=["*"]
                                                 )
                                             ])

            # 8. Create IAM group
            cltAccessGroup = iam.Group(
                self,
                "cltAccessGroup",
                group_name = "cltAccessGroup"
        )
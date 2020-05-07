from aws_cdk import core
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_cloudwatch as cloudwatch
from aws_cdk import aws_events as events
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_iam as iam
from aws_cdk import aws_events_targets as event_target
from aws_cdk import aws_sns as sns
from aws_cdk import aws_sns_subscriptions as subs

import os
import logging

logger = logging.getLogger(__name__)
class InClw01Stack(core.Stack):

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

        # The code that defines your stack goes here
            ep1 = {
                "source": [
                    "aws.logs"
                ]
            }

            ep2 = {
                "source": [
                    "aws.cloudwatch"
                ]
            }

            rule1 = events.Rule(self,
                               "cdkRule1_clw",
                               description='Rule created by CLW CDK',
                               enabled=True,
                               rule_name="rule1bycdk_clw",
                               event_pattern=ep1)

            rule2 = events.Rule(self,
                                "cdkRule2_clw",
                                description='Rule created by CLW CDK',
                                enabled=True,
                                rule_name="rule2bycdk_clw",
                                event_pattern=ep2)

            # 3. Create response lambda and add it as a target of the rule
            lambda_dir_path = os.path.join(os.getcwd(), "ir_cdk_stacks", "in_clw_01")
            response_lambda = _lambda.Function(
                self,
                "InClw01ResponseFunction",
                runtime=_lambda.Runtime.PYTHON_3_7,
                handler="clwUnauthAccessResponse.lambda_handler",
                code=_lambda.Code.from_asset(lambda_dir_path),
                function_name="InClw01ResponseFunction",
                environment = {
                    "webhook_url": SLACK_WEBHOOK_URL,
                    "white_list_group": WHITE_LIST_GROUP,
                }
            )

            response_lambda.add_to_role_policy(
                iam.PolicyStatement(
                    actions=["*"],
                    effect=iam.Effect.ALLOW, resources=["*"],
                )
            )


            rule1.add_target(event_target.LambdaFunction(response_lambda))
            rule2.add_target(event_target.LambdaFunction(response_lambda))


            # 4. Create SNS topic and subscription
            topic = sns.Topic(self, "CDKCLWAccess", topic_name="CDKCLWAccess")

            topic.add_subscription(subs.EmailSubscription(NOTIFY_EMAIL))
            #topic.add_subscription(subs.EmailSubscription('k.singh.1@unsw.edu.au'))



            # 5. Create IAM allow/deny policy
            clwDenyAccessPolicy1 = iam.ManagedPolicy(self,
                                             "InCLW01DenyPolicy1",
                                             managed_policy_name = "ClWDenyAccess1",
                                             statements=[
                                                 iam.PolicyStatement(
                                                     effect=iam.Effect.DENY,
                                                     actions=["logs:*"],
                                                     resources=["*"]
                                                 )
                                             ])

            clwDenyAccessPolicy2 = iam.ManagedPolicy(self,
                                                     "InCLW01DenyPolicy2",
                                                     managed_policy_name="ClWDenyAccess2",
                                                     statements=[
                                                         iam.PolicyStatement(
                                                             effect=iam.Effect.DENY,
                                                             actions=["cloudwatch:*"],
                                                             resources=["*"]
                                                         )
                                                     ])



            # 6. Create IAM group
            clwAccessGroup = iam.Group(
                self,
                "clwAccessGroup",
                group_name = "clwAccessGroup"
            )




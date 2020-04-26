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
import datetime

class CdkStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # The code that defines your stack goes here

        # 1. Create Cloudwatch Rule
        # 2. Make that rule Track Cloudtrail events

        lambda_dir_path = os.path.join(os.getcwd(), "cdk")
        response_lambda = _lambda.Function(
            self,
            "InClt01ResponseFunction",
            runtime=_lambda.Runtime.PYTHON_3_8,
            handler="clUnauthAccessResponse.lambda_handler",    #TODO: might have to change to lambda_function
            code=_lambda.Code.from_asset(lambda_dir_path),
            function_name="InClt01ResponseFunction"
        )

        ep = {
              "source": [
                "aws.cloudtrail"
              ]
            }

        rule = events.Rule(self,
                           "cdkRule",
                           description= 'Rule created by CDK',
                           enabled= True,
                           rule_name= "rulebycdk",
                           event_pattern= ep )

        # 3. Create response lambda and add it as a target of the rule
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
        # rule.add_target(response_lambda)

        rule.add_target(event_target.LambdaFunction(response_lambda))

        # 4. Create SNS topic and subscription
        topic = sns.Topic(self, "CDKTestCLTAccess", topic_name="CDKTestCLTAccess")
        # topic.grant_publish(iam.ServicePrincipal("*"))
        topic.add_subscription(subs.EmailSubscription('y.tamakuwala@unsw.edu.au'))

        # 5. Create IAM allow/deny policy
        cltDenyAccessPolicy = iam.Policy(self,
                                         f"InCLT01DenyPolicy{int(datetime.datetime.now().timestamp())}",
                                         policy_name = "CltDenyAccess",
                                         statements=[
                                             iam.PolicyStatement(
                                                 effect=iam.Effect.DENY,
                                                 actions=["cloudtrail:*"],
                                                 resources=["*"]
                                             )
                                         ])

        # 6. Create IAM group
        cltAccessGroup = iam.Group(
            self,
            "cltAccessGroup",
            group_name = "cltAccessGroup"
        )
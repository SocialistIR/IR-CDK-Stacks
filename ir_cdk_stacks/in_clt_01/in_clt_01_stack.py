
# from aws_cdk.aws_events import Rule
from aws_cdk import (
    aws_s3 as s3,
    core,
    aws_cloudwatch as cloudwatch,
    aws_events as events,
    aws_lambda as _lambda,
    aws_iam as iam,
)

import os

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
                           # targets=[response_lambda])

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

        # 4. Create SNS topic and subscription
        # 5. Create IAM allow/deny policy
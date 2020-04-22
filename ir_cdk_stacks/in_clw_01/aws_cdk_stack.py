from aws_cdk import core


# class AwsCdkStack(core.Stack):

#     def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
#         super().__init__(scope, id, **kwargs)

        # The code that defines your stack goes here


# from aws_cdk.aws_events import Rule
from aws_cdk import (
    aws_s3 as s3,
    core,
    aws_cloudwatch as cloudwatch,
    aws_events as events,
    aws_lambda as _lambda,
)

import os

class AwsCdkStack(core.Stack):

    def _init_(self, scope: core.Construct, id: str, **kwargs) -> None:
        super()._init_(scope, id, **kwargs)

        # The code that defines your stack goes here

        # 1. Create Cloudwatch Rule
        # 2. Make that rule Track Cloudtrail events

        ep = {
            "source": [
                    "aws.logs"
                    ]
            }

        rule = events.Rule(self,
                           "cdkRule_clw",
                           description= 'Rule created by CDK',
                           enabled= True,
                           rule_name= "rulebycdk_clw",
                           event_pattern= ep)

        # 3. Create response lambda and add it as a target of the rule
        lambda_dir_path = os.path.join(os.getcwd(), "aws_cdk")
        response_lambda = _lambda.Function(
            self,
            "InClw01ResponseFunction",
            runtime=_lambda.Runtime.PYTHON_3_8,
            handler="clwUnauthAccessResponse.lambda_handler",
            code=_lambda.Code.from_asset(lambda_dir_path),
            function_name="InClw01ResponseFunction"
        )

        rule.add_target(response_lambda)

        # 4. Create SNS topic and subscription
        # 5. Create IAM allow/deny policy


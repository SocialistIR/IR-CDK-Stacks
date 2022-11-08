import boto3
from aws_cdk import (
    aws_lambda as _lambda,
    aws_iam as iam,
    aws_s3 as _s3,
    aws_s3_notifications,
    core
)

class InApi01Stack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        
        bucket = self.node.try_get_context("input_bucket")
        stack_name = self.node.try_get_context("Stack_Name")
        
        s3 = _s3.Bucket(self, id = bucket)
        
        function = _lambda.Function(self, "lambda_function",
                                    runtime=_lambda.Runtime.PYTHON_2_7, memory_size = 512, #timeout=core.Duration(120),
                                    handler="parser.lambda_handler",
                                    code=_lambda.Code.asset("./lambda"),
                                    environment={
                                            "clf_name": stack_name}
                                            )
                                    
        function.add_to_role_policy(
                iam.PolicyStatement(
                    actions=["s3:*"],
                    effect=iam.Effect.ALLOW,
                    resources=["*"],
                )
            )
        function.add_to_role_policy(
                iam.PolicyStatement(
                    actions=["waf-regional:UpdateIPSet","waf-regional:GetIPSet","waf-regional:GetChangeToken"],
                    effect=iam.Effect.ALLOW,
                    resources=["*"],
                )
            )
        function.add_to_role_policy(
                iam.PolicyStatement(
                    actions=["logs:*"],
                    effect=iam.Effect.ALLOW,
                    resources=["*"],
                )
            )
        function.add_to_role_policy(
                iam.PolicyStatement(
                    actions=["cloudformation:DescribeStacks"],
                    effect=iam.Effect.ALLOW,
                    resources=["*"],
                )
            )
        function.add_to_role_policy(
                iam.PolicyStatement(
                    actions=["SNS:Publish"],
                    effect=iam.Effect.ALLOW,
                    resources=["arn:aws:sns:us-east-1:544820149332:IN-API-01-IPBlocked"],
                )
            )
        function.add_to_role_policy(
                iam.PolicyStatement(
                    actions=["cloudwatch:PutMetricData"],
                    effect=iam.Effect.ALLOW,
                    resources=["*"],
                )
            )
        function.add_to_role_policy(
                iam.PolicyStatement(
                    actions=["lambda:*"],
                    effect=iam.Effect.ALLOW,
                    resources=["*"],
                )
            )

        # create s3 notification for lambda function
        notification = aws_s3_notifications.LambdaDestination(function)

        # assign notification for the s3 event type (ex: OBJECT_CREATED)
        s3.add_event_notification(_s3.EventType.OBJECT_CREATED, notification)

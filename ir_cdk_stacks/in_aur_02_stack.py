from aws_cdk import (
    core,
    aws_lambda as _lambda,
    aws_iam as iam,
    aws_events as events,
    aws_events_targets as targets,
    aws_sns as sns,
    aws_sns_subscriptions as subs,
)
import os
import logging

logger = logging.getLogger(__name__)


class InAur02Stack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        CLUSTER_NAME = self.node.try_get_context("cluster_name")
        NOTIFY_EMAIL = self.node.try_get_context("notify_email")
        SLACK_WEBHOOK_URL = self.node.try_get_context("webhook_url")

        if not CLUSTER_NAME or not NOTIFY_EMAIL or not SLACK_WEBHOOK_URL:
            logger.error(f"Required context variables for {id} were not provided!")
        else:
            # Create explicit deny policy
            policy = iam.ManagedPolicy(
                self,
                "InAur02RdsDenyPolicy",
                managed_policy_name="InAur02RdsDenyPolicy",
                statements=[
                    iam.PolicyStatement(
                        actions=["rds:*", "iam:DetachUserPolicy"],
                        effect=iam.Effect.DENY,
                        resources=["*"],
                    )
                ],
            )

            # Create lambda function
            lambda_dir_path = os.path.join(os.getcwd(), "ir_cdk_stacks", "in_aur_02")
            lambda_func = _lambda.Function(
                self,
                "InAur02ResponseFunction",
                runtime=_lambda.Runtime.PYTHON_3_8,
                handler="response_lambda.lambda_handler",
                code=_lambda.Code.from_asset(lambda_dir_path),
                environment={
                    "webhook_url": SLACK_WEBHOOK_URL,
                    "policy_arn": policy.managed_policy_arn,
                    "cluster_name": CLUSTER_NAME,
                },
            )
            # Assign permissions to response lambda
            lambda_func.add_to_role_policy(
                iam.PolicyStatement(
                    actions=["iam:AttachUserPolicy",],
                    effect=iam.Effect.ALLOW,
                    resources=["*"],
                )
            )

            # Create new SNS topic
            topic = sns.Topic(self, "InAur02DetectionTopic")

            # Add email subscription
            topic.add_subscription(subs.EmailSubscription(NOTIFY_EMAIL))

            # Create new event rule to trigger lambda
            # when there are AWS RDS API calls
            events.Rule(
                self,
                "InAur02DetectionEventRule",
                event_pattern=events.EventPattern(
                    source=["aws.rds"],
                    detail_type=["AWS API Call via CloudTrail"],
                    detail={"eventSource": ["rds.amazonaws.com"]},
                ),
                targets=[
                    targets.LambdaFunction(handler=lambda_func),
                    targets.SnsTopic(topic),
                ],
            )

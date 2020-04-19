from aws_cdk import (
    core,
    aws_cloudwatch as cloudwatch,
    aws_cloudwatch_actions as cw_actions,
    aws_sns as sns,
    aws_logs as logs,
    aws_sns_subscriptions as subs,
    aws_lambda as _lambda,
    aws_lambda_event_sources as lambda_event_sources,
    aws_iam as iam,
    aws_wafv2 as wafv2,
    aws_stepfunctions as sfn,
    aws_stepfunctions_tasks as tasks,
)
import os
import logging

logger = logging.getLogger(__name__)


class InAur01Stack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        CLUSTER_NAME = self.node.try_get_context("cluster_name")
        NOTIFY_EMAIL = self.node.try_get_context("notify_email")
        SLACK_WEBHOOK_URL = self.node.try_get_context("webhook_url")

        if not CLUSTER_NAME or not NOTIFY_EMAIL or not SLACK_WEBHOOK_URL:
            logger.error(f"Required context variables for {id} were not provided!")
        else:
            # Get the log group of our postgres instance
            log_group = logs.LogGroup.from_log_group_name(
                self,
                "InAur01DetectionLogGroup",
                f"/aws/rds/cluster/{CLUSTER_NAME}/postgresql",
            )

            # Create new metric
            metric = cloudwatch.Metric(
                namespace="LogMetrics",
                metric_name="InAur01DetectionFailedDbLoginAttempts",
            )

            # Apply metric filter
            # Filter all metrics of failed login attempts in log
            metric_filter = logs.MetricFilter(
                self,
                "InAur01DetectionMetricFilter",
                log_group=log_group,
                metric_namespace=metric.namespace,
                metric_name=metric.metric_name,
                filter_pattern=logs.FilterPattern.all_terms(
                    "FATAL:  password authentication failed for user"
                ),
                metric_value="1",
            )

            # Create new SNS topic
            topic = sns.Topic(self, "InAur01DetectionTopic")

            # Add email subscription
            topic.add_subscription(subs.EmailSubscription(NOTIFY_EMAIL))

            # Create new alarm for metric
            # Alarm will trigger if there is >= 10 failed login attempts
            # over a period of 30 seconds.
            alarm = cloudwatch.Alarm(
                self,
                "InAur01DetectionAlarm",
                metric=metric,
                threshold=10,
                evaluation_periods=1,
                period=core.Duration.seconds(30),
                datapoints_to_alarm=1,
                statistic="sum",
            )

            # Add SNS action to alarm
            alarm.add_alarm_action(cw_actions.SnsAction(topic))

            # Create new WAF IPSet
            waf = wafv2.CfnIPSet(
                self,
                "InAur01ResponseIpSet",
                addresses=[],
                ip_address_version="IPV4",
                scope="REGIONAL",
                name="InAur01ResponseIpSet",
            )

            # Create unban lambda
            lambda_dir_path = os.path.join(os.getcwd(), "ir_cdk_stacks", "in_aur_01")
            unban_lambda = _lambda.Function(
                self,
                "InAur01ResponseUnbanFunction",
                runtime=_lambda.Runtime.PYTHON_3_8,
                handler="unban_lambda.lambda_handler",
                code=_lambda.Code.from_asset(lambda_dir_path),
                environment={
                    "waf_name": waf.name,
                    "waf_id": waf.attr_id,
                    "waf_scope": waf.scope,
                },
            )
            # Assign WAF permissions to lambda
            unban_lambda.add_to_role_policy(
                iam.PolicyStatement(
                    actions=["wafv2:GetIPSet", "wafv2:UpdateIPSet"],
                    effect=iam.Effect.ALLOW,
                    resources=[waf.attr_arn],
                )
            )
            # Assign EC2 permissions to lambda
            unban_lambda.add_to_role_policy(
                iam.PolicyStatement(
                    actions=["ec2:DeleteNetworkAclEntry"],
                    effect=iam.Effect.ALLOW,
                    resources=["*"],
                )
            )

            # Create stepfunction
            # Define a second state machine to unban the blacklisted IP after 1 hour
            wait_step = sfn.Wait(
                self,
                "InAur01ResponseStepWait",
                time=sfn.WaitTime.duration(core.Duration.hours(1)),
            )
            unban_step = sfn.Task(
                self,
                "InAur01ResponseStepUnban",
                task=tasks.RunLambdaTask(
                    unban_lambda,
                    integration_pattern=sfn.ServiceIntegrationPattern.FIRE_AND_FORGET,
                ),
                parameters={"Payload.$": "$"},
            )
            statemachine = sfn.StateMachine(
                self,
                "InAur01ResponseUnbanStateMachine",
                definition=wait_step.next(unban_step),
                timeout=core.Duration.hours(1.5),
            )

            # Create lambda function
            lambda_func = _lambda.Function(
                self,
                "InAur01ResponseFunction",
                runtime=_lambda.Runtime.PYTHON_3_8,
                handler="response_lambda.lambda_handler",
                code=_lambda.Code.from_asset(lambda_dir_path),
                environment={
                    "webhook_url": SLACK_WEBHOOK_URL,
                    "waf_name": waf.name,
                    "waf_id": waf.attr_id,
                    "waf_scope": waf.scope,
                    "unban_sm_arn": statemachine.state_machine_arn,
                    "cluster_name": CLUSTER_NAME,
                },
            )
            # AWS CDK has a bug where it would not add the correct permission
            # to the lambda for Cloudwatch log subscription to invoke it.
            # Hence, we need to manually add permission to lambda.
            lambda_func.add_permission(
                "InAur01ResponseFunctionInvokePermission",
                principal=iam.ServicePrincipal("logs.amazonaws.com"),
                action="lambda:InvokeFunction",
                source_arn=log_group.log_group_arn + ":*",
            )
            # Assign permissions to response lambda
            lambda_func.add_to_role_policy(
                iam.PolicyStatement(
                    actions=[
                        "wafv2:GetIPSet",
                        "wafv2:UpdateIPSet",
                        "states:StartExecution",
                    ],
                    effect=iam.Effect.ALLOW,
                    resources=[waf.attr_arn, statemachine.state_machine_arn],
                )
            )
            # Assign RDS Read-only permissions to lambda
            lambda_func.add_to_role_policy(
                iam.PolicyStatement(
                    actions=["rds:Describe*"], effect=iam.Effect.ALLOW, resources=["*"],
                )
            )
            # Assign EC2 permissions to lambda
            lambda_func.add_to_role_policy(
                iam.PolicyStatement(
                    actions=[
                        "ec2:Describe*",
                        "ec2:CreateNetworkAclEntry",
                        "ec2:DeleteNetworkAclEntry",
                    ],
                    effect=iam.Effect.ALLOW,
                    resources=["*"],
                )
            )
            # Assign CloudWatch logs permissions to lambda
            lambda_func.add_to_role_policy(
                iam.PolicyStatement(
                    actions=[
                        "cloudwatch:Get*",
                        "cloudwatch:Describe*",
                        "logs:FilterLogEvents",
                        "logs:DescribeMetricFilters",
                    ],
                    effect=iam.Effect.ALLOW,
                    resources=["*"],
                )
            )

            sns_event_source = lambda_event_sources.SnsEventSource(topic)
            lambda_func.add_event_source(sns_event_source)

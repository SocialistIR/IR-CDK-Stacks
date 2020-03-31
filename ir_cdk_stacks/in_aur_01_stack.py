from aws_cdk import (
    core,
    aws_cloudwatch as cloudwatch,
    aws_cloudwatch_actions as cw_actions,
    aws_sns as sns,
    aws_logs as logs,
    aws_sns_subscriptions as subs,
    aws_logs_destinations as logs_destinations,
    aws_lambda as _lambda,
    aws_iam as iam,
)
import os


class InAur01Stack(core.Stack):

    METRIC_NAMESPACE = "LogMetrics"
    METRIC_NAME = "InAur01DetectionFailedDbLoginAttempts"
    NOTIFY_EMAIL = "z5161477@unsw.edu.au"

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Get the log group of our postgres instance
        log_group = logs.LogGroup.from_log_group_name(
            self, "InAur01DetectionLogGroup", "/aws/rds/instance/testdb/postgresql"
        )

        # Create new metric
        metric = cloudwatch.Metric(
            namespace=self.METRIC_NAMESPACE, metric_name=self.METRIC_NAME
        )

        # Apply metric filter
        # Filter all metrics of failed login attempts in log
        filter_pattern = logs.FilterPattern.all_terms(
            "FATAL:  password authentication failed for user"
        )
        metric_filter = logs.MetricFilter(
            self,
            "InAur01DetectionMetricFilter",
            log_group=log_group,
            metric_namespace=self.METRIC_NAMESPACE,
            metric_name=self.METRIC_NAME,
            filter_pattern=filter_pattern,
            metric_value="1",
        )

        # Create new SNS topic
        topic = sns.Topic(self, "InAur01DetectionTopic")

        # Add email subscription
        topic.add_subscription(subs.EmailSubscription(self.NOTIFY_EMAIL))

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

        # Create lambda function
        dir_path = os.path.join(os.getcwd(), "ir_cdk_stacks", "in_aur_01")
        lambda_func = _lambda.Function(
            self,
            "InAur01ResponseFunction",
            runtime=_lambda.Runtime.PYTHON_3_8,
            handler="response_lambda.lambda_handler",
            code=_lambda.Code.from_asset(dir_path),
        )
        # AWS CDK has a bug where it would not add the correct permission
        # to the lambda for Cloudwatch log subscription to invoke it.
        # Hence, we need to manually add permission to lambda.
        lambda_func.add_permission(
            "InAur01ResponseFunctionInvokePermission",
            principal=iam.ServicePrincipal("logs.amazonaws.com"),
            action="lambda:InvokeFunction",
            source_arn=log_group.log_group_arn + ":*"
        )

        # Set source for lambda trigger
        lambda_destination = logs_destinations.LambdaDestination(lambda_func)
        log_group.add_subscription_filter("InAur01ResponseSubscriptionFilter",
            destination=lambda_destination, filter_pattern=filter_pattern
        )

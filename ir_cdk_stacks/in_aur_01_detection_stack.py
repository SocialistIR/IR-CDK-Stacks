from aws_cdk import (core, aws_cloudwatch as cloudwatch, aws_cloudwatch_actions as cw_actions, aws_sns as sns, aws_logs as logs, aws_sns_subscriptions as subs)

class InAur01DetectionStack(core.Stack):

    METRIC_NAMESPACE = "LogMetrics"
    METRIC_NAME = "InAur01DetectionFailedDbLoginAttempts"
    NOTIFY_EMAIL = ""

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Get the log group of our postgres instance
        log_group = logs.LogGroup.from_log_group_name(self, "InAur01DetectionLogGroup", "/aws/rds/instance/testdb/postgresql")

        # Create new metric
        metric = cloudwatch.Metric(
            namespace=self.METRIC_NAMESPACE,
            metric_name=self.METRIC_NAME
        )

        # Apply metric filter
        # Filter all metrics of failed login attempts in log
        metric_filter = logs.MetricFilter(self, "MetricFilter",
            log_group=log_group,
            metric_namespace=self.METRIC_NAMESPACE,
            metric_name=self.METRIC_NAME,
            filter_pattern=logs.FilterPattern.all_terms("FATAL: password authentication failed for user"),
            metric_value="1"
        )

        # Create new SNS topic
        topic = sns.Topic(self, "InAur01DetectionTopic")

        # Add email subscription
        topic.add_subscription(subs.EmailSubscription(self.NOTIFY_EMAIL))

        # Create new alarm for metric
        # Alarm will trigger if there is >= 10 failed login attempts
        # over a period of 30 seconds.
        alarm = cloudwatch.Alarm(self, "InAur01DetectionAlarm",
            metric=metric,
            threshold=10,
            evaluation_periods=1,
            period=core.Duration.seconds(30),
            datapoints_to_alarm=1,
            statistic="sum"
        )

        # Add SNS action to alarm
        alarm.add_alarm_action(cw_actions.SnsAction(topic))
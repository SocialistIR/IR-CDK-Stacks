from aws_cdk import (
    core,
    aws_iam as iam,
    aws_lambda as _lambda,
    aws_s3 as s3,
    aws_s3_notifications as s3_notifications,
    aws_stepfunctions as sfn,
    aws_stepfunctions_tasks as tasks,
    aws_wafv2 as wafv2,
    aws_kinesisfirehose as firehose,
    aws_events as events,
    aws_events_targets as targets,
)
import os
import logging
import jsii
from datetime import timezone, datetime, timedelta

# Fields to match
ALL_QUERY_ARGS = wafv2.CfnRuleGroup.FieldToMatchProperty(
    all_query_arguments={"Name": "all query arguments"})
BODY = wafv2.CfnRuleGroup.FieldToMatchProperty(body={"Name": "body"})
QUERY_STRING = wafv2.CfnRuleGroup.FieldToMatchProperty(
    query_string={"Name": "query string"})
SINGLE_HEADER = wafv2.CfnRuleGroup.FieldToMatchProperty(
    single_header={"Name": "single header"})
SINGLE_QUERY_ARG = wafv2.CfnRuleGroup.FieldToMatchProperty(
    single_query_argument={"Name": "single query argument"})
URI_PATH = wafv2.CfnRuleGroup.FieldToMatchProperty(
    uri_path={"Name": "uri path"})

NO_TEXT_TRANSFORMATION = wafv2.CfnRuleGroup.TextTransformationProperty(
    priority=7, type="NONE")


@jsii.implements(wafv2.CfnRuleGroup.IPSetReferenceStatementProperty)
class IPSetReferenceStatement:
    @property
    def arn(self):
        return self._arn

    @arn.setter
    def arn(self, value):
        self._arn = value


class Ext06Stack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        try:
            API_ARN = self.node.try_get_context("api_arn")
            # Create rate based rule
            rbr_statement = wafv2.CfnRuleGroup.RateBasedStatementOneProperty(aggregate_key_type="IP", limit=100)

            # Create new WAF IPSet
            doslist = wafv2.CfnIPSet(
                self,
                "Ext06DosIpSet",
                addresses=[],
                ip_address_version="IPV4",
                scope="REGIONAL",
                name="Ext06DosIpSet",
            )

            suslist = wafv2.CfnIPSet(
                self,
                "Ext06SusIpSet",
                addresses=[],
                ip_address_version="IPV4",
                scope="REGIONAL",
                name="Ext06SusIpSet",
            )

            # Create reference statements

            # Currently IPSetReference is bugged
            #blacklist_ref = wafv2.CfnWebACL.IPSetReferenceStatementProperty()
            #ip_set_ref_stmnt = IPSetReferenceStatement()
            #ip_set_ref_stmnt.arn = blacklist.attr_arn

            # Create a WAF
            waf = wafv2.CfnWebACL(
                self,
                id="Ext06_WAF",
                default_action=wafv2.CfnWebACL.DefaultActionProperty(allow={}),
                scope="REGIONAL",
                visibility_config=wafv2.CfnWebACL.VisibilityConfigProperty(
                    cloud_watch_metrics_enabled=True,
                    metric_name="EXT06_WAF",
                    sampled_requests_enabled=True
                ),
                rules=[
                    wafv2.CfnWebACL.RuleProperty(
                        name="Spam",
                        priority=1,
                        statement=wafv2.CfnWebACL.StatementOneProperty(rate_based_statement=rbr_statement),
                        visibility_config=wafv2.CfnWebACL.VisibilityConfigProperty(
                            cloud_watch_metrics_enabled=False,
                            metric_name="rbr_requests",
                            sampled_requests_enabled=False
                        ),
                        override_action=wafv2.CfnWebACL.OverrideActionProperty(
                            none={}
                        ),
                    ),
                ],
            )

            # Create Susunban lambda
            lambda_dir_path = os.path.join(
                os.getcwd(), "ir_cdk_stacks", "ext_06")
            susunban_lambda = _lambda.Function(
                self,
                "Ext06ResponseSusUnbanFunction",
                runtime=_lambda.Runtime.PYTHON_3_8,
                handler="susunban_lambda.lambda_handler",
                code=_lambda.Code.from_asset(lambda_dir_path),
                environment={
                    "ipset_id": suslist.attr_id,
                    "ipset_name": suslist.name,
                    "ipset_scope": suslist.scope,
                }
            )
            # Assign WAF permissions to lambda
            susunban_lambda.add_to_role_policy(
                iam.PolicyStatement(
                    actions=["wafv2:GetIPSet", "wafv2:UpdateIPSet"],
                    effect=iam.Effect.ALLOW,
                    resources=[suslist.attr_arn],
                )
            )

            # Create Dosunban lambda
            lambda_dir_path = os.path.join(
                os.getcwd(), "ir_cdk_stacks", "ext_06")
            dosunban_lambda = _lambda.Function(
                self,
                "Ext06ResponseDosUnbanFunction",
                runtime=_lambda.Runtime.PYTHON_3_8,
                handler="dosunban_lambda.lambda_handler",
                code=_lambda.Code.from_asset(lambda_dir_path),
                environment={
                    "ipset_id": doslist.attr_id,
                    "ipset_name": doslist.name,
                    "ipset_scope": doslist.scope,
                }
            )
            # Assign WAF permissions to lambda
            dosunban_lambda.add_to_role_policy(
                iam.PolicyStatement(
                    actions=["wafv2:GetIPSet", "wafv2:UpdateIPSet"],
                    effect=iam.Effect.ALLOW,
                    resources=[doslist.attr_arn],
                )
            )

            # Create dos stepfunction
            # Define a second state machine to unban the blacklisted IP after 1 hour
            wait_step = sfn.Wait(
                self,
                "Ext06ResponseStepWait",
                time=sfn.WaitTime.duration(core.Duration.hours(1)),
            )
            dosunban_step = sfn.Task(
                self,
                "Ext06ResponseStepUnban",
                task=tasks.RunLambdaTask(
                    dosunban_lambda,
                    integration_pattern=sfn.ServiceIntegrationPattern.FIRE_AND_FORGET,
                ),
            )
            susunban_step = sfn.Task(
                self,
                "Ext06ResponseStepUnban",
                task=tasks.RunLambdaTask(
                    susunban_lambda,
                    integration_pattern=sfn.ServiceIntegrationPattern.FIRE_AND_FORGET,
                ),
            )
            dos_statemachine = sfn.StateMachine(
                self,
                "Ext06ResponseUnbanStateMachine",
                definition=wait_step.next(dosunban_step),
                timeout=core.Duration.hours(1.5),
            )
            sus_statemachine = sfn.StateMachine(
                self,
                "Ext06ResponseUnbanStateMachine",
                definition=wait_step.next(susunban_step),
                timeout=core.Duration.hours(1.5),
            )

            # Create lambda function
            lambda_func = _lambda.Function(
                self,
                "Ext06ResponseFunction",
                runtime=_lambda.Runtime.PYTHON_3_8,
                handler="response_lambda.lambda_handler",
                code=_lambda.Code.from_asset(lambda_dir_path),
                environment={
                    "suslist_id": suslist.attr_id,
                    "suslist_name": suslist.name,
                    "suslist_scope": suslist.scope,
                    "doslist_id": doslist.attr_id,
                    "doslist_name": doslist.name,
                    "doslist_scope": doslist.scope,
                    "dos_arn": dos_statemachine.state_machine_arn,
                    "sus_arn": sus_statemachine.state_machine_arn,
                },
            )

            kinesis_log = s3.Bucket(
                self,
                id='dos_logs',
                access_control=s3.BucketAccessControl.PUBLIC_READ_WRITE,
            )

            # Assign permissions to response lambda
            lambda_func.add_to_role_policy(
                iam.PolicyStatement(
                    actions=[
                        "wafv2:GetIPSet",
                        "wafv2:UpdateIPSet",
                        "states:StartExecution",
                        "s3:GetObject",
                    ],
                    effect=iam.Effect.ALLOW,
                    resources=[doslist.attr_arn, suslist.attr_arn, sus_statemachine.state_machine_arn, dos_statemachine.state_machine_arn,
                               kinesis_log.bucket_arn, kinesis_log.bucket_arn, kinesis_log.bucket_arn + "/*"],
                )
            )

            # Create an IAM role for the steram
            stream_role = iam.Role(
                self,
                id="waf-kinesis-log-role",
                assumed_by=iam.ServicePrincipal(
                    service="firehose.amazonaws.com",),
            )

            stream_permissions = iam.Policy(
                self,
                id="Ext-06-kinesis-permissions",
                statements=[
                    iam.PolicyStatement(
                        actions=[
                            "s3:AbortMultipartUpload",
                            "s3:GetBucketLocation",
                            "s3:GetObject",
                            "s3:ListBucket",
                            "s3:ListBucketMultipartUploads",
                            "s3:PutObject",
                        ],
                        effect=iam.Effect.ALLOW,
                        resources=[kinesis_log.bucket_arn,
                                   kinesis_log.bucket_arn + "/*"],
                    )
                ]
            )

            stream_role.attach_inline_policy(stream_permissions)

            log_stream = firehose.CfnDeliveryStream(
                self,
                id="aws-waf-logs-ext06",
                delivery_stream_type="DirectPut",
                delivery_stream_name="aws-waf-logs-ext06",
                s3_destination_configuration=firehose.CfnDeliveryStream.S3DestinationConfigurationProperty(
                    bucket_arn=kinesis_log.bucket_arn,
                    buffering_hints=firehose.CfnDeliveryStream.BufferingHintsProperty(
                        interval_in_seconds=300,
                        size_in_m_bs=5
                    ),
                    compression_format="UNCOMPRESSED",
                    role_arn=stream_role.role_arn
                ),
            )
            kinesis_log.add_event_notification(
                s3.EventType.OBJECT_CREATED, dest=s3_notifications.LambdaDestination(lambda_func))
            utc_time = datetime.now(tz=timezone.utc)
            utc_time = utc_time + timedelta(minutes=5)
            cron_string = "cron(" + str(utc_time.minute) + " " + str(utc_time.hour) + " " + str(
                utc_time.day) + " " + str(utc_time.month) + " ? " + str(utc_time.year) + ")"
            trigger = events.Rule(
                self,
                id="ext-06 setup",
                rule_name="Ext06-trigger",
                schedule=events.Schedule.expression(cron_string)
            )

            setup_dir_path = os.path.join(
                os.getcwd(), "ir_cdk_stacks", "ext_06")
            setup_func = _lambda.Function(
                self,
                id="Ext06Setup",
                runtime=_lambda.Runtime.PYTHON_3_8,
                handler="setup.lambda_handler",
                code=_lambda.Code.from_asset(setup_dir_path),
                environment={
                    "waf_arn": waf.attr_arn,
                    "firehose_arn": log_stream.attr_arn,
                    "rule_name": "Ext06-trigger",

                },
            )

            # Assign permissions to setup lambda
            setup_func.add_to_role_policy(
                iam.PolicyStatement(
                    actions=["wafv2:PutLoggingConfiguration"],
                    effect=iam.Effect.ALLOW,
                    resources=[waf.attr_arn],
                )
            )

            setup = targets.LambdaFunction(
                handler=setup_func,
            )

            setup.bind(rule=trigger)
            trigger.add_target(target=setup)

            wafv2.CfnWebACLAssociation(
                self,
                id="API gateway association",
                resource_arn=API_ARN,
                web_acl_arn=waf.attr_arn,
            )

        except Exception:
            logging.error(
                f"Required context variables for {id} were not provided!")

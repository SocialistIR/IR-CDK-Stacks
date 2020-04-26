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


class Ext06Stack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        try:
            API_ARN = self.node.try_get_context("api_arn")
            # Create the WAF IPSets
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
                name="Ext06-WAF",
                default_action=wafv2.CfnWebACL.DefaultActionProperty(allow={}),
                scope="REGIONAL",
                visibility_config=wafv2.CfnWebACL.VisibilityConfigProperty(
                    cloud_watch_metrics_enabled=True,
                    metric_name="EXT06_WAF",
                    sampled_requests_enabled=True
                ),
                rules=[
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
            doswait_step = sfn.Wait(
                self,
                "Ext06ResponseStepDosWait",
                time=sfn.WaitTime.duration(core.Duration.hours(1)),
            )
            suswait_step = sfn.Wait(
                self,
                "Ext06ResponseStepSusWait",
                time=sfn.WaitTime.duration(core.Duration.hours(1)),
            )
            dosunban_step = sfn.Task(
                self,
                "Ext06ResponseStepDosUnban",
                task=tasks.RunLambdaTask(
                    dosunban_lambda,
                    integration_pattern=sfn.ServiceIntegrationPattern.FIRE_AND_FORGET,
                    payload={"Input.$": "$"},
                ),
            )
            susunban_step = sfn.Task(
                self,
                "Ext06ResponseStepSosUnban",
                task=tasks.RunLambdaTask(
                    susunban_lambda,
                    integration_pattern=sfn.ServiceIntegrationPattern.FIRE_AND_FORGET,
                    payload={"Input.$": "$"},
                ),
            )
            dos_statemachine = sfn.StateMachine(
                self,
                "Ext06ResponseDosUnbanStateMachine",
                definition=doswait_step.next(dosunban_step),
                timeout=core.Duration.hours(1.5),
            )

            sus_statemachine = sfn.StateMachine(
                self,
                "Ext06ResponseSusUnbanStateMachine",
                definition=suswait_step.next(susunban_step),
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
                    "waf_id": waf.attr_id,
                    "waf_scope": waf.scope,
                    "waf_name": waf.name,
                    "firehose_arn": log_stream.attr_arn,
                    "rule_name": "Ext06-trigger",
                    "doslist_arn": doslist.attr_arn,
                    "rate": "100",
                },
            )
            
            # Assign permissions to setup lambda
            setup_func.add_to_role_policy(
                iam.PolicyStatement(
                    actions=["wafv2:PutLoggingConfiguration", "wafv2:GetWebACL", "wafv2:UpdateWebACL"],
                    effect=iam.Effect.ALLOW,
                    resources=[waf.attr_arn, doslist.attr_arn],
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
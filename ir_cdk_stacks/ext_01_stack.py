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
import boto3
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


class Ext01Stack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        try:
            API_ARN = self.node.try_get_context("api_arn")

            # Create XSS rule
            xss_body = wafv2.CfnRuleGroup.StatementOneProperty(xss_match_statement=wafv2.CfnRuleGroup.XssMatchStatementProperty(
                field_to_match=BODY, text_transformations=[NO_TEXT_TRANSFORMATION]))
            xss_query_string = wafv2.CfnRuleGroup.StatementOneProperty(xss_match_statement=wafv2.CfnRuleGroup.XssMatchStatementProperty(
                field_to_match=QUERY_STRING, text_transformations=[NO_TEXT_TRANSFORMATION]))
            xss_uri = wafv2.CfnRuleGroup.StatementOneProperty(xss_match_statement=wafv2.CfnRuleGroup.XssMatchStatementProperty(
                field_to_match=URI_PATH, text_transformations=[NO_TEXT_TRANSFORMATION]))
            xss_header = wafv2.CfnRuleGroup.StatementOneProperty(xss_match_statement=wafv2.CfnRuleGroup.XssMatchStatementProperty(
                field_to_match=SINGLE_HEADER, text_transformations=[NO_TEXT_TRANSFORMATION]))

            xss_rule_group = wafv2.CfnRuleGroup(
                self,
                id="XSS",
                capacity=160,
                scope="REGIONAL",
                visibility_config=wafv2.CfnRuleGroup.VisibilityConfigProperty(
                    cloud_watch_metrics_enabled=True,
                    metric_name="xss_attacks",
                    sampled_requests_enabled=False
                ),
                rules=[
                    wafv2.CfnRuleGroup.RuleProperty(
                        name="xss_query_string",
                        priority=1,
                        statement=xss_query_string,
                        action=wafv2.CfnRuleGroup.RuleActionProperty(block={}),
                        visibility_config=wafv2.CfnRuleGroup.VisibilityConfigProperty(
                            cloud_watch_metrics_enabled=False,
                            metric_name="xss_attacks",
                            sampled_requests_enabled=False
                        ),
                    ),
                    wafv2.CfnRuleGroup.RuleProperty(
                        name="xss_body",
                        priority=2,
                        statement=xss_body,
                        action=wafv2.CfnRuleGroup.RuleActionProperty(block={}),
                        visibility_config=wafv2.CfnRuleGroup.VisibilityConfigProperty(
                            cloud_watch_metrics_enabled=False,
                            metric_name="xss_attacks",
                            sampled_requests_enabled=False
                        )
                    ),
                    wafv2.CfnRuleGroup.RuleProperty(
                        name="xss_uri",
                        priority=3,
                        statement=xss_uri,
                        action=wafv2.CfnRuleGroup.RuleActionProperty(block={}),
                        visibility_config=wafv2.CfnRuleGroup.VisibilityConfigProperty(
                            cloud_watch_metrics_enabled=False,
                            metric_name="xss_attacks",
                            sampled_requests_enabled=False
                        )
                    ),
                    wafv2.CfnRuleGroup.RuleProperty(
                        name="xss_header",
                        priority=4,
                        statement=xss_header,
                        action=wafv2.CfnRuleGroup.RuleActionProperty(block={}),
                        visibility_config=wafv2.CfnRuleGroup.VisibilityConfigProperty(
                            cloud_watch_metrics_enabled=False,
                            metric_name="xss_attacks",
                            sampled_requests_enabled=False
                        ),
                    ),
                ],
            )

            # Create the SQLI rule group
            sqli_body = wafv2.CfnRuleGroup.StatementOneProperty(sqli_match_statement=wafv2.CfnRuleGroup.SqliMatchStatementProperty(
                field_to_match=BODY, text_transformations=[NO_TEXT_TRANSFORMATION]))
            sqli_query_string = wafv2.CfnRuleGroup.StatementOneProperty(sqli_match_statement=wafv2.CfnRuleGroup.SqliMatchStatementProperty(
                field_to_match=QUERY_STRING, text_transformations=[NO_TEXT_TRANSFORMATION]))
            sqli_uri = wafv2.CfnRuleGroup.StatementOneProperty(sqli_match_statement=wafv2.CfnRuleGroup.SqliMatchStatementProperty(
                field_to_match=URI_PATH, text_transformations=[NO_TEXT_TRANSFORMATION]))
            sqli_header = wafv2.CfnRuleGroup.StatementOneProperty(sqli_match_statement=wafv2.CfnRuleGroup.SqliMatchStatementProperty(
                field_to_match=SINGLE_HEADER, text_transformations=[NO_TEXT_TRANSFORMATION]))

            sqli_rule_group = wafv2.CfnRuleGroup(
                self,
                id="SQLI",
                capacity=80,
                scope="REGIONAL",
                visibility_config=wafv2.CfnRuleGroup.VisibilityConfigProperty(
                    cloud_watch_metrics_enabled=True,
                    metric_name="sqli_attacks",
                    sampled_requests_enabled=False
                ),
                rules=[
                    wafv2.CfnRuleGroup.RuleProperty(
                        name="sqli_query_string",
                        priority=1,
                        statement=sqli_query_string,
                        action=wafv2.CfnRuleGroup.RuleActionProperty(block={}),
                        visibility_config=wafv2.CfnRuleGroup.VisibilityConfigProperty(
                            cloud_watch_metrics_enabled=False,
                            metric_name="sqli_attacks",
                            sampled_requests_enabled=False
                        ),
                    ),
                    wafv2.CfnRuleGroup.RuleProperty(
                        name="sqli_body",
                        priority=2,
                        statement=sqli_body,
                        action=wafv2.CfnRuleGroup.RuleActionProperty(block={}),
                        visibility_config=wafv2.CfnRuleGroup.VisibilityConfigProperty(
                            cloud_watch_metrics_enabled=False,
                            metric_name="sqli_attacks",
                            sampled_requests_enabled=False
                        )
                    ),
                    wafv2.CfnRuleGroup.RuleProperty(
                        name="sqli_uri",
                        priority=3,
                        statement=sqli_uri,
                        action=wafv2.CfnRuleGroup.RuleActionProperty(block={}),
                        visibility_config=wafv2.CfnRuleGroup.VisibilityConfigProperty(
                            cloud_watch_metrics_enabled=False,
                            metric_name="sqli_attacks",
                            sampled_requests_enabled=False
                        )
                    ),
                    wafv2.CfnRuleGroup.RuleProperty(
                        name="sqli_header",
                        priority=4,
                        statement=sqli_header,
                        action=wafv2.CfnRuleGroup.RuleActionProperty(block={}),
                        visibility_config=wafv2.CfnRuleGroup.VisibilityConfigProperty(
                            cloud_watch_metrics_enabled=False,
                            metric_name="sqli_attacks",
                            sampled_requests_enabled=False
                        ),
                    ),
                ],
            )

            # Create the LFI and path traversal sets
            regex_pattern_set = wafv2.CfnRegexPatternSet(self, id="Ext01LptSet", regular_expression_list=[
                                                         ".*\.\./.*", ".*://.*"], scope="REGIONAL")
            lpt_query_string = wafv2.CfnRuleGroup.StatementOneProperty(regex_pattern_set_reference_statement=wafv2.CfnRuleGroup.RegexPatternSetReferenceStatementProperty(
                arn=regex_pattern_set.attr_arn, field_to_match=QUERY_STRING, text_transformations=[NO_TEXT_TRANSFORMATION]))
            lpt_uri = wafv2.CfnRuleGroup.StatementOneProperty(regex_pattern_set_reference_statement=wafv2.CfnRuleGroup.RegexPatternSetReferenceStatementProperty(
                arn=regex_pattern_set.attr_arn, field_to_match=URI_PATH, text_transformations=[NO_TEXT_TRANSFORMATION]))

            lpt_rule_group = wafv2.CfnRuleGroup(
                self,
                id="LPT",
                capacity=50,
                scope="REGIONAL",
                visibility_config=wafv2.CfnRuleGroup.VisibilityConfigProperty(
                    cloud_watch_metrics_enabled=True,
                    metric_name="lpt_attacks",
                    sampled_requests_enabled=False
                ),
                rules=[
                    wafv2.CfnRuleGroup.RuleProperty(
                        name="lpt_query_string",
                        priority=1,
                        statement=lpt_query_string,
                        action=wafv2.CfnRuleGroup.RuleActionProperty(block={}),
                        visibility_config=wafv2.CfnRuleGroup.VisibilityConfigProperty(
                            cloud_watch_metrics_enabled=False,
                            metric_name="lpt_attacks",
                            sampled_requests_enabled=False
                        ),
                    ),
                    wafv2.CfnRuleGroup.RuleProperty(
                        name="lpt_uri",
                        priority=2,
                        statement=lpt_uri,
                        action=wafv2.CfnRuleGroup.RuleActionProperty(block={}),
                        visibility_config=wafv2.CfnRuleGroup.VisibilityConfigProperty(
                            cloud_watch_metrics_enabled=False,
                            metric_name="lpt_attacks",
                            sampled_requests_enabled=False
                        )
                    ),
                ],
            )

            # Create new WAF IPSet
            blacklist = wafv2.CfnIPSet(
                self,
                "Ext01ResponseIpSet",
                addresses=[],
                ip_address_version="IPV4",
                scope="REGIONAL",
                name="Ext01ResponseIpSet",
            )

            # Create reference statements
            xss_ref = wafv2.CfnWebACL.RuleGroupReferenceStatementProperty(
                arn=xss_rule_group.attr_arn)
            sqli_ref = wafv2.CfnWebACL.RuleGroupReferenceStatementProperty(
                arn=sqli_rule_group.attr_arn)
            lpt_ref = wafv2.CfnWebACL.RuleGroupReferenceStatementProperty(
                arn=lpt_rule_group.attr_arn)

            # Currently IPSetReference is bugged
            #blacklist_ref = wafv2.CfnWebACL.IPSetReferenceStatementProperty()
            ip_set_ref_stmnt = IPSetReferenceStatement()
            ip_set_ref_stmnt.arn = blacklist.attr_arn

            # Create a WAF
            waf = wafv2.CfnWebACL(
                self,
                id="Ext01_WAF",
                default_action=wafv2.CfnWebACL.DefaultActionProperty(allow={}),
                scope="REGIONAL",
                visibility_config=wafv2.CfnWebACL.VisibilityConfigProperty(
                    cloud_watch_metrics_enabled=True,
                    metric_name="EXT01_WAF",
                    sampled_requests_enabled=True
                ),
                rules=[
                    wafv2.CfnWebACL.RuleProperty(
                        name="SQLI",
                        priority=2,
                        statement=wafv2.CfnWebACL.StatementOneProperty(
                            rule_group_reference_statement=sqli_ref),
                        visibility_config=wafv2.CfnWebACL.VisibilityConfigProperty(
                            cloud_watch_metrics_enabled=False,
                            metric_name="sqli_requests",
                            sampled_requests_enabled=False
                        ),
                        override_action=wafv2.CfnWebACL.OverrideActionProperty(
                            none={}
                        ),
                    ),
                    wafv2.CfnWebACL.RuleProperty(
                        name="XSS",
                        priority=3,
                        statement=wafv2.CfnWebACL.StatementOneProperty(
                            rule_group_reference_statement=xss_ref),
                        visibility_config=wafv2.CfnWebACL.VisibilityConfigProperty(
                            cloud_watch_metrics_enabled=False,
                            metric_name="xss_requests",
                            sampled_requests_enabled=False
                        ),
                        override_action=wafv2.CfnWebACL.OverrideActionProperty(
                            none={}
                        ),
                    ),
                    wafv2.CfnWebACL.RuleProperty(
                        name="LPT",
                        priority=4,
                        statement=wafv2.CfnWebACL.StatementOneProperty(
                            rule_group_reference_statement=lpt_ref),
                        visibility_config=wafv2.CfnWebACL.VisibilityConfigProperty(
                            cloud_watch_metrics_enabled=False,
                            metric_name="lpt_requests",
                            sampled_requests_enabled=False
                        ),
                        override_action=wafv2.CfnWebACL.OverrideActionProperty(
                            none={}
                        ),
                    ),
                ],
            )

            # Create unban lambda
            lambda_dir_path = os.path.join(
                os.getcwd(), "ir_cdk_stacks", "ext_01")
            unban_lambda = _lambda.Function(
                self,
                "Ext01ResponseUnbanFunction",
                runtime=_lambda.Runtime.PYTHON_3_8,
                handler="unban_lambda.lambda_handler",
                code=_lambda.Code.from_asset(lambda_dir_path),
                environment={
                    "ipset_id": blacklist.attr_id,
                    "ipset_name": blacklist.name,
                    "ipset_scope": blacklist.scope,
                }
            )
            # Assign WAF permissions to lambda
            unban_lambda.add_to_role_policy(
                iam.PolicyStatement(
                    actions=["wafv2:GetIPSet", "wafv2:UpdateIPSet"],
                    effect=iam.Effect.ALLOW,
                    resources=[blacklist.attr_arn],
                )
            )

            # Create stepfunction
            # Define a second state machine to unban the blacklisted IP after 1 hour
            wait_step = sfn.Wait(
                self,
                "Ext01ResponseStepWait",
                time=sfn.WaitTime.duration(core.Duration.hours(1)),
            )
            unban_step = sfn.Task(
                self,
                "Ext01ResponseStepUnban",
                task=tasks.RunLambdaTask(
                    unban_lambda,
                    integration_pattern=sfn.ServiceIntegrationPattern.FIRE_AND_FORGET,
                ),
            )
            statemachine = sfn.StateMachine(
                self,
                "Ext01ResponseUnbanStateMachine",
                definition=wait_step.next(unban_step),
                timeout=core.Duration.hours(1.5),
            )

            # Create lambda function
            lambda_func = _lambda.Function(
                self,
                "Ext01ResponseFunction",
                runtime=_lambda.Runtime.PYTHON_3_8,
                handler="response_lambda.lambda_handler",
                code=_lambda.Code.from_asset(lambda_dir_path),
                environment={
                    "ipset_id": blacklist.attr_id,
                    "ipset_name": blacklist.name,
                    "ipset_scope": blacklist.scope,
                    "sfn_arn": statemachine.state_machine_arn,
                },
            )

            kinesis_log = s3.Bucket(
                self,
                id='waf_logs',
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
                    resources=[blacklist.attr_arn, statemachine.state_machine_arn,
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
                id="Ext-01-kinesis-permissions",
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
                id="aws-waf-logs-ext01",
                delivery_stream_type="DirectPut",
                delivery_stream_name="aws-waf-logs-ext01",
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
                id="ext-01 setup",
                rule_name="Ext01-trigger",
                schedule=events.Schedule.expression(cron_string)
            )

            setup_dir_path = os.path.join(
                os.getcwd(), "ir_cdk_stacks", "ext_01")
            setup_func = _lambda.Function(
                self,
                id="Ext01Setup",
                runtime=_lambda.Runtime.PYTHON_3_8,
                handler="setup.lambda_handler",
                code=_lambda.Code.from_asset(setup_dir_path),
                environment={
                    "waf_arn": waf.attr_arn,
                    "firehose_arn": log_stream.attr_arn,
                    "rule_name": "Ext01-trigger",

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

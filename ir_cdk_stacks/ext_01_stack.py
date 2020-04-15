from aws_cdk import (
    core,
    aws_iam as iam,
    aws_lambda as _lambda,
    aws_s3 as s3,
    aws_s3_notifications as s3_notifications,
    aws_stepfunctions as sfn,
    aws_stepfunctions_tasks as tasks,
    aws_wafv2 as wafv2,
)
import os
import logging

#Fields to match
ALL_QUERY_ARGS = wafv2.CfnRuleGroup.FieldToMatchProperty(all_query_arguments={"Name": "all query arguments"})
BODY = wafv2.CfnRuleGroup.FieldToMatchProperty(body={"Name": "body"})
QUERY_STRING = wafv2.CfnRuleGroup.FieldToMatchProperty(query_string= {"Name": "query string"})
SINGLE_HEADER = wafv2.CfnRuleGroup.FieldToMatchProperty(single_header= {"Name": "single header"})
SINGLE_QUERY_ARG = wafv2.CfnRuleGroup.FieldToMatchProperty(single_query_argument={"Name": "single query argument"})
URI_PATH = wafv2.CfnRuleGroup.FieldToMatchProperty(uri_path={"Name": "uri path"})

NO_TEXT_TRANSFORMATION = wafv2.CfnRuleGroup.TextTransformationProperty(priority=7, type="NONE")

class Ext01Stack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        
        #Create XSS rule
        xss_body = wafv2.CfnRuleGroup.StatementOneProperty(xss_match_statement= wafv2.CfnRuleGroup.XssMatchStatementProperty(field_to_match=BODY, text_transformations=[NO_TEXT_TRANSFORMATION]))
        xss_query_string = wafv2.CfnRuleGroup.StatementOneProperty(xss_match_statement= wafv2.CfnRuleGroup.XssMatchStatementProperty(field_to_match=QUERY_STRING, text_transformations=[NO_TEXT_TRANSFORMATION]))
        xss_uri = wafv2.CfnRuleGroup.StatementOneProperty(xss_match_statement= wafv2.CfnRuleGroup.XssMatchStatementProperty(field_to_match=URI_PATH, text_transformations=[NO_TEXT_TRANSFORMATION]))
        xss_header = wafv2.CfnRuleGroup.StatementOneProperty(xss_match_statement= wafv2.CfnRuleGroup.XssMatchStatementProperty(field_to_match=SINGLE_HEADER, text_transformations=[NO_TEXT_TRANSFORMATION]))

        xss_rule_group = wafv2.CfnRuleGroup(
            self, 
            id="XSS", 
            capacity=1, 
            scope="REGIONAL", 
            visibility_config = wafv2.CfnRuleGroup.VisibilityConfigProperty(
                cloud_watch_metrics_enabled=True, 
                metric_name="xss_attacks", 
                sampled_requests_enabled=False
            ),
            rules = [
                wafv2.CfnRuleGroup.RuleProperty(
                    name="xss_query_string", 
                    priority=1, 
                    statement= xss_query_string,
                    visibility_config= wafv2.CfnRuleGroup.VisibilityConfigProperty(
                        cloud_watch_metrics_enabled=False, 
                        metric_name="xss_attacks", 
                        sampled_requests_enabled=False
                    )
                ),
                wafv2.CfnRuleGroup.RuleProperty(
                    name="xss_body", 
                    priority=2, 
                    statement= xss_body,
                    visibility_config= wafv2.CfnRuleGroup.VisibilityConfigProperty(
                        cloud_watch_metrics_enabled=False, 
                        metric_name="xss_attacks", 
                        sampled_requests_enabled=False
                    )
                ),
                wafv2.CfnRuleGroup.RuleProperty(
                    name="xss_uri", 
                    priority=3, 
                    statement= xss_uri,
                    visibility_config= wafv2.CfnRuleGroup.VisibilityConfigProperty(
                        cloud_watch_metrics_enabled=False, 
                        metric_name="xss_attacks", 
                        sampled_requests_enabled=False
                    )
                ),
                wafv2.CfnRuleGroup.RuleProperty(
                    name="xss_header", 
                    priority=4, 
                    statement= xss_header,
                    visibility_config= wafv2.CfnRuleGroup.VisibilityConfigProperty(
                        cloud_watch_metrics_enabled=False, 
                        metric_name="xss_attacks", 
                        sampled_requests_enabled=False
                    )
                ),
            ]
        )
        """
        #Create the SQLI rule group
        sqli_body = wafv2.CfnRuleGroup.StatementOneProperty(sqli_match_statement= wafv2.CfnRuleGroup.SqliMatchStatementProperty(field_to_match=BODY, text_transformations=[]))
        sqli_query_string = wafv2.CfnRuleGroup.StatementOneProperty(sqli_match_statement= wafv2.CfnRuleGroup.SqliMatchStatementProperty(field_to_match=QUERY_STRING, text_transformations=[]))
        sqli_uri = wafv2.CfnRuleGroup.StatementOneProperty(sqli_match_statement= wafv2.CfnRuleGroup.SqliMatchStatementProperty(field_to_match=URI_PATH, text_transformations=[]))
        sqli_header = wafv2.CfnRuleGroup.StatementOneProperty(sqli_match_statement= wafv2.CfnRuleGroup.SqliMatchStatementProperty(field_to_match=SINGLE_HEADER, text_transformations=[]))

        sqli_rule_group = wafv2.CfnRuleGroup(
            self, 
            id="SQLI", 
            capacity=1, 
            scope="REGIONAL", 
            visibility_config = wafv2.CfnRuleGroup.VisibilityConfigProperty(
                cloud_watch_metrics_enabled=True, 
                metric_name="sqli attacks", 
                sampled_requests_enabled=False
            ),
            rules = [
                wafv2.CfnRuleGroup.RuleProperty(
                    name="sqli query string", 
                    priority=1, 
                    statement= sqli_query_string,
                    visibility_config= wafv2.CfnRuleGroup.VisibilityConfigProperty(
                        cloud_watch_metrics_enabled=False, 
                        metric_name="sqli attacks", 
                        sampled_requests_enabled=False
                    )
                ),
                wafv2.CfnRuleGroup.RuleProperty(
                    name="sqli body", 
                    priority=2, 
                    statement= sqli_body,
                    visibility_config= wafv2.CfnRuleGroup.VisibilityConfigProperty(
                        cloud_watch_metrics_enabled=False, 
                        metric_name="sqli attacks", 
                        sampled_requests_enabled=False
                    )
                ),
                wafv2.CfnRuleGroup.RuleProperty(
                    name="sqli uri", 
                    priority=3, 
                    statement= sqli_uri,
                    visibility_config= wafv2.CfnRuleGroup.VisibilityConfigProperty(
                        cloud_watch_metrics_enabled=False, 
                        metric_name="sqli attacks", 
                        sampled_requests_enabled=False
                    )
                ),
                wafv2.CfnRuleGroup.RuleProperty(
                    name="sqli header", 
                    priority=4, 
                    statement= sqli_header,
                    visibility_config= wafv2.CfnRuleGroup.VisibilityConfigProperty(
                        cloud_watch_metrics_enabled=False, 
                        metric_name="sqli attacks", 
                        sampled_requests_enabled=False
                    )
                ),
            ]
        )

        #Create the LFI and path traversal sets
        regex_pattern_set = wafv2.CfnRegexPatternSet(self, id="Ext01LptSet", regular_expression_list=[".*\.\./.*", ".*://.*"], scope="REGIONAL")
        lpt_query_string = wafv2.CfnRuleGroup.StatementOneProperty(regex_pattern_set_reference_statement=wafv2.CfnRuleGroup.RegexPatternSetReferenceStatementProperty(arn=regex_pattern_set.attr_arn, field_to_match=QUERY_STRING, text_transformations=[]))
        lpt_uri = wafv2.CfnRuleGroup.StatementOneProperty(regex_pattern_set_reference_statement=wafv2.CfnRuleGroup.RegexPatternSetReferenceStatementProperty(arn=regex_pattern_set.attr_arn, field_to_match=URI_PATH, text_transformations=[]))

        lpt_rule_group = wafv2.CfnRuleGroup(
            self, 
            id="LPT", 
            capacity=1, 
            scope="REGIONAL", 
            visibility_config = wafv2.CfnRuleGroup.VisibilityConfigProperty(
                cloud_watch_metrics_enabled=True, 
                metric_name="lpt attacks", 
                sampled_requests_enabled=False
            ),
            rules = [
                wafv2.CfnRuleGroup.RuleProperty(
                    name="lpt query string",
                    priority=1,
                    statement=lpt_query_string,
                    visibility_config= wafv2.CfnRuleGroup.VisibilityConfigProperty(
                        cloud_watch_metrics_enabled=False, 
                        metric_name="lpt attacks", 
                        sampled_requests_enabled=False
                    )
                ),
                wafv2.CfnRuleGroup.RuleProperty(
                    name="lpt uri", 
                    priority=2, 
                    statement= lpt_uri,
                    visibility_config= wafv2.CfnRuleGroup.VisibilityConfigProperty(
                        cloud_watch_metrics_enabled=False, 
                        metric_name="lpt attacks", 
                        sampled_requests_enabled=False
                        )
                    )
            ]
        )
        """

        # Create new WAF IPSet
        waf = wafv2.CfnIPSet(
            self,
            "Ext01ResponseIpSet",
            addresses=[],
            ip_address_version="IPV4",
            scope="REGIONAL",
            name="Ext01ResponseIpSet",
        )

        kinesis_log = s3.Bucket(self, id='waf_logs') 
        #kinesis_log.add_event_notification(s3.EventType.OBJECT_CREATED, )

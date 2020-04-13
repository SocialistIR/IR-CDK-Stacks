from aws_cdk import (
    core,
    aws_s3 as s3,
    aws_wafv2 as wafv2
)
import os
import logging

class Ext01Stack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        
        #Create XSS rule
        xss_vis_con = wafv2.VisibilityConfigProperty = {
            "cloudWatchMetricsEnabled": True, 
            "metricName": "xss attacks", 
            "sampledRequestsEnabled": False
        }
        xss_body_match = wafv2.FieldToMatchProperty = {
            "body": True        
        }

        xss_match_prop = wafv2.XssMatchStatementProperty = {
            "fieldToMatch": xss_body_match,
            "textTransformations": []
        }
        
        xss_statement_one = wafv2.StatementOneProperty = {
            "xssMatchStatement": xss_match_prop        
        }

        block_property = wafv2.RuleActionProperty = {
            "block": True
        }

        xss_rule1 = wafv2.RuleProperty = {
            "name": "xss", 
            "priority": 2, 
            "statement": xss_statement_one, 
            "action": block_property
        }

        xss_rules = []
        xss_rules.append(xss_rule1)

        xss_rule_group_props = wafv2.CfnRuleGroupProps = {
            "capacity": 0,
            "scope": self,
            "visibilityConfig": xss_vis_con,
            "rules": xss_rules
        }
        

        xss_rule_group = wafv2.CfnRuleGroup(
            self, 
            id="xss", 
            capacity=1, 
            scope="REGIONAL", 
            visibility_config = wafv2.CfnRuleGroup.VisbilityConfigProperty(cloudWatchMetricsEnabled=True, metricName="xss attacks", sampledRequestsEnabled=False),
            rules=xss_rules
        )

        kinesis_log = s3.Bucket(self, id='waf_logs') 

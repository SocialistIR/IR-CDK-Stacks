from aws_cdk import (
    core,
    aws_events as cw_event,
    aws_lambda as _lambda
)
import os
import logging
import datetime

logger = logging.getLogger(__name__)


class InLam01Stack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        SLACK_WEBHOOK_URL = self.node.try_get_context("webhook_url")

        if not SLACK_WEBHOOK_URL:
            logger.error(f"Required context variables for {id} were not provided!")
        else:
            # set up cloudwatch event for lambda invokes
            cw_hook = cw_event.Rule(
                description = "Monitor Lambda Invokes",
                event_pattern=None,
                rule_name = "lambdaMonitor",
                targets=None
            )

            # Create unban lambda
            lambda_dir_path = os.path.join(os.getcwd(), "ir_cdk_stacks", "in_aur_01")
            lockdown_lambda = _lambda.Function(
                self,
                f"InLam01LockdownFunction{int(datetime.datetime.now().timestamp())}",
                runtime=_lambda.Runtime.PYTHON_3_8,
                handler="response_lambda.lambda_handler",
                code=_lambda.Code.from_asset(lambda_dir_path),
                environment={
                    "webhook_url": SLACK_WEBHOOK_URL,
                    "lambdaDenyIAM" : "test"
                }
            )
            

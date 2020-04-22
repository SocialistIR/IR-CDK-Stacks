from aws_cdk import core
from aws_cdk import aws_sns as sns
from aws_cdk import aws_sns_subscriptions as subs
from aws_cdk import aws_iam as iam
import aws_cdk.aws_cloudtrail as cloudtrail
from aws_cdk import aws_events as events
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_s3 as s3

class CdkStackStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # The code that defines your stack goes here
        topic = sns.Topic(self, "CDKTestSNSTopic", topic_name = "CDKTestSNSTopic")
        # topic.grant_publish(iam.ServicePrincipal("*"))
        topic.add_subscription(subs.EmailSubscription('s.mathur@unsw.edu.au'))


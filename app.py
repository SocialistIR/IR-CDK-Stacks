#!/usr/bin/env python3

from aws_cdk import core

from ir_cdk_stacks.ir_cdk_stacks_stack import IrCdkStacksStack
from ir_cdk_stacks.in_aur_01_stack import InAur01Stack
from ir_cdk_stacks.In_S3_01_Prod_Stack import InS301StackProd
from ir_cdk_stacks.In_S3_01_Preprod_Stack import InS301PreprodStack
from ir_cdk_stacks.In_S3_01_Dev_Stack import InS301DevStack
from socialist_ir.config import Config

config = Config.get_config()

ACCOUNT = config.get("main", "account")
REGION = config.get("main", "region")

env_US = core.Environment(account=ACCOUNT, region=REGION)

app = core.App()
IrCdkStacksStack(app, "ir-cdk-stacks", env=env_US)
InAur01Stack(app, "in-aur-01-stack", env=env_US)
InS301StackProd(app, "in-s3-01-prod-stack", env=env_US)
InS301PreprodStack(app, "in-s3-01-preprod-stack", env=env_US)
InS301DevStack(app, "in-s3-01-dev-stack", env=env_US)

app.synth()

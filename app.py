#!/usr/bin/env python3

from aws_cdk import core

from ir_cdk_stacks.ir_cdk_stacks_stack import IrCdkStacksStack
from ir_cdk_stacks.in_aur_01_stack import InAur01Stack

env_US = core.Environment(account="544820149332", region="us-east-1")

app = core.App()
IrCdkStacksStack(app, "ir-cdk-stacks")
InAur01Stack(app, "in-aur-01-stack", env=env_US)

app.synth()

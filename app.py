#!/usr/bin/env python3

from aws_cdk import core

from ir_cdk_stacks.ir_cdk_stacks_stack import IrCdkStacksStack
from ir_cdk_stacks.in_aur_01_detection_stack import InAur01DetectionStack


app = core.App()
IrCdkStacksStack(app, "ir-cdk-stacks")
InAur01DetectionStack(app, "in-aur-01-detection-stack")

app.synth()

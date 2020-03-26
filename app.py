#!/usr/bin/env python3

from aws_cdk import core

from ir_cdk_stacks.ir_cdk_stacks_stack import IrCdkStacksStack


app = core.App()
IrCdkStacksStack(app, "ir-cdk-stacks")

app.synth()

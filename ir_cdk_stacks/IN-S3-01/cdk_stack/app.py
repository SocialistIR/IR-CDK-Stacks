#!/usr/bin/env python3

from aws_cdk import core

from cdk_stack.cdk_stack_stack import CdkStackStack


app = core.App()
CdkStackStack(app, "IN-S3-01-cdk-stack")

app.synth()

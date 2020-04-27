#!/usr/bin/env python3

from aws_cdk import core

from ir_cdk_stacks.ir_cdk_stacks_stack import IrCdkStacksStack
from ir_cdk_stacks.in_aur_01_stack import InAur01Stack
from ir_cdk_stacks.in_aur_02_stack import InAur02Stack
from ir_cdk_stacks.in_lam_01_stack import InLam01Stack
from ir_cdk_stacks.ext_01_stack import Ext01Stack
from ir_cdk_stacks.ext_06_stack import Ext06Stack
from socialist_ir.config import Config

config = Config.get_config()

ACCOUNT = config.get("main", "account")
REGION = config.get("main", "region")

env_US = core.Environment(account=ACCOUNT, region=REGION)

app = core.App()
IrCdkStacksStack(app, "ir-cdk-stacks", env=env_US)
InAur01Stack(app, "in-aur-01-stack", env=env_US)
InAur02Stack(app, "in-aur-02-stack", env=env_US)
InLam01Stack(app, "in-lam-01-stack", env=env_US)
Ext01Stack(app, "ext-01-stack", env=env_US)
Ext06Stack(app, "ext-06-stack", env=env_US)


app.synth()

from PyInquirer import prompt
from socialist_ir.cdk_menu import CdkMenu
from socialist_ir.config import Config
from aws_cdk import (
    core,
    aws_lambda as _lambda,
)
import boto3
import os
import json
import yaml
import zipfile
import time
import datetime


class AccessClt(CdkMenu):
    def __init__(
            self,
            name: str = "lambda_create",
            required_variables: list = [],
    ):
        super().__init__(name=name, required_variables=required_variables)

    # def execute(self) -> bool:

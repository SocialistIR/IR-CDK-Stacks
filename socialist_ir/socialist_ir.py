import os
import sys
from PyInquirer import prompt
from socialist_ir.utils.validators import (
    AwsAccountIdValidator,
    AwsRegionValidator,
)
from socialist_ir.in_aur_01_stack import InAur01Stack
from socialist_ir.config import Config


class SocialistIr:
    def __init__(self):
        self.config = Config.get_config()

    def init_config(self):
        if "main" not in self.config:
            self.config.add_section("main")

    def environment_setup(self):
        # Prompt required variables
        questions = [
            {
                "type": "input",
                "name": "account",
                "message": "Please enter your AWS Account ID",
                "validate": AwsAccountIdValidator,
            },
            {
                "type": "input",
                "name": "region",
                "message": "Please enter the region you want to deploy your IR stack to",
                "validate": AwsRegionValidator,
            },
        ]

        answers = prompt(questions)

        # Save variables to config
        if answers and answers["account"] and answers["region"]:
            self.config.set("main", "account", answers["account"])
            self.config.set("main", "region", answers["region"])
            Config.save_config(self.config)

    def list_ir_stacks(self):
        while True:
            questions = [
                {
                    "type": "list",
                    "name": "ir",
                    "message": "Which IR stack do you want to deploy?",
                    "choices": [
                        "IN-S3-01",
                        "IN-AUR-01",
                        "IN-AUR-02",
                        "IN-AUR-03",
                        "IN-API-01",
                        "IN-API-02",
                        "IN-LAM-01",
                        "IN-CLW-01",
                        "IN-CLT-01",
                        "IN-IAM-01",
                        "Back",
                    ],
                }
            ]

            answers = prompt(questions)

            # Process answers
            if answers and answers["ir"]:
                stack = None
                if answers["ir"] == "IN-AUR-01":
                    stack = InAur01Stack(
                        name="in-aur-01-stack",
                        required_variables=[
                            "cluster_name",
                            "notify_email",
                            "webhook_url",
                        ],
                    )
                if answers["ir"] == "Back":
                    return
                if stack:
                    stack.run()

    def run(self):
        # Initialize config file
        self.init_config()

        # Check main variables
        if "account" not in self.config["main"] or "region" not in self.config["main"]:
            print(
                "Required environment variables were not configured, running setup..."
            )
            self.environment_setup()

        # Prompt main
        while True:
            questions = [
                {
                    "type": "list",
                    "name": "main",
                    "message": "Welcome to SocialistIR!",
                    "choices": ["Run environment setup", "Deploy IR stacks", "Exit",],
                }
            ]

            answers = prompt(questions)

            # Process answers
            if answers and answers["main"]:
                if answers["main"] == "Run environment setup":
                    self.environment_setup()
                elif answers["main"] == "Deploy IR stacks":
                    self.list_ir_stacks()
                elif answers["main"] == "Exit":
                    sys.exit(0)

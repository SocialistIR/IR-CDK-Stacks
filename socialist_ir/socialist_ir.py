import sys
from PyInquirer import prompt
from socialist_ir.utils.validators import AwsAccountIdValidator
from socialist_ir.in_aur_01_stack import InAur01Stack
from socialist_ir.in_aur_02_stack import InAur02Stack
from socialist_ir.in_lam_01_stack import InLam01Stack
from socialist_ir.ext_01_stack import Ext01Stack
from socialist_ir.ext_06_stack import Ext06Stack
from socialist_ir.in_clt_01_stack import InClt01Stack
from socialist_ir.in_s3_01_stack_prod import InS301StackProd
from socialist_ir.in_s3_01_stack_preprod import InS301StackPreprod
from socialist_ir.in_s3_01_stack_dev import InS301StackDev


from socialist_ir.config import Config
from socialist_ir.cdk_menu import CdkMenu


class SocialistIr(CdkMenu):
    def __init__(
        self, name: str = "main", required_variables: list = ["account", "region"],
    ):
        super().__init__(name=name, required_variables=required_variables)

    def setup(self) -> None:
        # Prompt required variables
        questions = [
            {
                "type": "input",
                "name": "account",
                "message": "Please enter your AWS Account ID",
                "validate": AwsAccountIdValidator,
            },
            {
                "type": "list",
                "name": "region",
                "message": "Please enter the region you want to deploy your IR stack to",
                "choices": [
                    "us-east-2",
                    "us-east-1",
                    "us-west-1",
                    "us-west-2",
                    "ap-east-1",
                    "ap-south-1",
                    "ap-northeast-3",
                    "ap-northeast-2",
                    "ap-southeast-1",
                    "ap-southeast-2",
                    "ap-northeast-1",
                    "ca-central-1",
                    "eu-central-1",
                    "eu-west-1",
                    "eu-west-2",
                    "eu-west-3",
                    "eu-north-1",
                    "me-south-1",
                    "sa-east-1",
                ],
            },
        ]

        answers = prompt(questions)

        # Save variables to config
        if answers and answers["account"] and answers["region"]:
            self.config.set(self.name, "account", answers["account"])
            self.config.set(self.name, "region", answers["region"])
            Config.save_config(self.config)

    def list_internal_stacks(self) -> None:
        while True:
            questions = [
                {
                    "type": "list",
                    "name": "ir",
                    "message": "Which Internal IR stack do you want to deploy?",
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
                if answers["ir"] == "IN-S3-01":
                    ques = [
                        {
                            "type": "list",
                            "name": "envName",
                            "message": "Which environment does the currently configured AWS account belong to?",
                            "choices": [
                                "dev",
                                "pre-prod",
                                "prod"
                            ],
                        }
                    ]
                    ans = prompt(ques)

                    if ans["envName"] == "dev":
                        stack = InS301StackDev(
                            name = "in-s3-01-dev-stack",
                            required_variables=[]
                            )
                    elif ans["envName"] == "pre-prod":
                        stack = InS301StackPreprod(
                            name = "in-s3-01-preprod-stack",
                            required_variables=[]
                            )
                    elif ans["envName"] == "prod":
                        stack = InS301StackProd(
                            name = "in-s3-01-prod-stack",
                            required_variables=[]
                            )

                elif answers["ir"] == "IN-AUR-01":
                    stack = InAur01Stack(
                        name="in-aur-01-stack",
                        required_variables=[
                            "cluster_name",
                            "notify_email",
                            "webhook_url",
                        ],
                    )
                elif answers["ir"] == "IN-AUR-02":
                    stack = InAur02Stack(
                        name="in-aur-02-stack",
                        required_variables=[
                            "cluster_name",
                            "notify_email",
                            "webhook_url",
                            "white_list_group",
                        ],
                    )
                elif answers["ir"] == "IN-AUR-03":
                    pass
                elif answers["ir"] == "IN-API-01":
                    pass
                elif answers["ir"] == "IN-API-02":
                    pass
                elif answers["ir"] == "IN-LAM-01":
                    # Prompt required variables
                    questions = [
                        {
                            "type": "confirm",
                            "message": "Deploying IN-LAM-01 may deny permissions on lambdas and IAMs on all AWS users in your account. Continue?",
                            "name": "continue",
                            "default": False,
                        },
                    ]

                    answers = prompt(questions)

                    if questions and answers["continue"]:
                        stack = InLam01Stack(
                            name="in-lam-01-stack",
                            required_variables=[
                                "webhook_url",
                            ],
                        )
                elif answers["ir"] == "IN-CLW-01":
                    pass
                elif answers["ir"] == "IN-CLT-01":
                    stack = InClt01Stack(
                            name="in-clt-01-stack",
                            required_variables=[
                                "notify_email",
                                "webhook_url",
                                "white_list_group",
                            ],
                        )
                    
                elif answers["ir"] == "IN-IAM-01":
                    pass
                elif answers["ir"] == "Back":
                    return
                if stack:
                    stack.run()

    def list_external_stacks(self) -> None:
        while True:
            questions = [
                {
                    "type": "list",
                    "name": "ir",
                    "message": "Which External IR stack do you want to deploy?",
                    "choices": [
                        "EXT-01",
                        "EXT-02",
                        "EXT-03",
                        "EXT-04",
                        "EXT-05",
                        "EXT-06",
                        "Back",
                    ],
                }
            ]

            answers = prompt(questions)

            # Process answers
            if answers and answers["ir"]:
                stack = None
                if answers["ir"] == "EXT-01":
                    stack = Ext01Stack(
                        name="ext-01-stack",
                        required_variables=[
                            "api_arn",
                        ],
                    )
                elif answers["ir"] == "EXT-02":
                    pass
                elif answers["ir"] == "EXT-03":
                    pass
                elif answers["ir"] == "EXT-04":
                    pass
                elif answers["ir"] == "EXT-05":
                    pass
                elif answers["ir"] == "EXT-06":
                    stack = Ext06Stack(
                        name="ext-06-stack",
                        required_variables=[
                            "api_arn",
                            "rate",
                        ],
                    )
                elif answers["ir"] == "Back":
                    return
                if stack:
                    stack.run()

    def list_ir_stacks(self) -> None:
        while True:
            questions = [
                {
                    "type": "list",
                    "name": "ir_scope",
                    "message": "Choose your IR scope:",
                    "choices": ["Internal", "External", "Back",],
                }
            ]

            answers = prompt(questions)

            # Process answers
            if answers and answers["ir_scope"]:
                stack = None
                if answers["ir_scope"] == "Internal":
                    self.list_internal_stacks()
                elif answers["ir_scope"] == "External":
                    self.list_external_stacks()
                elif answers["ir_scope"] == "Back":
                    return
                if stack:
                    stack.run()

    def run(self) -> None:
        # Check required variables
        self.check_required_variables()

        # Prompt main
        while True:
            questions = [
                {
                    "type": "list",
                    "name": self.name,
                    "message": "Welcome to SocialistIR!",
                    "choices": [
                        "Run environment setup",
                        "List config variables",
                        "Deploy IR stacks",
                        "Exit",
                    ],
                }
            ]

            answers = prompt(questions)

            # Process answers
            if answers and answers[self.name]:
                if answers[self.name] == "Run environment setup":
                    self.setup()
                elif answers[self.name] == "List config variables":
                    self.list_required_variables()
                elif answers[self.name] == "Deploy IR stacks":
                    self.list_ir_stacks()
                elif answers[self.name] == "Exit":
                    sys.exit(0)

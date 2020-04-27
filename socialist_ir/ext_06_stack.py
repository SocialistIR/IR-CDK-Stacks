from PyInquirer import prompt
from socialist_ir.cdk_menu import StackMenu
from socialist_ir.utils.validators import (
    ApiArnValidator,
    RateValidator,
)
from socialist_ir.config import Config


class Ext06Stack(StackMenu):
    def __init__(
        self,
        name="ext-06-stack",
        required_variables=["api_arn"],
    ):
        super().__init__(name=name, required_variables=required_variables)

    def setup(self):
        # Prompt required variables
        questions = [
            {
                "type": "input",
                "name": "api_arn",
                "message": "Please enter the arn of your API gateway or Elastic Load Balancer",
                "validate": ApiArnValidator,
            },
            {
                "type": "input",
                "name": "rate",
                "message": "Please enter the desired maximum requests over 5 minutes per IP address",
                "validate": RateValidator,
            },
        ]

        answers = prompt(questions)

        # Save variables to config
        if answers and answers["api_arn"]:
            self.config.set(self.name, "api_arn", answers["api_arn"])
            self.config.set(self.name, "rate", answers["rate"])
            Config.save_config(self.config)
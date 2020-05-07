from PyInquirer import prompt
from socialist_ir.cdk_menu import StackMenu
from socialist_ir.utils.validators import (
    ApiArnValidator,
    RateValidator,
    YesOrNoValidator,
)
from socialist_ir.config import Config
from socialist_ir.pen_testing.dos_url import DosUrl


class Ext06Stack(StackMenu):
    def __init__(
        self,
        name="ext-06-stack",
        required_variables=["api_arn"],
    ):
        super().__init__(name=name, required_variables=required_variables)

    def test(self):
        questions = [
            {
                "type": "input",
                "name": "response",
                "message": "WARNING!!!! This test will send many requests to your website\nTo continue, type y\nTo exit type n\n",
                "validate": YesOrNoValidator,
            },

        ]

        answers = prompt(questions)
        print("Roughly 5 minutes after the attack is complete, check the Ext06Suslist if its the first attack or the Ext06Doslist if its the second attack. Your IP address should appear there")
        if answers["response"] == 'y':
            dos_attack = DosUrl(
                name="dos_url", required_variables=["invoke_url"]
            )
            dos_attack.run()

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

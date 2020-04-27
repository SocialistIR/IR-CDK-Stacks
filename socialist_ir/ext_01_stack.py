from PyInquirer import prompt
from socialist_ir.cdk_menu import StackMenu
from socialist_ir.utils.validators import (
    ApiArnValidator,
)
from socialist_ir.config import Config


class Ext01Stack(StackMenu):
    def __init__(
        self,
        name="ext-01-stack",
        required_variables=["api_arn"],
    ):
        super().__init__(name=name, required_variables=required_variables)

    def test(self) -> None:
        print("Automated testing not doable.\n Manual testing procedure:\n1. Enter <script>alert(123);</script> as input to any API endpoint.")
        print("2. Wait 5 minutes")
        print("3. Check Ext06ResponseIpSet to see if it contains your IP address. If it doesn't depoyment has failed")
        print("4. If it does, wait for an hour and see if it gone")
        print("5. If it has disappeared, deployment was succesful. Otherwise it failed")

    def setup(self):
        # Prompt required variables
        questions = [
            {
                "type": "input",
                "name": "api_arn",
                "message": "Please enter the arn of your API gateway or Elastic Load Balancer",
                "validate": ApiArnValidator,
            },
        ]

        answers = prompt(questions)

        # Save variables to config
        if answers and answers["api_arn"]:
            self.config.set(self.name, "api_arn", answers["api_arn"])
            Config.save_config(self.config)

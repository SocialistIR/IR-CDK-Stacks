from PyInquirer import prompt
from socialist_ir.cdk_menu import CdkMenu
from socialist_ir.config import Config
import requests
import logging

from socialist_ir.utils.validators import (
    RateValidator,
)


class DosUrl(CdkMenu):
    def __init__(
        self,
        name: str = "dos_url",
        required_variables: list = ["invoke_url"],
    ):
        super().__init__(name=name, required_variables=required_variables)

    def setup(self) -> None:
        # Prompt required variables
        questions = [
            {
                "type": "input",
                "name": "invoke_url",
                "message": "Please enter your Amazon API Gateway Stage invoke url",
            },
            {
                "type": "input",
                "name": "rate",
                "message": "Enter the amount of requests that you want to send.\nNote that this should be higher than the rate set while deploying EXT-06 however if the rate is too high, not enough requests will be sent in the 5 minute period.\nNote 50 additional requests are sent to allow for time for the rule to trigger\n",
                "validate": RateValidator,
            },
        ]

        answers = prompt(questions)

        # Save variables to config
        if answers and answers["invoke_url"] and answers["rate"]:
            self.config.set(self.name, "invoke_url", answers["invoke_url"])
            self.config.set(self.name, "rate", answers["rate"])
            Config.save_config(self.config)

    def execute(self) -> None:
        invoke_url = self.config.get(self.name, "invoke_url")
        rate = self.config.get(self.name, "rate")
        if invoke_url == "":
            print("Please complete setupo")
        else:
            PARAMS = {}
            print("Attack starting")
            for i in range(0, int(rate) + 50):
                print(str(i) + ". ", end='')
                r = requests.get(url=invoke_url, params=PARAMS)
                print(r)
            print("Attack finished")
            print(
                "If <Response [403]> was being returned, the rate based rule triggered. Check Ext06DosIpSet or Ext06SusIpSet in about 5 minute to see if your IP was added")

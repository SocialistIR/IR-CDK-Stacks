from PyInquirer import prompt
from socialist_ir.cdk_menu import StackMenu
from socialist_ir.utils.validators import (
    SlackWebhookValidator,
)
from socialist_ir.config import Config
from socialist_ir.pen_testing.lambda_create import LambdaCreate


class InLam01Stack(StackMenu):
    def __init__(
        self,
        name: str = "in-lam-01-stack",
        required_variables: list = ["webhook_url"],
    ):
        super().__init__(name=name, required_variables=required_variables)


    def test(self) -> None:
        # Prompt tests
        questions = [
            {
                "type": "list",
                "name": "test",
                "message": "Select test to run:",
                "choices": ["Create Lambda"],
            },
        ]

        answers = prompt(questions)

        # Save variables to config
        if answers and answers["test"]:
            if answers["test"] == "Create Lambda":
                l = LambdaCreate()
                l.run()


    def setup(self) -> None:
        # Prompt required variables
        questions = [
            {
                "type": "input",
                "name": "webhook_url",
                "message": "Please enter your Slack Webhook URL",
                "validate": SlackWebhookValidator,
            },
        ]

        answers = prompt(questions)

        # Save variables to config
        if (
            answers
            and answers["webhook_url"]
        ):
            self.config.set(self.name, "webhook_url", answers["webhook_url"])
            Config.save_config(self.config)

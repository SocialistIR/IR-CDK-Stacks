from PyInquirer import prompt
from socialist_ir.cdk_menu import StackMenu
from socialist_ir.utils.validators import (
    EmailValidator,
    SlackWebhookValidator,
    AwsAuroraClusterNameValidator,
)
from socialist_ir.config import Config
from socialist_ir.pen_testing.aurora_pwd_crack import AuroraPwdCrack


class InClt01Stack(StackMenu):
    def __init__(
        self,
        name: str = "in-clt-01-stack",
        required_variables: list = ["webhook_url"],
    ):
        super().__init__(name=name, required_variables=required_variables)

    def setup(self) -> None:
        # Prompt required variables
        questions = [
            {
                "type": "input",
                "name": "webhook_url",
                "message": "Please enter your Slack Webhook URL",
                "validate": SlackWebhookValidator,
            }
        ]

        answers = prompt(questions)

        # Save variables to config
        if (
            answers
            # and answers["notify_email"]
            and answers["webhook_url"]
        ):
            # self.config.set(self.name, "notify_email", answers["notify_email"])
            self.config.set(self.name, "webhook_url", answers["webhook_url"])
            Config.save_config(self.config)
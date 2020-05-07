from PyInquirer import prompt
from socialist_ir.cdk_menu import StackMenu
from socialist_ir.utils.validators import (
    EmailValidator,
    SlackWebhookValidator,
)
from socialist_ir.config import Config
from socialist_ir.pen_testing.access_clt import AccessClt


class InClt01Stack(StackMenu):
    def __init__(
            self,
            name: str = "in-clt-01-stack",
            required_variables: list = ["webhook_url", "notify_email", "white_list_group"],
    ):
        super().__init__(name=name, required_variables=required_variables)

    def setup(self) -> None:
        # Prompt required variables
        questions = [
            {
                "type": "input",
                "name": "webhook_url",
                "message": "Please enter your Slack Webhook URL: ",
                "validate": SlackWebhookValidator,
            },
            {
                "type": "input",
                "name": "notify_email",
                "message": "Please enter your SNS Topic Subscription Email Address: ",
                "validate": EmailValidator,
            },
            {
                "type": "input",
                "name": "white_list_group",
                "message": "Please enter name of whitelist CloudTrail Access IAM Group",
            },
        ]

        answers = prompt(questions)

        # Save variables to config
        if (
                answers
                and answers["notify_email"]
                and answers["webhook_url"]
                and answers["white_list_group"]
        ):
            self.config.set(self.name, "notify_email", answers["notify_email"])
            self.config.set(self.name, "webhook_url", answers["webhook_url"])
            self.config.set(self.name, "white_list_group", answers["white_list_group"])
            Config.save_config(self.config)

    def test(self) -> None:
        # Prompt tests
        questions = [
            {
                "type": "list",
                "name": "test",
                "message": "Select test to run:",
                "choices": ["Access Cloudtrail"],
            },
        ]

        answers = prompt(questions)

        # Save variables to config
        if answers and answers["test"]:
            if answers["test"] == "Access Cloudtrail":
                access_clt_checker = AccessClt(name="access_clt", required_variables=[])
                access_clt_checker.run()

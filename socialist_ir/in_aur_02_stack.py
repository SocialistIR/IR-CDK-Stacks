from PyInquirer import prompt
from socialist_ir.cdk_menu import StackMenu
from socialist_ir.utils.validators import (
    EmailValidator,
    SlackWebhookValidator,
    AwsAuroraClusterNameValidator,
)
from socialist_ir.config import Config
from socialist_ir.pen_testing.aurora_api_modify import AuroraApiModify


class InAur02Stack(StackMenu):
    def __init__(
        self,
        name: str = "in-aur-02-stack",
        required_variables: list = ["cluster_name", "notify_email", "webhook_url"],
    ):
        super().__init__(name=name, required_variables=required_variables)

    def test(self) -> None:
        # Prompt tests
        questions = [
            {
                "type": "list",
                "name": "test",
                "message": "Select test to run:",
                "choices": ["Modify cluster master password using RDS API"],
            },
        ]

        answers = prompt(questions)

        # Save variables to config
        if answers and answers["test"]:
            if answers["test"] == "Modify cluster master password using RDS API":
                aurora_modify = AuroraApiModify(
                    name="aurora-api-modify", required_variables=["cluster"]
                )
                aurora_modify.run()

    def setup(self) -> None:
        # Prompt required variables
        questions = [
            {
                "type": "input",
                "name": "cluster_name",
                "message": "Please enter the name of the Aurora Cluster",
                "validate": AwsAuroraClusterNameValidator,
            },
            {
                "type": "input",
                "name": "notify_email",
                "message": "Please enter your notification email",
                "validate": EmailValidator,
            },
            {
                "type": "input",
                "name": "webhook_url",
                "message": "Please enter your Slack Webhook URL",
                "validate": SlackWebhookValidator,
            },
            {
                "type": "input",
                "name": "white_list_group",
                "message": "Please enter the name of your white list IAM group",
            },
        ]

        answers = prompt(questions)

        # Save variables to config
        if (
            answers
            and answers["cluster_name"]
            and answers["notify_email"]
            and answers["webhook_url"]
        ):
            self.config.set(self.name, "cluster_name", answers["cluster_name"])
            self.config.set(self.name, "notify_email", answers["notify_email"])
            self.config.set(self.name, "webhook_url", answers["webhook_url"])
            Config.save_config(self.config)

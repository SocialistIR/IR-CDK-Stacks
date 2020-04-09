from PyInquirer import prompt
from socialist_ir.cdk_menu import CdkMenu
from socialist_ir.utils.validators import (
    EmailValidator,
    SlackWebhookValidator,
    AwsAuroraClusterNameValidator,
)
from socialist_ir.config import Config


class InAur01Stack(CdkMenu):
    def __init__(
        self,
        name="in-aur-01-stack",
        required_variables=["cluster_name", "notify_email", "webhook_url"],
    ):
        super().__init__(name=name, required_variables=required_variables)

    def setup(self):
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
        ]

        answers = prompt(questions)

        # Save variables to config
        if answers and answers["cluster_name"] and answers["notify_email"] and answers["webhook_url"]:
            self.config.set(self.name, "cluster_name", answers["cluster_name"])
            self.config.set(self.name, "notify_email", answers["notify_email"])
            self.config.set(self.name, "webhook_url", answers["webhook_url"])
            Config.save_config(self.config)

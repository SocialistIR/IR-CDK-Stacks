from PyInquirer import prompt
from socialist_ir.cdk_menu import StackMenu
from socialist_ir.utils.validators import (
    EmailValidator,
    SlackWebhookValidator,
)
from socialist_ir.config import Config


class InApi01Stack(StackMenu):
    def __init__(
            self,
            name: str = "in-api-01-stack",
            required_variables: list = ["input_bucket", "Stack_Name"],
    ):
        super().__init__(name=name, required_variables=required_variables)

    def setup(self) -> None:
        # Prompt required variables
        questions = [
            {
                "type": "input",
                "name": "input_bucket",
                "message": "Please enter S3 bucket name"
            },
            {
                "type": "input",
                "name": "Stack_Name",
                "message": "Enter the name of the stack created in clf"
            }
        ]

        answers = prompt(questions)

        # Save variables to config
        if (
                answers
                and answers["input_bucket"]
                and answers["Stack_Name"]
        ):
            self.config.set(self.name, "input_bucket", answers["input_bucket"])
            self.config.set(self.name, "Stack_Name", answers["Stack_Name"])
            Config.save_config(self.config)
          
    def test(self) -> None:
        print("Automated testing not added")
        print("2. Wait 2 minutes")
        print("3. Check IPset to see if it contains your IP address. If it doesn't depoyment has failed")
        print("4. If it does, wait for the inputted time and see if it gone")
        print("5. If it has disappeared, deployment was succesful. Otherwise it failed")

import boto3
from PyInquirer import prompt
from socialist_ir.cdk_menu import CdkMenu
from socialist_ir.config import Config

rds = boto3.client("rds")


class AuroraApiModify(CdkMenu):
    def __init__(
        self, name: str = "aurora-api-modify", required_variables: list = ["cluster"],
    ):
        super().__init__(name=name, required_variables=required_variables)

    def execute(self) -> bool:
        try:
            rds.modify_db_cluster(
                DBClusterIdentifier=self.config.get(self.name, "cluster"),
                MasterUserPassword="password",
                ApplyImmediately=True,
            )
            print("Success: Cluster master password modified!")
            return True
        except Exception as e:
            print(f"Error: Could not modify cluster.\nReason: {e}")
        return False

    def setup(self) -> None:
        # Prompt required variables
        questions = [
            {
                "type": "input",
                "name": "cluster",
                "message": "Please enter the ID of the Aurora cluster",
            },
        ]

        answers = prompt(questions)

        # Save variables to config
        if answers and answers["cluster"]:
            self.config.set(self.name, "cluster", answers["cluster"])
            Config.save_config(self.config)

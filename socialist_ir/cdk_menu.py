import subprocess
from PyInquirer import prompt
from socialist_ir.config import Config


class CdkMenu:
    def __init__(self, name: str, required_variables: list = []):
        if not name:
            raise ValueError("'name' argument is required")
        self.name = name
        self.required_variables = required_variables
        self.config = Config.get_config()
        if name not in self.config:
            self.config.add_section(name)

    def setup(self) -> None:
        pass

    def execute(self) -> None:
        pass

    def list_required_variables(self) -> None:
        for var in self.required_variables:
            print(f"{var}: {self.config.get(self.name, var)}")

    def check_required_variables(self) -> None:
        for var in self.required_variables:
            if var not in self.config[self.name]:
                print(
                    "Required variables were not correctly configured, running setup..."
                )
                self.setup()

    def run(self) -> None:
        self.check_required_variables()
        while True:
            questions = [
                {
                    "type": "list",
                    "name": self.name,
                    "message": "Choose your action:",
                    "choices": [
                        "Run setup",
                        "List config variables",
                        "Execute",
                        "Back",
                    ],
                }
            ]
            answers = prompt(questions)
            if answers[self.name] == "Run setup":
                self.setup()
            elif answers[self.name] == "List config variables":
                self.list_required_variables()
            elif answers[self.name] == "Execute":
                self.execute()
            elif answers[self.name] == "Back":
                return


class StackMenu(CdkMenu):
    def __init__(self, name: str, required_variables: list = []):
        super().__init__(name, required_variables)

    def aws_cdk_cli(self, cmd: str) -> None:
        command = [
            "cdk",
            cmd,
            self.name,
        ]
        for var in self.required_variables:
            command.append("-c")
            command.append(f"{var}={self.config.get(self.name, var)}")
        subprocess.run(command)

    def deploy(self) -> None:
        self.aws_cdk_cli("deploy")

    def synth(self) -> None:
        self.aws_cdk_cli("synth")

    def destroy(self) -> None:
        self.aws_cdk_cli("destroy")

    def test(self) -> None:
        pass

    def run(self) -> None:
        self.check_required_variables()
        while True:
            questions = [
                {
                    "type": "list",
                    "name": self.name,
                    "message": "Choose your action:",
                    "choices": [
                        "Run setup",
                        "List config variables",
                        "Run tests",
                        "Deploy stack",
                        "Synthesize stack",
                        "Destroy stack",
                        "Back",
                    ],
                }
            ]
            answers = prompt(questions)
            if answers[self.name] == "Run setup":
                self.setup()
            elif answers[self.name] == "List config variables":
                self.list_required_variables()
            elif answers[self.name] == "Run tests":
                self.test()
            elif answers[self.name] == "Deploy stack":
                self.deploy()
            elif answers[self.name] == "Synthesize stack":
                self.synth()
            elif answers[self.name] == "Destroy stack":
                self.destroy()
            elif answers[self.name] == "Back":
                return

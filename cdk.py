from __future__ import print_function, unicode_literals
from PyInquirer import prompt
from pprint import pprint
import click
import subprocess

from utils.helpers import is_valid_email, is_valid_webhook_url

def in_aur_01_stack():
    # Prompt required variables
    questions = [
        {
            "type": "input",
            "name": "notify_email",
            "message": "Please enter your notification email",
        },
        {
            "type": "input",
            "name": "webhook_url",
            "message": "Please enter your Slack Webhook URL",
        },
    ]
    answers = prompt(questions)

    if answers and answers["notify_email"] and answers["webhook_url"]:
        notify_email = answers["notify_email"]
        webhook_url = answers["webhook_url"]
        if not is_valid_email(notify_email):
            raise ValueError("You must enter a valid email.")
        if not is_valid_webhook_url(webhook_url):
            raise ValueError("You must enter a valid Slack Webhook URL.")
        subprocess.run(
            [
                "cdk",
                "synth",
                "in-aur-01-stack",
                "-c",
                f"notify_email={notify_email}",
                "-c",
                f"webhook_url={webhook_url}",
            ]
        )


def process_ir(ir_answers):
    if ir_answers["ir"] == "IN-AUR-01":
        in_aur_01_stack()


questions = [
    {
        "type": "list",
        "name": "ir",
        "message": "Which IR stack do you want to deploy?",
        "choices": [
            "IN-S3-01",
            "IN-AUR-01",
            "IN-AUR-02",
            "IN-AUR-03",
            "IN-API-01",
            "IN-API-02",
            "IN-LAM-01",
            "IN-CLW-01",
            "IN-CLT-01",
            "IN-IAM-01",
        ],
    }
]

answers = prompt(questions)
process_ir(answers)

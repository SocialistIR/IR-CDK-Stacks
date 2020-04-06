import re


def is_valid_email(email):
    # Regular expression for validating an Email format
    email_regex = "^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$"
    return re.search(email_regex, email)


def is_valid_webhook_url(webhook_url):
    webhook_regex = (
        "https:\/\/hooks\.slack\.com\/services\/T[0-9A-Z]+\/B[0-9A-Z]+\/[0-9A-Za-z]+"
    )
    return re.search(webhook_regex, webhook_url)

import pytest
from socialist_ir.utils.validators import EmailValidator
from PyInquirer import ValidationError
from prompt_toolkit.document import Document


def test_email_validator() -> None:
    char_only = Document(text="wrongFormat")
    digits = Document(text="234234")
    web = Document(text="abc.com")
    no_dot_com = Document(text="abc@asd")
    good = Document(text="test@email.com")

    with pytest.raises(ValidationError):
        validator = EmailValidator()
        validator.validate(char_only)

    with pytest.raises(ValidationError):
        validator = EmailValidator()
        validator.validate(digits)

    with pytest.raises(ValidationError):
        validator = EmailValidator()
        validator.validate(web)

    with pytest.raises(ValidationError):
        validator = EmailValidator()
        validator.validate(no_dot_com)

    validator.validate(good)

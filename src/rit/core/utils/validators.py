import re


class RitValidationException(Exception):
    pass

email_user_regex = re.compile(
    r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*\Z"  # dot-atom
    r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-\011\013\014\016-\177])*"\Z)',  # quoted-string
    re.IGNORECASE
)
email_domain_regex = re.compile(
    # max length for domain name labels is 63 characters per RFC
    # 1034
    r'((?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+)(?:[A-Z0-9-]{2,63}(?<!-))\Z',
    re.IGNORECASE
)


def validate_email(email, message='Enter a valid email address. An example example@example.com'):

    if not email or '@' not in email:
        raise RitValidationException(message)

    user_part, domain_part = email.rsplit('@', 1)

    if not email_user_regex.match(user_part):
        raise RitValidationException(message)

    if not email_domain_regex.match(domain_part):
        raise RitValidationException(message)


def validate_password(password):
    if not password:
        raise RitValidationException('Sorry, password is empty')

    if len(password) < 8:
        raise RitValidationException('Password wrong: 8 characters or more! Be tricky.')

    if not re.search(r'[a-z]{1,}', password):
        raise RitValidationException('Password wrong: Add at least one small letter (i.e. a)')

    if not re.search(r'[A-Z]{1,}', password):
        raise RitValidationException('Password wrong: Add at least one letter (i.e. A)')

    if not re.search(r'\d{1,}', password):
        raise RitValidationException('Password wrong: Add at least one number (i.e. 12)')

    if not re.search(r'[\^\&\!\@\#\$\%\&\*\(\)\<\>\?]{1,}', password):
        raise RitValidationException('Password wrong: Add at least one special character (i.e. ^&!@#$%&*()<>?)')


def get_first_error_from_wheezy_validator_result(errors):
    return errors.popitem()[1].pop()

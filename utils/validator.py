import re

from utils.exceptions import WeakPasswordError, InvalidNameException


class Messages:
    """
    Defines standard message strings for the application.
    """
    error_400 = "Invalid request. {} is invalid"
    generic_error = "An unknown error has occurred. Please try again!"


class Status:
    """
    Defines standard status codes for API responses.
    """
    INVALID_REQUEST = 400
    SUCCESS = 200
    CREATED_SUCCESS = 201


def validate_email(email: str) -> bool:
    """
    Validates if a given string is a correctly formatted email address.

    Args:
        email: The string to validate.

    Returns:
        True if the email is valid, False otherwise.
    """
    at, dot = "@", "."
    is_valid = False
    if at not in email or dot not in email:
        return is_valid
    email_segments = email.strip().lower().split(at)
    if len(email_segments) == 2:
        if email_segments[0][0].isalpha():
            domain_seg = email_segments[1].split(dot)
            is_valid = (1 < len(domain_seg) < 4) and domain_seg[0].isalpha() and domain_seg[1].isalpha()
    return is_valid


def validate_username(username: str) -> bool:
    """
    Validates if a given string is a valid username.

    A valid username starts with an alphabet and contains only alphanumeric characters.
    It must also have a length of at least 1.

    Args:
        username: The string to validate.

    Returns:
        True if the username is valid, False otherwise.
    """
    if len(username) < 1:
        return False
    return username[0].isalpha() and username.isalnum()


def check_name(name: str) -> str:
    """
    Checks if a given string is a valid name.

    A valid name has a length between 2 and 49 (inclusive) and contains only alphabetic characters.
    If the name is invalid, it raises an InvalidNameException.

    Args:
        name: The string to check.

    Returns:
        The validated name if it is valid.

    Raises:
        InvalidNameException: If the name does not meet the validation criteria.
    """
    if 1 < len(name) < 50 and name.isalpha():
        return name
    raise InvalidNameException


def check_password(password: str) -> str:
    """
    Checks if a given string is a strong password.

    A strong password must meet the following criteria:
    - Be at least 6 characters long.
    - Contain at least one digit.
    - Contain at least one non-alphanumeric character (symbol).
    - Not contain any whitespace.

    If the password is weak, it raises a WeakPasswordError.

    Args:
        password: The string to check.

    Returns:
        The validated password if it is strong.

    Raises:
        WeakPasswordError: If the password does not meet the strength criteria.
    """
    if len(password) >= 6 and re.search(r'\d+', password) \
            and re.search(r'\W+', password) \
            and not re.search(r'\s+', password):
        return password
    else:
        raise WeakPasswordError


def check_none(v1, v2):
    """
    Checks if the first value is None.

    If the first value is not None, it is returned.
    Otherwise, the second value is returned.

    Args:
        v1: The first value to check.
        v2: The second value to return if the first is None.

    Returns:
        v1 if it is not None, otherwise v2.
    """
    return v1 if v1 else v2
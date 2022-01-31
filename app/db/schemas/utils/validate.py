"""Validate for schema"""
import re


def password_validate(v):
    """
    Password validate
    - contains at least one lower character
    - contains at least one upper character
    - contains at least one digit character
    - contains at least one special character
    - contains at least 8 characters
    Raises:
        ValueError
    Returns:
        v
    """
    if not re.findall(r'[a-z]', v):
        raise ValueError('Contains at least one lower character')
    elif not re.findall(r'[A-Z]', v):
        raise ValueError('Contains at least one upper character')
    elif not re.findall(r'[0-9]', v):
        raise ValueError('Contains at least one digit character')
    elif not re.findall(r'[^\w\s]', v):
        raise ValueError('Contains at least one special character')
    elif not re.findall(r'.{8,}', v):
        raise ValueError('Contains at least 8 characters')

    return v

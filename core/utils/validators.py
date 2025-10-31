"""
Common validation functions for PulseWatch.

Provides reusable validators for models and forms.
"""

import re
from typing import Any
from urllib.parse import urlparse

from django.core.exceptions import ValidationError
from django.core.validators import URLValidator


def validate_url(value: str) -> None:
    """
    Validate that a string is a valid URL.

    Args:
        value: The URL string to validate

    Raises:
        ValidationError: If the URL is invalid
    """
    validator = URLValidator()
    validator(value)


def validate_http_url(value: str) -> None:
    """
    Validate that a string is a valid HTTP/HTTPS URL.

    Args:
        value: The URL string to validate

    Raises:
        ValidationError: If the URL is not HTTP/HTTPS
    """
    validate_url(value)
    parsed = urlparse(value)
    if parsed.scheme not in ["http", "https"]:
        raise ValidationError(f"URL must use HTTP or HTTPS protocol, got: {parsed.scheme}")


def validate_port(value: int) -> None:
    """
    Validate that a port number is in valid range (1-65535).

    Args:
        value: The port number to validate

    Raises:
        ValidationError: If the port is out of range
    """
    if not 1 <= value <= 65535:
        raise ValidationError(f"Port must be between 1 and 65535, got: {value}")


def validate_cron_expression(value: str) -> None:
    """
    Validate a basic cron expression (5 or 6 fields).

    Args:
        value: The cron expression to validate

    Raises:
        ValidationError: If the cron expression is invalid
    """
    parts = value.split()
    if len(parts) not in [5, 6]:
        raise ValidationError("Cron expression must have 5 or 6 fields")

    # Basic validation of each field (not comprehensive)
    cron_pattern = r"^(\*|[0-9]+([-/,][0-9]+)*|\*/[0-9]+)$"
    for part in parts:
        if not re.match(cron_pattern, part):
            raise ValidationError(f"Invalid cron field: {part}")


def validate_timeout(value: int) -> None:
    """
    Validate that a timeout value is positive.

    Args:
        value: The timeout in seconds

    Raises:
        ValidationError: If the timeout is not positive
    """
    if value <= 0:
        raise ValidationError(f"Timeout must be positive, got: {value}")


def validate_json_structure(value: Any, required_keys: list[str]) -> None:
    """
    Validate that a dictionary contains required keys.

    Args:
        value: The dictionary to validate
        required_keys: List of required key names

    Raises:
        ValidationError: If required keys are missing
    """
    if not isinstance(value, dict):
        raise ValidationError("Value must be a dictionary")

    missing_keys = set(required_keys) - set(value.keys())
    if missing_keys:
        raise ValidationError(f'Missing required keys: {", ".join(missing_keys)}')

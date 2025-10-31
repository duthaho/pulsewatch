"""
Custom exception classes for PulseWatch.

Provides domain-specific exceptions with DRF integration.
"""
from rest_framework import status
from rest_framework.exceptions import APIException


class PulseWatchException(Exception):
    """Base exception for all PulseWatch custom exceptions."""
    pass


class ResourceNotFoundException(PulseWatchException, APIException):
    """Raised when a requested resource is not found."""
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'The requested resource was not found.'
    default_code = 'not_found'


class ValidationException(PulseWatchException, APIException):
    """Raised when validation fails."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Validation error.'
    default_code = 'validation_error'


class PermissionDeniedException(PulseWatchException, APIException):
    """Raised when user lacks permission for an action."""
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'You do not have permission to perform this action.'
    default_code = 'permission_denied'


class ConflictException(PulseWatchException, APIException):
    """Raised when a conflict occurs (e.g., duplicate resource)."""
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'A conflict occurred with the current state.'
    default_code = 'conflict'


class ServiceUnavailableException(PulseWatchException, APIException):
    """Raised when a service is temporarily unavailable."""
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = 'Service temporarily unavailable.'
    default_code = 'service_unavailable'


class RateLimitExceededException(PulseWatchException, APIException):
    """Raised when rate limit is exceeded."""
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    default_detail = 'Rate limit exceeded.'
    default_code = 'rate_limit_exceeded'


class ExternalServiceException(PulseWatchException, APIException):
    """Raised when an external service call fails."""
    status_code = status.HTTP_502_BAD_GATEWAY
    default_detail = 'External service error.'
    default_code = 'external_service_error'

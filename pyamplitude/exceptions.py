"""Exception hierarchy for pyamplitude."""

from typing import Any, Mapping, Optional


class PyAmplitudeError(Exception):
    """Base exception for all pyamplitude errors."""


class ConfigurationError(PyAmplitudeError):
    """Raised when client configuration is incomplete or invalid."""


class ValidationError(PyAmplitudeError, ValueError):
    """Raised when a request model or parameter is invalid."""


class AmplitudeHTTPError(PyAmplitudeError):
    """Raised when Amplitude returns a non-success HTTP response."""

    def __init__(
        self,
        status_code: int,
        message: str,
        *,
        payload: Optional[Any] = None,
        response_text: str = "",
        headers: Optional[Mapping[str, str]] = None,
    ) -> None:
        self.status_code = status_code
        self.payload = payload
        self.response_text = response_text
        self.headers = dict(headers or {})
        super().__init__(message)


class AmplitudeBadRequest(AmplitudeHTTPError):
    """Raised for HTTP 400 responses."""


class AmplitudeAuthError(AmplitudeHTTPError):
    """Raised for HTTP 401 or 403 responses."""


class AmplitudeRateLimitError(AmplitudeHTTPError):
    """Raised for HTTP 429 responses."""


class AmplitudeServerError(AmplitudeHTTPError):
    """Raised for HTTP 5xx responses."""

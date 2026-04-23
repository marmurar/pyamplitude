"""Credential models."""

from dataclasses import dataclass
from typing import Optional, Tuple

from .exceptions import ConfigurationError


@dataclass(frozen=True)
class AmplitudeCredentials:
    """Credentials for Amplitude APIs.

    Dashboard, Export and Cohorts use ``api_key`` plus ``secret_key`` through
    Basic Auth. Ingestion APIs only need ``api_key`` in the request body.
    """

    api_key: str
    secret_key: Optional[str] = None
    project_name: Optional[str] = None
    project_id: Optional[int] = None

    def __post_init__(self) -> None:
        if not self.api_key:
            raise ConfigurationError("api_key is required.")

    @property
    def basic_auth(self) -> Tuple[str, str]:
        """Return a requests-compatible Basic Auth tuple."""

        if not self.secret_key:
            raise ConfigurationError("secret_key is required for this Amplitude API.")
        return (self.api_key, self.secret_key)

    def __repr__(self) -> str:
        name = self.project_name or "<unnamed>"
        return f"project_name: {name} | api_key: {self.api_key} | secret_key: {'***' if self.secret_key else ''}"


class ProjectsHandler(AmplitudeCredentials):
    """Backward-compatible alias for the original credential class."""

    def __init__(self, project_name: str, api_key: str, secret_key: str) -> None:
        super().__init__(api_key=api_key, secret_key=secret_key, project_name=project_name)

"""HTTP transport primitives.

The public clients accept any object exposing ``request(method, url, **kwargs)``.
Tests use that seam to avoid network access.
"""

from typing import Any, Optional

import requests


class RequestsTransport:
    """Small wrapper around ``requests.Session``."""

    def __init__(self, session: Optional[requests.Session] = None, timeout: float = 30.0) -> None:
        self.session = session or requests.Session()
        self.timeout = timeout

    def request(self, method: str, url: str, **kwargs: Any) -> requests.Response:
        """Send an HTTP request."""

        kwargs.setdefault("timeout", self.timeout)
        return self.session.request(method, url, **kwargs)

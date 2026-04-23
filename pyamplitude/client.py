"""Shared HTTP client helpers."""

from typing import Any, Dict, Iterable, Mapping, Optional, Sequence, Tuple

from .credentials import AmplitudeCredentials
from .exceptions import (
    AmplitudeAuthError,
    AmplitudeBadRequest,
    AmplitudeHTTPError,
    AmplitudeRateLimitError,
    AmplitudeServerError,
    ValidationError,
)
from .regions import RegionEndpoints, get_region
from .transport import RequestsTransport


SuccessCodes = Sequence[int]


class BaseClient:
    """Base class for Amplitude API clients."""

    def __init__(
        self,
        credentials: AmplitudeCredentials,
        *,
        region: str = "US",
        transport: Optional[Any] = None,
        timeout: float = 30.0,
    ) -> None:
        self.credentials = credentials
        self.region_name = region.upper()
        self.endpoints: RegionEndpoints = get_region(region)
        self.transport = transport or RequestsTransport(timeout=timeout)

    @staticmethod
    def _extend_params(params: Optional[Iterable[Tuple[str, Any]]] = None) -> list:
        return list(params or [])

    @staticmethod
    def _json_or_none(response: Any) -> Optional[Any]:
        text = getattr(response, "text", "")
        content = getattr(response, "content", b"")
        if not text and not content:
            return None
        try:
            return response.json()
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _response_text(response: Any) -> str:
        text = getattr(response, "text", None)
        if text is not None:
            return text
        content = getattr(response, "content", b"")
        if isinstance(content, bytes):
            return content.decode("utf-8", errors="replace")
        return str(content)

    def _raise_for_response(self, response: Any, success: SuccessCodes) -> None:
        status_code = int(getattr(response, "status_code"))
        if status_code in success:
            return
        payload = self._json_or_none(response)
        text = self._response_text(response)
        message = f"Amplitude API request failed with HTTP {status_code}."
        if isinstance(payload, Mapping):
            detail = payload.get("error") or payload.get("message")
            if detail:
                message = f"{message} {detail}"
        elif text:
            message = f"{message} {text}"
        headers = getattr(response, "headers", {})
        exc_kwargs: Dict[str, Any] = {
            "payload": payload,
            "response_text": text,
            "headers": headers,
        }
        if status_code == 400:
            raise AmplitudeBadRequest(status_code, message, **exc_kwargs)
        if status_code in {401, 403}:
            raise AmplitudeAuthError(status_code, message, **exc_kwargs)
        if status_code == 429:
            raise AmplitudeRateLimitError(status_code, message, **exc_kwargs)
        if status_code >= 500:
            raise AmplitudeServerError(status_code, message, **exc_kwargs)
        raise AmplitudeHTTPError(status_code, message, **exc_kwargs)

    def request_json(
        self,
        method: str,
        url: str,
        *,
        params: Optional[Iterable[Tuple[str, Any]]] = None,
        json: Optional[Mapping[str, Any]] = None,
        auth: bool = False,
        headers: Optional[Mapping[str, str]] = None,
        success: SuccessCodes = tuple(range(200, 300)),
    ) -> Any:
        """Send a request and parse a JSON response."""

        kwargs: Dict[str, Any] = {"params": self._extend_params(params)}
        if json is not None:
            kwargs["json"] = dict(json)
        if auth:
            kwargs["auth"] = self.credentials.basic_auth
        if headers:
            kwargs["headers"] = dict(headers)
        response = self.transport.request(method.upper(), url, **kwargs)
        self._raise_for_response(response, success)
        payload = self._json_or_none(response)
        if payload is None:
            raise ValidationError("Amplitude response did not contain valid JSON.")
        return payload

    def request_bytes(
        self,
        method: str,
        url: str,
        *,
        params: Optional[Iterable[Tuple[str, Any]]] = None,
        auth: bool = False,
        headers: Optional[Mapping[str, str]] = None,
        success: SuccessCodes = tuple(range(200, 300)),
    ) -> bytes:
        """Send a request and return raw response bytes."""

        kwargs: Dict[str, Any] = {"params": self._extend_params(params)}
        if auth:
            kwargs["auth"] = self.credentials.basic_auth
        if headers:
            kwargs["headers"] = dict(headers)
        response = self.transport.request(method.upper(), url, **kwargs)
        self._raise_for_response(response, success)
        content = getattr(response, "content", None)
        if isinstance(content, bytes):
            return content
        return self._response_text(response).encode("utf-8")

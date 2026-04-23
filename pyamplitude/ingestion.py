"""Clients for Amplitude ingestion APIs."""

from typing import Any, Mapping, Optional, Sequence, Union

from .client import BaseClient
from .credentials import AmplitudeCredentials
from .models import AmplitudeEvent, UploadOptions


def _event_payloads(events: Sequence[Union[AmplitudeEvent, Mapping[str, Any]]]) -> list:
    return [event.to_payload() if isinstance(event, AmplitudeEvent) else dict(event) for event in events]


def _options_payload(options: Optional[Union[UploadOptions, Mapping[str, Any]]]) -> Optional[dict]:
    if options is None:
        return None
    if isinstance(options, UploadOptions):
        payload = options.to_payload()
    else:
        payload = dict(options)
    return payload or None


class HTTPV2Client(BaseClient):
    """Client for the HTTP V2 API."""

    def upload(
        self,
        events: Sequence[Union[AmplitudeEvent, Mapping[str, Any]]],
        *,
        options: Optional[Union[UploadOptions, Mapping[str, Any]]] = None,
    ) -> Any:
        payload = {"api_key": self.credentials.api_key, "events": _event_payloads(events)}
        options_payload = _options_payload(options)
        if options_payload is not None:
            payload["options"] = options_payload
        return self.request_json(
            "POST",
            self.endpoints.http_v2,
            json=payload,
            headers={"Content-Type": "application/json"},
        )

    def identify(
        self,
        *,
        user_id: Optional[str] = None,
        device_id: Optional[str] = None,
        user_properties: Mapping[str, Any],
        insert_id: Optional[str] = None,
    ) -> Any:
        event = AmplitudeEvent(
            event_type="$identify",
            user_id=user_id,
            device_id=device_id,
            user_properties=user_properties,
            insert_id=insert_id,
        )
        return self.upload([event])


class BatchClient(BaseClient):
    """Client for the Batch Event Upload API."""

    def upload(
        self,
        events: Sequence[Union[AmplitudeEvent, Mapping[str, Any]]],
        *,
        options: Optional[Union[UploadOptions, Mapping[str, Any]]] = None,
    ) -> Any:
        payload = {"api_key": self.credentials.api_key, "events": _event_payloads(events)}
        options_payload = _options_payload(options)
        if options_payload is not None:
            payload["options"] = options_payload
        return self.request_json(
            "POST",
            self.endpoints.batch,
            json=payload,
            headers={"Content-Type": "application/json"},
        )


def make_ingestion_credentials(api_key: str) -> AmplitudeCredentials:
    """Create credentials for APIs that only require an API key."""

    return AmplitudeCredentials(api_key=api_key)

import pytest

from pyamplitude.client import BaseClient
from pyamplitude.exceptions import (
    AmplitudeAuthError,
    AmplitudeBadRequest,
    AmplitudeHTTPError,
    AmplitudeRateLimitError,
    AmplitudeServerError,
    ValidationError,
)
from pyamplitude.transport import RequestsTransport

from conftest import FakeResponse, RecordingTransport


def test_request_json_success_uses_basic_auth(credentials):
    transport = RecordingTransport(FakeResponse(json_data={"ok": True}))
    client = BaseClient(credentials, transport=transport)

    assert client.request_json("get", "https://example.test", auth=True) == {"ok": True}
    assert transport.requests[0]["method"] == "GET"
    assert transport.requests[0]["auth"] == ("api-key", "secret")


def test_request_json_requires_json_body(credentials):
    client = BaseClient(credentials, transport=RecordingTransport(FakeResponse(text="plain")))

    with pytest.raises(ValidationError):
        client.request_json("GET", "https://example.test")


def test_request_json_empty_body_is_invalid(credentials):
    client = BaseClient(credentials, transport=RecordingTransport(FakeResponse()))

    with pytest.raises(ValidationError):
        client.request_json("GET", "https://example.test")


@pytest.mark.parametrize(
    ("status", "error_type"),
    [
        (400, AmplitudeBadRequest),
        (401, AmplitudeAuthError),
        (403, AmplitudeAuthError),
        (429, AmplitudeRateLimitError),
        (500, AmplitudeServerError),
        (418, AmplitudeHTTPError),
    ],
)
def test_http_error_mapping(credentials, status, error_type):
    response = FakeResponse(status_code=status, json_data={"error": "bad things"}, headers={"x": "y"})
    client = BaseClient(credentials, transport=RecordingTransport(response))

    with pytest.raises(error_type) as exc:
        client.request_json("GET", "https://example.test")

    assert exc.value.status_code == status
    assert exc.value.payload == {"error": "bad things"}
    assert exc.value.headers == {"x": "y"}


def test_http_error_uses_plain_text_when_json_is_missing(credentials):
    client = BaseClient(credentials, transport=RecordingTransport(FakeResponse(status_code=409, text="conflict")))

    with pytest.raises(AmplitudeHTTPError) as exc:
        client.request_json("GET", "https://example.test")

    assert "conflict" in str(exc.value)


def test_http_error_can_render_non_byte_content(credentials):
    response = FakeResponse(status_code=409)
    response.text = None
    response.content = {"error": "conflict"}
    client = BaseClient(credentials, transport=RecordingTransport(response))

    with pytest.raises(AmplitudeHTTPError) as exc:
        client.request_json("GET", "https://example.test")

    assert "{'error': 'conflict'}" in str(exc.value)


def test_request_bytes_handles_text_response(credentials):
    client = BaseClient(credentials, transport=RecordingTransport(FakeResponse(text="csv")))

    assert client.request_bytes("GET", "https://example.test") == b"csv"


def test_request_bytes_encodes_non_byte_content(credentials):
    response = FakeResponse()
    response.text = None
    response.content = ["csv"]
    client = BaseClient(credentials, transport=RecordingTransport(response))

    assert client.request_bytes("GET", "https://example.test") == b"['csv']"


def test_requests_transport_forwards_timeout():
    class Session:
        def __init__(self):
            self.calls = []

        def request(self, method, url, **kwargs):
            self.calls.append((method, url, kwargs))
            return FakeResponse(json_data={"ok": True})

    session = Session()
    response = RequestsTransport(session=session, timeout=12).request("GET", "https://example.test")

    assert response.json() == {"ok": True}
    assert session.calls[0][2]["timeout"] == 12

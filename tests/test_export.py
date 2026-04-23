from io import BytesIO
import json
from zipfile import ZipFile

import pytest

from pyamplitude import ExportClient
from pyamplitude.exceptions import ValidationError
from pyamplitude.export import AmplitudeExportApi, validate_export_hour

from conftest import FakeResponse, RecordingTransport


def make_archive():
    buffer = BytesIO()
    with ZipFile(buffer, "w") as zip_file:
        zip_file.writestr("events/2024-01-01_0.json", json.dumps({"event_type": "Signup"}) + "\n")
        zip_file.writestr("events/2024-01-01_1.json", "\n" + json.dumps({"event_type": "Purchase"}) + "\n")
    return buffer.getvalue()


def test_export_download_and_parse(credentials):
    archive = make_archive()
    transport = RecordingTransport(FakeResponse(content=archive))
    client = ExportClient(credentials, transport=transport)

    assert client.download_archive(start="20240101T00", end="20240101T23") == archive
    assert list(client.iter_events_from_archive(archive)) == [{"event_type": "Signup"}, {"event_type": "Purchase"}]
    assert client.export_events(start="20240101T00", end="20240101T23") == [
        {"event_type": "Signup"},
        {"event_type": "Purchase"},
    ]
    assert transport.requests[0]["params"] == [("start", "20240101T00"), ("end", "20240101T23")]


def test_export_validates_hours_and_legacy_wrapper(credentials):
    with pytest.raises(ValidationError):
        validate_export_hour("20240101")
    with pytest.raises(ValidationError):
        validate_export_hour("20240101T24")

    transport = RecordingTransport(FakeResponse(content=make_archive()))
    legacy = AmplitudeExportApi(credentials, transport=transport)

    assert legacy.get_all_events_data("20240101T00", "20240101T23")

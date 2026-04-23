from pyamplitude import AmplitudeEvent, BatchClient, HTTPV2Client, UploadOptions
from pyamplitude.ingestion import make_ingestion_credentials

from conftest import FakeResponse, RecordingTransport


def test_http_v2_upload_and_identify():
    credentials = make_ingestion_credentials("api-key")
    transport = RecordingTransport(FakeResponse(json_data={"code": 200}))
    client = HTTPV2Client(credentials, transport=transport)

    response = client.upload([AmplitudeEvent("Signup", user_id="u1")], options=UploadOptions(min_id_length=1))
    client.identify(user_id="u1", user_properties={"plan": "pro"}, insert_id="i1")

    assert response == {"code": 200}
    assert transport.requests[0]["url"] == "https://api2.amplitude.com/2/httpapi"
    assert transport.requests[0]["json"]["events"][0]["event_type"] == "Signup"
    assert transport.requests[0]["json"]["options"] == {"min_id_length": 1}
    assert transport.requests[1]["json"]["events"][0]["event_type"] == "$identify"


def test_batch_upload_supports_mappings_and_eu_region():
    credentials = make_ingestion_credentials("api-key")
    transport = RecordingTransport(FakeResponse(json_data={"events_ingested": 1}))
    client = BatchClient(credentials, region="EU", transport=transport)

    client.upload([{"event_type": "Signup", "device_id": "d1"}], options={"min_id_length": 1})

    assert transport.requests[0]["url"] == "https://api.eu.amplitude.com/batch"
    assert transport.requests[0]["json"]["api_key"] == "api-key"
    assert transport.requests[0]["headers"] == {"Content-Type": "application/json"}


def test_upload_without_options_omits_options_key():
    credentials = make_ingestion_credentials("api-key")
    transport = RecordingTransport(FakeResponse(json_data={"ok": True}))

    BatchClient(credentials, transport=transport).upload([{"event_type": "Signup", "user_id": "u1"}])

    assert "options" not in transport.requests[0]["json"]

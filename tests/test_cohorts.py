import pytest

from pyamplitude import CohortMembership, CohortsClient
from pyamplitude.behavioralcohortsapi import BehavioralCohortsApi
from pyamplitude.exceptions import ValidationError

from conftest import FakeResponse, RecordingTransport


def test_list_request_status_and_download(credentials):
    transport = RecordingTransport(
        FakeResponse(json_data={"cohorts": []}),
        FakeResponse(status_code=202, json_data={"request_id": "r1"}),
        FakeResponse(json_data={"status": "ready"}),
        FakeResponse(content=b"user_id\nu1\n"),
    )
    client = CohortsClient(credentials, transport=transport)

    assert client.list_cohorts(include_sync_info=True) == {"cohorts": []}
    assert client.request_cohort("c1", include_properties=True, property_keys=["country"]) == {"request_id": "r1"}
    assert client.request_status("r1") == {"status": "ready"}
    assert client.download_cohort("r1") == b"user_id\nu1\n"

    assert transport.requests[0]["params"] == [("includeSyncInfo", "true")]
    assert ("propKeys", "country") in transport.requests[1]["params"]
    assert transport.requests[2]["url"].endswith("/request-status/r1")
    assert transport.requests[3]["url"].endswith("/request/r1/file")


def test_cohort_methods_validate_ids(credentials):
    client = CohortsClient(credentials, transport=RecordingTransport(FakeResponse(json_data={"ok": True})))

    with pytest.raises(ValidationError):
        client.request_cohort("")
    with pytest.raises(ValidationError):
        client.request_status("")
    with pytest.raises(ValidationError):
        client.download_cohort("")


def test_upload_cohort_payload_and_validation(credentials):
    transport = RecordingTransport(FakeResponse(json_data={"cohort_id": "c1"}))
    client = CohortsClient(credentials, transport=transport)

    response = client.upload_cohort(
        name="VIP",
        app_id=123,
        id_type="BY_USER_ID",
        ids=["u1"],
        owner="owner@example.com",
        published=True,
        skip_invalid_ids=True,
    )

    assert response == {"cohort_id": "c1"}
    assert transport.requests[0]["url"].endswith("/api/3/cohorts/upload")
    assert transport.requests[0]["json"]["skip_invalid_ids"] is True
    assert "existing_cohort_id" not in transport.requests[0]["json"]

    with pytest.raises(ValidationError):
        client.upload_cohort(name="VIP", app_id=123, id_type="BAD", ids=["u1"], owner="o", published=True)
    with pytest.raises(ValidationError):
        client.upload_cohort(name="VIP", app_id=123, id_type="BY_USER_ID", ids=[], owner="o", published=True)


def test_update_membership_and_legacy_methods(credentials):
    transport = RecordingTransport(FakeResponse(json_data={"ok": True}))
    client = BehavioralCohortsApi(credentials, transport=transport)

    assert client.update_membership(
        cohort_id="c1",
        memberships=[CohortMembership(ids=["u1"], id_type="BY_ID", operation="ADD")],
        count_group="org",
        skip_invalid_ids=True,
    ) == {"ok": True}
    assert transport.requests[0]["json"]["memberships"][0]["operation"] == "ADD"

    client.update_membership(cohort_id="c1", memberships=[{"ids": ["u2"], "id_type": "BY_NAME", "operation": "REMOVE"}])
    client.get_cohort("c1", props=1, propKeys=["country"])
    assert client.list_all_cohorts() == {"ok": True}
    client.upload_cohort_from_ids(
        name="VIP",
        app_id=123,
        id_type="BY_USER_ID",
        ids=["u1"],
        owner="owner@example.com",
    )

    with pytest.raises(ValidationError):
        client.update_membership(cohort_id="", memberships=[{"ids": ["u1"]}])
    with pytest.raises(ValidationError):
        client.update_membership(cohort_id="c1", memberships=[])

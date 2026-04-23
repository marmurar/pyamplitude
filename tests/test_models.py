import json

import pytest

from pyamplitude import (
    AmplitudeCredentials,
    AmplitudeEvent,
    CohortMembership,
    DashboardEvent,
    Event,
    ProjectsHandler,
    Segment,
    UploadOptions,
)
from pyamplitude.exceptions import ConfigurationError, ValidationError
from pyamplitude.models import clean_payload
from pyamplitude.regions import get_region


def test_credentials_mask_secret_and_require_api_key():
    creds = ProjectsHandler("demo", "key", "secret")

    assert creds.basic_auth == ("key", "secret")
    assert "secret_key: ***" in repr(creds)

    with pytest.raises(ConfigurationError):
        AmplitudeCredentials(api_key="")
    with pytest.raises(ConfigurationError):
        AmplitudeCredentials(api_key="key").basic_auth


def test_regions_are_validated():
    assert get_region("eu").http_v2 == "https://api.eu.amplitude.com/2/httpapi"

    with pytest.raises(ConfigurationError):
        get_region("apac")


def test_segment_serialization_and_legacy_return_values():
    segment = Segment()

    assert segment.add_filter("country", "is", ["AR"]) is True
    assert segment.add_filter("", "is", ["AR"]) is False
    assert segment.add_filter("country", "bad", ["AR"]) is False
    assert segment.add_filter("country", "is", []) is False

    segment.add_raw({"type": "user", "prop": "platform"})
    assert segment.filter_count() == 2
    assert segment.get_filters()[0]["prop"] == "country"
    assert json.loads(str(segment))[0] == {"prop": "country", "op": "is", "values": ["AR"]}


def test_segment_convenience_factories():
    segment = Segment.user_property("country", "is", ["UY"])
    performed = Segment.who_performed("Signup", value=2, time_value=30)

    assert segment.to_payload()[0]["values"] == ["UY"]
    assert performed.to_payload()[0]["event_type"] == "Signup"

    with pytest.raises(ValidationError):
        Segment.who_performed("")
    with pytest.raises(ValidationError):
        Segment.who_performed("Signup", op="sometimes")


def test_dashboard_event_serialization_and_alias():
    event = DashboardEvent("Signup")

    assert Event is DashboardEvent
    assert event.add_filter("event", "plan", "is", ["pro"]) is True
    assert event.add_filter("bad", "plan", "is", ["pro"]) is False
    assert event.add_filter("event", "", "is", ["pro"]) is False
    assert event.add_filter("event", "plan", "bad", ["pro"]) is False
    assert event.add_filter("event", "plan", "is", []) is False
    assert event.add_groupby("user", "country") is True
    assert event.add_groupby("event", "source") is True
    assert event.add_groupby("event", "third") is False
    assert event.add_groupby("bad", "country") is False
    assert event.add_groupby("event", "") is False
    assert event.filter_count() == 1
    assert event.groupby_count() == 2
    assert event.get_groupby()[0] == {"type": "user", "value": "country"}
    assert json.loads(str(event))["event_type"] == "Signup"

    with pytest.raises(ValidationError):
        DashboardEvent("")


def test_ingestion_event_validation_and_payload():
    event = AmplitudeEvent(
        "Purchase",
        user_id="u1",
        time=123,
        event_properties={"sku": "A"},
        user_properties={"plan": "pro"},
        groups={"org": "acme"},
        group_properties={"tier": "enterprise"},
        insert_id="i1",
        extra={"platform": "web"},
    )

    payload = event.to_payload()

    assert payload["event_type"] == "Purchase"
    assert payload["platform"] == "web"
    assert payload["user_properties"] == {"plan": "pro"}

    with pytest.raises(ValidationError):
        AmplitudeEvent("", user_id="u1").to_payload()
    with pytest.raises(ValidationError):
        AmplitudeEvent("Purchase").to_payload()


def test_upload_options_and_cohort_membership_payloads():
    assert UploadOptions(min_id_length=3).to_payload() == {"min_id_length": 3}
    assert UploadOptions().to_payload() == {}

    membership = CohortMembership(ids=["u1"], id_type="BY_ID", operation="ADD")
    assert membership.to_payload() == {"ids": ["u1"], "id_type": "BY_ID", "operation": "ADD"}

    with pytest.raises(ValidationError):
        CohortMembership(ids=[], id_type="BY_ID", operation="ADD").to_payload()
    with pytest.raises(ValidationError):
        CohortMembership(ids=["u1"], id_type="BAD", operation="ADD").to_payload()
    with pytest.raises(ValidationError):
        CohortMembership(ids=["u1"], id_type="BY_ID", operation="UPSERT").to_payload()


def test_clean_payload_removes_none_only():
    assert clean_payload({"a": 1, "b": None, "c": False}) == {"a": 1, "c": False}

import json

import pytest

from pyamplitude import DashboardClient, DashboardEvent, Segment
from pyamplitude.amplituderestapi import AmplitudeRestApi
from pyamplitude.exceptions import ValidationError

from conftest import FakeResponse, RecordingTransport


def make_client(credentials, response=None):
    transport = RecordingTransport(response or FakeResponse(json_data={"ok": True}))
    return DashboardClient(credentials, transport=transport), transport


def test_active_users_builds_params(credentials):
    segment = Segment.user_property("country", "is", ["AR"])
    client, transport = make_client(credentials)

    assert client.active_users(start="20240101", end="20240102", segments=[segment], group_by=["country"]) == {
        "ok": True
    }

    request = transport.requests[0]
    assert request["url"] == "https://amplitude.com/api/2/users"
    assert request["auth"] == ("api-key", "secret")
    assert ("m", "active") in request["params"]
    assert ("g", "country") in request["params"]
    assert ("s", segment.to_json()) in request["params"]


def test_dashboard_validates_dates_modes_and_intervals(credentials):
    client, _ = make_client(credentials)

    with pytest.raises(ValidationError):
        client.active_users(start="20240101", end="20231231")
    with pytest.raises(ValidationError):
        client.active_users(start="bad", end="20240101")
    with pytest.raises(ValidationError):
        client.active_users(start="20240101", end="20240101", mode="all")
    with pytest.raises(ValidationError):
        client.active_users(start="20240101", end="20240101", interval=2)


def test_session_and_composition_methods(credentials):
    client, transport = make_client(credentials)

    client.session_length_distribution(start="20240101", end="20240101", minSessionLength=10)
    client.average_session_length(start="20240101", end="20240101")
    client.average_sessions_per_user(start="20240101", end="20240101")
    client.user_composition(start="20240101", end="20240101", properties=["country", "platform"])

    assert [request["url"].rsplit("/", 1)[-1] for request in transport.requests[:3]] == ["length", "average", "peruser"]
    assert ("p", "country") in transport.requests[3]["params"]

    with pytest.raises(ValidationError):
        client.user_composition(start="20240101", end="20240101", properties=[])


def test_event_segmentation_supports_one_or_two_events(credentials):
    event = DashboardEvent("Signup")
    event.add_filter("event", "source", "is", ["web"])
    client, transport = make_client(credentials)

    client.event_segmentation(start="20240101", end="20240101", events=[event, "Purchase"], mode="uniques", interval=7)

    params = transport.requests[0]["params"]
    assert ("m", "uniques") in params
    assert json.loads(dict(params)["e"])["event_type"] == "Signup"
    assert json.loads(dict(params)["e2"])["event_type"] == "Purchase"

    with pytest.raises(ValidationError):
        client.event_segmentation(start="20240101", end="20240101", events=[])
    with pytest.raises(ValidationError):
        client.event_segmentation(start="20240101", end="20240101", events=["a", "b", "c"])
    with pytest.raises(ValidationError):
        client.event_segmentation(start="20240101", end="20240101", events=["a"], mode="bad")


def test_user_metadata_methods(credentials):
    client, transport = make_client(credentials)

    client.event_list()
    client.user_activity(user="u1", offset=10, limit=100)
    client.user_search(user="u1")
    client.realtime_active_users(interval=5)

    assert transport.requests[0]["url"].endswith("/events/list")
    assert ("offset", 10) in transport.requests[1]["params"]
    assert transport.requests[3]["params"] == [("i", 5)]

    with pytest.raises(ValidationError):
        client.user_activity(user="")
    with pytest.raises(ValidationError):
        client.user_search(user="")
    with pytest.raises(ValidationError):
        client.realtime_active_users(interval=1)


def test_retention_and_funnel(credentials):
    segment = Segment.user_property("country", "is", ["AR"])
    client, transport = make_client(credentials)

    client.retention(
        start_event="Signup",
        return_event="Purchase",
        start="20240101",
        end="20240102",
        retention_mode="bracket",
        bracket=[0, 7],
        segments=[segment],
        group_by="country",
    )
    client.funnel(events=["Signup", "Purchase"], start="20240101", end="20240102", mode="unordered", users="new")

    assert ("rm", "bracket") in transport.requests[0]["params"]
    assert ("rb", "[0,7]") in transport.requests[0]["params"]
    assert transport.requests[1]["url"].endswith("/funnels")

    with pytest.raises(ValidationError):
        client.retention(start_event="a", return_event="b", start="20240101", end="20240101", retention_mode="bad")
    with pytest.raises(ValidationError):
        client.retention(start_event="a", return_event="b", start="20240101", end="20240101", retention_mode="bracket")
    with pytest.raises(ValidationError):
        client.funnel(events=[], start="20240101", end="20240101")
    with pytest.raises(ValidationError):
        client.funnel(events=["a"], start="20240101", end="20240101", mode="bad")
    with pytest.raises(ValidationError):
        client.funnel(events=["a"], start="20240101", end="20240101", users="all")


def test_chart_csv_query_cost_query_and_backwards_wrappers(credentials):
    transport = RecordingTransport(FakeResponse(content=b"a,b\n"), FakeResponse(json_data={"ok": True}))
    client = DashboardClient(credentials, transport=transport)

    assert client.chart_csv("chart-id") == b"a,b\n"
    assert transport.requests[0]["url"] == "https://amplitude.com/api/3/chart/chart-id/csv"
    assert client.query_cost(start="20240101", end="20240102", endpoint="users") == 8

    assert client.query("custom/endpoint", {"a": "b"}) == {"ok": True}
    assert transport.requests[-1]["url"].endswith("/custom/endpoint")

    legacy = AmplitudeRestApi(credentials, transport=transport)
    legacy.get_active_and_new_user_count("20240101", "20240101", segment_definitions=None)
    legacy.get_session_length_distribution("20240101", "20240101")
    legacy.get_average_session_length("20240101", "20240101")
    legacy.get_average_session_per_user("20240101", "20240101")
    legacy.get_user_composition("20240101", "20240101", ["country"])
    legacy.get_events("20240101", "20240101", ["Signup"])
    legacy.get_event_list()
    legacy.get_user_activity("u1")
    legacy.get_user_search("u1")
    legacy.get_realtime_active_users()

    with pytest.raises(ValidationError):
        client.chart_csv("")
    with pytest.raises(ValidationError):
        client.query("")

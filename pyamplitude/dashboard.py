"""Client for the Amplitude Dashboard REST API."""

from datetime import datetime
import json
from typing import Any, Iterable, Mapping, Optional, Sequence, Tuple, Union

from .client import BaseClient
from .credentials import AmplitudeCredentials
from .exceptions import ValidationError
from .models import DashboardEvent, Segment

Date = str
GroupBy = Optional[Union[str, Sequence[str]]]


def validate_dashboard_date(value: str, name: str = "date") -> None:
    """Validate an Amplitude Dashboard ``YYYYMMDD`` date."""

    try:
        datetime.strptime(value, "%Y%m%d")
    except ValueError as exc:
        raise ValidationError(f"{name} must be formatted as YYYYMMDD.") from exc


def calculate_days(start: str, end: str) -> int:
    """Return inclusive day count for Dashboard query cost estimation."""

    validate_dashboard_date(start, "start")
    validate_dashboard_date(end, "end")
    start_dt = datetime.strptime(start, "%Y%m%d")
    end_dt = datetime.strptime(end, "%Y%m%d")
    if end_dt < start_dt:
        raise ValidationError("end must be on or after start.")
    return (end_dt - start_dt).days + 1


def _as_group_by_items(group_by: GroupBy) -> list:
    if group_by is None:
        return []
    if isinstance(group_by, str):
        return [group_by]
    return list(group_by)


def _segments_to_params(segments: Optional[Sequence[Segment]]) -> list:
    params = []
    for segment in segments or []:
        params.append(("s", segment.to_json()))
    return params


def _event_to_json(event: Union[str, DashboardEvent]) -> str:
    if isinstance(event, DashboardEvent):
        return event.to_json()
    return json.dumps({"event_type": event}, separators=(",", ":"))


class DashboardClient(BaseClient):
    """Client for dashboard chart data and metadata."""

    CHART_TYPE_COST = {
        "events/segmentation": 1,
        "funnels": 2,
        "retention": 8,
        "users": 4,
        "sessions": 4,
    }

    def __init__(
        self,
        credentials: AmplitudeCredentials,
        *,
        region: str = "US",
        transport: Optional[Any] = None,
        timeout: float = 30.0,
        show_query_cost: bool = False,
    ) -> None:
        super().__init__(credentials, region=region, transport=transport, timeout=timeout)
        self.show_query_cost = show_query_cost

    def query_cost(
        self,
        *,
        start: str,
        end: str,
        endpoint: str,
        segments: Optional[Sequence[Segment]] = None,
        group_by: GroupBy = None,
        event_count: int = 1,
    ) -> int:
        """Estimate Dashboard REST API rate-limit cost."""

        conditions = max(1, len(segments or []))
        conditions += sum(segment.filter_count() for segment in segments or [])
        conditions += 4 * len(_as_group_by_items(group_by))
        chart_cost = self.CHART_TYPE_COST.get(endpoint, 1)
        return calculate_days(start, end) * conditions * chart_cost * event_count

    def _get(self, endpoint: str, params: Iterable[Tuple[str, Any]]) -> Any:
        return self.request_json("GET", f"{self.endpoints.dashboard}/{endpoint}", params=params, auth=True)

    @staticmethod
    def _validate_interval(interval: int) -> None:
        if interval not in {1, 7, 30}:
            raise ValidationError("interval must be one of 1, 7 or 30.")

    @staticmethod
    def _validate_dates(start: str, end: str) -> None:
        calculate_days(start, end)

    def active_users(
        self,
        *,
        start: Date,
        end: Date,
        mode: str = "active",
        interval: int = 1,
        segments: Optional[Sequence[Segment]] = None,
        group_by: GroupBy = None,
    ) -> Any:
        """Get active or new user counts."""

        self._validate_dates(start, end)
        if mode not in {"active", "new"}:
            raise ValidationError("mode must be 'active' or 'new'.")
        self._validate_interval(interval)
        params = [("start", start), ("end", end), ("m", mode), ("i", interval)]
        params.extend(_segments_to_params(segments))
        params.extend(("g", item) for item in _as_group_by_items(group_by))
        return self._get("users", params)

    def session_length_distribution(self, *, start: Date, end: Date, **bin_config: Any) -> Any:
        """Get session length distribution."""

        self._validate_dates(start, end)
        params = [("start", start), ("end", end)]
        params.extend((key, value) for key, value in bin_config.items() if value is not None)
        return self._get("sessions/length", params)

    def average_session_length(self, *, start: Date, end: Date) -> Any:
        self._validate_dates(start, end)
        return self._get("sessions/average", [("start", start), ("end", end)])

    def average_sessions_per_user(self, *, start: Date, end: Date) -> Any:
        self._validate_dates(start, end)
        return self._get("sessions/peruser", [("start", start), ("end", end)])

    def user_composition(self, *, start: Date, end: Date, properties: Sequence[str]) -> Any:
        self._validate_dates(start, end)
        if not properties:
            raise ValidationError("properties must not be empty.")
        params = [("start", start), ("end", end)]
        params.extend(("p", prop) for prop in properties)
        return self._get("composition", params)

    def event_segmentation(
        self,
        *,
        start: Date,
        end: Date,
        events: Sequence[Union[str, DashboardEvent]],
        mode: str = "totals",
        interval: int = 1,
        segments: Optional[Sequence[Segment]] = None,
    ) -> Any:
        """Query the event segmentation chart endpoint."""

        self._validate_dates(start, end)
        if mode not in {"totals", "uniques", "average", "pct_dau"}:
            raise ValidationError("mode must be one of totals, uniques, average or pct_dau.")
        self._validate_interval(interval)
        if not 1 <= len(events) <= 2:
            raise ValidationError("events must contain one or two events.")
        params = [("start", start), ("end", end), ("m", mode), ("i", interval), ("e", _event_to_json(events[0]))]
        if len(events) == 2:
            params.append(("e2", _event_to_json(events[1])))
        params.extend(_segments_to_params(segments))
        return self._get("events/segmentation", params)

    def event_list(self) -> Any:
        return self._get("events/list", [])

    def user_activity(self, *, user: str, offset: Optional[int] = None, limit: Optional[int] = None) -> Any:
        if not user:
            raise ValidationError("user is required.")
        params = [("user", user)]
        if offset is not None:
            params.append(("offset", offset))
        if limit is not None:
            params.append(("limit", limit))
        return self._get("useractivity", params)

    def user_search(self, *, user: str) -> Any:
        if not user:
            raise ValidationError("user is required.")
        return self._get("usersearch", [("user", user)])

    def realtime_active_users(self, *, interval: int = 5) -> Any:
        if interval != 5:
            raise ValidationError("Amplitude only supports interval=5 for realtime users.")
        return self._get("realtime", [("i", interval)])

    def retention(
        self,
        *,
        start_event: Union[str, DashboardEvent],
        return_event: Union[str, DashboardEvent],
        start: Date,
        end: Date,
        retention_mode: str = "n-day",
        bracket: Optional[Sequence[int]] = None,
        interval: int = 1,
        segments: Optional[Sequence[Segment]] = None,
        group_by: GroupBy = None,
    ) -> Any:
        self._validate_dates(start, end)
        self._validate_interval(interval)
        if retention_mode not in {"bracket", "rolling", "n-day"}:
            raise ValidationError("retention_mode must be bracket, rolling or n-day.")
        if retention_mode == "bracket" and not bracket:
            raise ValidationError("bracket is required when retention_mode='bracket'.")
        params = [
            ("se", _event_to_json(start_event)),
            ("re", _event_to_json(return_event)),
            ("start", start),
            ("end", end),
            ("i", interval),
        ]
        if retention_mode != "n-day":
            params.append(("rm", retention_mode))
        if bracket:
            params.append(("rb", json.dumps(list(bracket), separators=(",", ":"))))
        params.extend(_segments_to_params(segments))
        params.extend(("g", item) for item in _as_group_by_items(group_by))
        return self._get("retention", params)

    def funnel(
        self,
        *,
        events: Sequence[Union[str, DashboardEvent]],
        start: Date,
        end: Date,
        mode: str = "ordered",
        users: str = "active",
        segments: Optional[Sequence[Segment]] = None,
        group_by: GroupBy = None,
        conversion_window_seconds: int = 2592000,
    ) -> Any:
        self._validate_dates(start, end)
        if not events:
            raise ValidationError("events must not be empty.")
        if mode not in {"ordered", "unordered"}:
            raise ValidationError("mode must be ordered or unordered.")
        if users not in {"active", "new"}:
            raise ValidationError("users must be active or new.")
        params = [
            ("start", start),
            ("end", end),
            ("mode", mode),
            ("n", users),
            ("cs", conversion_window_seconds),
        ]
        params.extend(("e", _event_to_json(event)) for event in events)
        params.extend(_segments_to_params(segments))
        params.extend(("g", item) for item in _as_group_by_items(group_by))
        return self._get("funnels", params)

    def chart_csv(self, chart_id: str) -> bytes:
        if not chart_id:
            raise ValidationError("chart_id is required.")
        url = f"{self.endpoints.dashboard.rsplit('/api/2', 1)[0]}/api/3/chart/{chart_id}/csv"
        return self.request_bytes("GET", url, auth=True)

    def query(self, endpoint: str, params: Optional[Mapping[str, Any]] = None) -> Any:
        """Run a GET request against any Dashboard REST API endpoint."""

        if not endpoint:
            raise ValidationError("endpoint is required.")
        clean_endpoint = endpoint.strip("/")
        return self._get(clean_endpoint, list((params or {}).items()))

    # Backward-compatible method names.
    def get_active_and_new_user_count(self, start: str, end: str, m: str = "active", interval: int = 1,
                                      segment_definitions: Optional[Sequence[Segment]] = None,
                                      group_by: GroupBy = None) -> Any:
        return self.active_users(start=start, end=end, mode=m, interval=interval,
                                 segments=segment_definitions, group_by=group_by)

    def get_session_length_distribution(self, start: str, end: str) -> Any:
        return self.session_length_distribution(start=start, end=end)

    def get_average_session_length(self, start: str, end: str) -> Any:
        return self.average_session_length(start=start, end=end)

    def get_average_session_per_user(self, start: str, end: str) -> Any:
        return self.average_sessions_per_user(start=start, end=end)

    def get_user_composition(self, start: str, end: str, proper: Sequence[str]) -> Any:
        return self.user_composition(start=start, end=end, properties=proper)

    def get_events(self, start: str, end: str, events: Sequence[Union[str, DashboardEvent]],
                   mode: str = "totals", interval: int = 1,
                   segment_definitions: Optional[Sequence[Segment]] = None) -> Any:
        return self.event_segmentation(start=start, end=end, events=events, mode=mode,
                                       interval=interval, segments=segment_definitions)

    def get_event_list(self) -> Any:
        return self.event_list()

    def get_user_activity(self, user: str, offset: Optional[int] = None, limit: Optional[int] = None) -> Any:
        return self.user_activity(user=user, offset=offset, limit=limit)

    def get_user_search(self, user: str) -> Any:
        return self.user_search(user=user)

    def get_realtime_active_users(self, interval: int = 5) -> Any:
        return self.realtime_active_users(interval=interval)

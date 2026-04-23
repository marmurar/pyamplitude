"""Request models for Amplitude APIs."""

from dataclasses import dataclass, field
import json
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional, Sequence

from .exceptions import ValidationError

SEGMENT_OPERATORS = {
    "is",
    "is not",
    "contains",
    "does not contain",
    "less",
    "less or equal",
    "greater",
    "greater or equal",
    "set is",
    "set is not",
}

EVENT_SEGMENT_OPERATORS = SEGMENT_OPERATORS | {">", ">=", "<", "<=", "=", "!="}
SUBPROP_TYPES = {"event", "user"}
ID_TYPES = {"BY_AMP_ID", "BY_USER_ID"}
MEMBERSHIP_ID_TYPES = {"BY_ID", "BY_NAME"}
MEMBERSHIP_OPERATIONS = {"ADD", "REMOVE"}


def _require_non_empty_string(value: str, name: str) -> None:
    if not isinstance(value, str) or not value:
        raise ValidationError(f"{name} must be a non-empty string.")


def _as_list(values: Iterable[Any], name: str) -> List[Any]:
    result = list(values)
    if not result:
        raise ValidationError(f"{name} must not be empty.")
    return result


@dataclass
class Segment:
    """Dashboard segment definition.

    Segments serialize to the JSON array expected by Dashboard REST API query
    parameter ``s``.
    """

    filters: List[Dict[str, Any]] = field(default_factory=list)

    @classmethod
    def user_property(cls, prop: str, op: str, values: Sequence[str]) -> "Segment":
        segment = cls()
        segment.add_filter(prop=prop, op=op, values=list(values))
        return segment

    @classmethod
    def who_performed(
        cls,
        event_type: str,
        *,
        op: str = ">=",
        value: int = 1,
        time_type: str = "allTime",
        time_value: Optional[int] = None,
        filters: Optional[Sequence[Mapping[str, Any]]] = None,
    ) -> "Segment":
        _require_non_empty_string(event_type, "event_type")
        if op not in EVENT_SEGMENT_OPERATORS:
            raise ValidationError(f"Unsupported segment operator: {op!r}.")
        payload: Dict[str, Any] = {
            "op": op,
            "type": "event",
            "event_type": event_type,
            "filters": list(filters or []),
            "value": value,
            "time_type": time_type,
        }
        if time_value is not None:
            payload["time_value"] = time_value
        return cls(filters=[payload])

    def add_filter(self, prop: str, op: str, values: Sequence[str]) -> bool:
        """Add a user-property filter.

        Returns ``True`` for compatibility with the original API.
        """

        try:
            _require_non_empty_string(prop, "prop")
            if op not in SEGMENT_OPERATORS:
                raise ValidationError(f"Unsupported segment operator: {op!r}.")
            self.filters.append({"prop": prop, "op": op, "values": _as_list(values, "values")})
            return True
        except ValidationError:
            return False

    def add_raw(self, payload: Mapping[str, Any]) -> None:
        """Append a raw segment payload for advanced Amplitude filters."""

        self.filters.append(dict(payload))

    def get_filters(self) -> List[Dict[str, Any]]:
        return self.filters

    def filter_count(self) -> int:
        return len(self.filters)

    def to_payload(self) -> List[Dict[str, Any]]:
        return [dict(item) for item in self.filters]

    def to_json(self) -> str:
        return json.dumps(self.to_payload(), separators=(",", ":"))

    def __str__(self) -> str:
        return self.to_json()


@dataclass
class DashboardEvent:
    """Event parameter for Dashboard REST charts."""

    event_type: str
    filters: List[Dict[str, Any]] = field(default_factory=list)
    group_by: List[Dict[str, str]] = field(default_factory=list)

    def __post_init__(self) -> None:
        _require_non_empty_string(self.event_type, "event_type")

    def add_filter(
        self,
        subprop_type: str,
        subprop_key: str,
        subprop_op: str,
        subprop_values: Sequence[Any],
    ) -> bool:
        try:
            if subprop_type not in SUBPROP_TYPES:
                raise ValidationError(f"Unsupported subprop_type: {subprop_type!r}.")
            _require_non_empty_string(subprop_key, "subprop_key")
            if subprop_op not in SEGMENT_OPERATORS:
                raise ValidationError(f"Unsupported subprop_op: {subprop_op!r}.")
            self.filters.append(
                {
                    "subprop_type": subprop_type,
                    "subprop_key": subprop_key,
                    "subprop_op": subprop_op,
                    "subprop_value": _as_list(subprop_values, "subprop_values"),
                }
            )
            return True
        except ValidationError:
            return False

    def add_groupby(self, groupby_type: str, groupby_value: str) -> bool:
        try:
            if groupby_type not in SUBPROP_TYPES:
                raise ValidationError(f"Unsupported groupby_type: {groupby_type!r}.")
            _require_non_empty_string(groupby_value, "groupby_value")
            if len(self.group_by) >= 2:
                raise ValidationError("Dashboard events support at most two group_by entries.")
            self.group_by.append({"type": groupby_type, "value": groupby_value})
            return True
        except ValidationError:
            return False

    def get_filters(self) -> List[Dict[str, Any]]:
        return self.filters

    def get_groupby(self) -> List[Dict[str, str]]:
        return self.group_by

    def filter_count(self) -> int:
        return len(self.filters)

    def groupby_count(self) -> int:
        return len(self.group_by)

    def to_payload(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"event_type": self.event_type}
        if self.filters:
            payload["filters"] = [dict(item) for item in self.filters]
        if self.group_by:
            payload["group_by"] = [dict(item) for item in self.group_by]
        return payload

    def to_json(self) -> str:
        return json.dumps(self.to_payload(), separators=(",", ":"))

    def __str__(self) -> str:
        return self.to_json()


Event = DashboardEvent


@dataclass(frozen=True)
class AmplitudeEvent:
    """Event payload for HTTP V2 and Batch ingestion APIs."""

    event_type: str
    user_id: Optional[str] = None
    device_id: Optional[str] = None
    time: Optional[int] = None
    event_properties: Optional[Mapping[str, Any]] = None
    user_properties: Optional[Mapping[str, Any]] = None
    groups: Optional[Mapping[str, Any]] = None
    group_properties: Optional[Mapping[str, Any]] = None
    insert_id: Optional[str] = None
    extra: Mapping[str, Any] = field(default_factory=dict)

    def to_payload(self) -> Dict[str, Any]:
        _require_non_empty_string(self.event_type, "event_type")
        if not self.user_id and not self.device_id:
            raise ValidationError("Amplitude events require user_id or device_id.")
        payload: Dict[str, Any] = {"event_type": self.event_type}
        optional_fields = {
            "user_id": self.user_id,
            "device_id": self.device_id,
            "time": self.time,
            "event_properties": self.event_properties,
            "user_properties": self.user_properties,
            "groups": self.groups,
            "group_properties": self.group_properties,
            "insert_id": self.insert_id,
        }
        for key, value in optional_fields.items():
            if value is not None:
                payload[key] = value
        payload.update(dict(self.extra))
        return payload


@dataclass(frozen=True)
class UploadOptions:
    """Options shared by HTTP V2 and Batch upload requests."""

    min_id_length: Optional[int] = None

    def to_payload(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {}
        if self.min_id_length is not None:
            payload["min_id_length"] = self.min_id_length
        return payload


@dataclass(frozen=True)
class CohortMembership:
    """Single membership operation for Behavioral Cohorts."""

    ids: Sequence[str]
    id_type: str
    operation: str

    def to_payload(self) -> Dict[str, Any]:
        if self.id_type not in MEMBERSHIP_ID_TYPES:
            raise ValidationError(f"id_type must be one of {sorted(MEMBERSHIP_ID_TYPES)}.")
        if self.operation not in MEMBERSHIP_OPERATIONS:
            raise ValidationError(f"operation must be one of {sorted(MEMBERSHIP_OPERATIONS)}.")
        return {
            "ids": _as_list(self.ids, "ids"),
            "id_type": self.id_type,
            "operation": self.operation,
        }


def clean_payload(payload: MutableMapping[str, Any]) -> Dict[str, Any]:
    """Return a copy without keys whose value is ``None``."""

    return {key: value for key, value in payload.items() if value is not None}

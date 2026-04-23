"""Client for the Behavioral Cohorts API."""

from typing import Any, Mapping, Optional, Sequence, Union

from .client import BaseClient
from .credentials import AmplitudeCredentials
from .exceptions import ValidationError
from .models import CohortMembership, ID_TYPES, clean_payload


class CohortsClient(BaseClient):
    """Client for Behavioral Cohorts list, download and upload APIs."""

    def list_cohorts(self, *, include_sync_info: bool = False) -> Any:
        params = [("includeSyncInfo", str(include_sync_info).lower())] if include_sync_info else []
        return self.request_json("GET", self.endpoints.cohorts_v3, params=params, auth=True)

    def request_cohort(
        self,
        cohort_id: str,
        *,
        include_properties: bool = False,
        property_keys: Optional[Sequence[str]] = None,
    ) -> Any:
        if not cohort_id:
            raise ValidationError("cohort_id is required.")
        params = [("props", 1 if include_properties or property_keys else 0)]
        for key in property_keys or []:
            params.append(("propKeys", key))
        url = f"{self.endpoints.cohorts_v5}/request/{cohort_id}"
        return self.request_json("GET", url, params=params, auth=True, success=(200, 202))

    def request_status(self, request_id: str) -> Any:
        if not request_id:
            raise ValidationError("request_id is required.")
        url = f"{self.endpoints.cohorts_v5}/request-status/{request_id}"
        return self.request_json("GET", url, auth=True, success=(200, 202))

    def download_cohort(self, request_id: str) -> bytes:
        if not request_id:
            raise ValidationError("request_id is required.")
        url = f"{self.endpoints.cohorts_v5}/request/{request_id}/file"
        return self.request_bytes("GET", url, auth=True)

    def upload_cohort(
        self,
        *,
        name: str,
        app_id: int,
        id_type: str,
        ids: Sequence[str],
        owner: str,
        published: bool,
        cg: Optional[str] = None,
        skip_save: Optional[bool] = None,
        skip_invalid_ids: Optional[bool] = None,
        existing_cohort_id: Optional[str] = None,
    ) -> Any:
        if id_type not in ID_TYPES:
            raise ValidationError(f"id_type must be one of {sorted(ID_TYPES)}.")
        if not ids:
            raise ValidationError("ids must not be empty.")
        payload = clean_payload(
            {
                "name": name,
                "app_id": app_id,
                "id_type": id_type,
                "cg": cg,
                "ids": list(ids),
                "owner": owner,
                "published": published,
                "skip_save": skip_save,
                "skip_invalid_ids": skip_invalid_ids,
                "existing_cohort_id": existing_cohort_id,
            }
        )
        return self.request_json(
            "POST",
            f"{self.endpoints.cohorts_v3}/upload",
            json=payload,
            auth=True,
            headers={"Content-Type": "application/json"},
        )

    def update_membership(
        self,
        *,
        cohort_id: str,
        memberships: Sequence[Union[CohortMembership, Mapping[str, Any]]],
        count_group: Optional[str] = None,
        skip_invalid_ids: Optional[bool] = None,
    ) -> Any:
        if not cohort_id:
            raise ValidationError("cohort_id is required.")
        if not memberships:
            raise ValidationError("memberships must not be empty.")
        payload = clean_payload(
            {
                "cohort_id": cohort_id,
                "count_group": count_group,
                "memberships": [
                    membership.to_payload() if isinstance(membership, CohortMembership) else dict(membership)
                    for membership in memberships
                ],
                "skip_invalid_ids": skip_invalid_ids,
            }
        )
        return self.request_json(
            "POST",
            f"{self.endpoints.cohorts_v3}/membership",
            json=payload,
            auth=True,
            headers={"Content-Type": "application/json"},
        )

    # Backward-compatible method names.
    def get_cohort(self, cohort_id: str, props: int = 0, propKeys: Optional[Sequence[str]] = None) -> Any:
        return self.request_cohort(cohort_id, include_properties=bool(props), property_keys=propKeys)

    def list_all_cohorts(self) -> Any:
        response = self.list_cohorts()
        return response.get("cohorts", response)

    def upload_cohort_from_ids(
        self,
        name: str = "",
        app_id: int = 0,
        id_type: str = "",
        ids: Sequence[str] = (),
        owner: str = "",
        published: bool = True,
    ) -> Any:
        return self.upload_cohort(
            name=name,
            app_id=app_id,
            id_type=id_type,
            ids=ids,
            owner=owner,
            published=published,
        )


class BehavioralCohortsApi(CohortsClient):
    """Backward-compatible Behavioral Cohorts class."""

    def __init__(
        self,
        projects_handler: AmplitudeCredentials,
        show_logs: bool = False,
        *,
        region: str = "US",
        transport: Optional[Any] = None,
        timeout: float = 30.0,
    ) -> None:
        super().__init__(projects_handler, region=region, transport=transport, timeout=timeout)

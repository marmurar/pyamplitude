"""Client for the Amplitude Export API."""

from io import BytesIO
import json
import re
from typing import Any, Iterator, Optional
from zipfile import ZipFile

from .client import BaseClient
from .credentials import AmplitudeCredentials
from .exceptions import ValidationError

EXPORT_HOUR_RE = re.compile(r"^\d{8}T\d{2}$")


def validate_export_hour(value: str, name: str = "hour") -> None:
    """Validate an Export API hour formatted as ``YYYYMMDDTHH``."""

    if not EXPORT_HOUR_RE.match(value):
        raise ValidationError(f"{name} must be formatted as YYYYMMDDTHH.")
    hour = int(value[-2:])
    if hour > 23:
        raise ValidationError(f"{name} hour must be between 00 and 23.")


class ExportClient(BaseClient):
    """Client for zipped event data exports."""

    def download_archive(self, *, start: str, end: str) -> bytes:
        validate_export_hour(start, "start")
        validate_export_hour(end, "end")
        return self.request_bytes("GET", self.endpoints.export, params=[("start", start), ("end", end)], auth=True)

    @staticmethod
    def iter_events_from_archive(archive: bytes) -> Iterator[Any]:
        """Yield JSON events from an Export API zip archive."""

        with ZipFile(BytesIO(archive)) as zip_file:
            for name in zip_file.namelist():
                with zip_file.open(name) as handle:
                    for raw_line in handle:
                        line = raw_line.decode("utf-8").strip()
                        if line:
                            yield json.loads(line)

    def export_events(self, *, start: str, end: str) -> list:
        """Download and parse all events for a time range."""

        return list(self.iter_events_from_archive(self.download_archive(start=start, end=end)))

    # Backward-compatible method name.
    def get_all_events_data(self, start: str, end: str) -> bytes:
        return self.download_archive(start=start, end=end)


class AmplitudeExportApi(ExportClient):
    """Backward-compatible Export API class."""

    def __init__(
        self,
        project_handler: AmplitudeCredentials,
        show_logs: bool = False,
        *,
        region: str = "US",
        transport: Optional[Any] = None,
        timeout: float = 30.0,
    ) -> None:
        super().__init__(project_handler, region=region, transport=transport, timeout=timeout)

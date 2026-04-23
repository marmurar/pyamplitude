"""Amplitude API endpoint configuration."""

from dataclasses import dataclass
from typing import Mapping

from .exceptions import ConfigurationError


@dataclass(frozen=True)
class RegionEndpoints:
    """Base URLs for a supported Amplitude data residency region."""

    dashboard: str
    export: str
    cohorts_v3: str
    cohorts_v5: str
    http_v2: str
    batch: str


REGIONS: Mapping[str, RegionEndpoints] = {
    "US": RegionEndpoints(
        dashboard="https://amplitude.com/api/2",
        export="https://amplitude.com/api/2/export",
        cohorts_v3="https://amplitude.com/api/3/cohorts",
        cohorts_v5="https://amplitude.com/api/5/cohorts",
        http_v2="https://api2.amplitude.com/2/httpapi",
        batch="https://api2.amplitude.com/batch",
    ),
    "EU": RegionEndpoints(
        dashboard="https://analytics.eu.amplitude.com/api/2",
        export="https://analytics.eu.amplitude.com/api/2/export",
        cohorts_v3="https://analytics.eu.amplitude.com/api/3/cohorts",
        cohorts_v5="https://analytics.eu.amplitude.com/api/5/cohorts",
        http_v2="https://api.eu.amplitude.com/2/httpapi",
        batch="https://api.eu.amplitude.com/batch",
    ),
}


def get_region(region: str) -> RegionEndpoints:
    """Return endpoints for a region name."""

    normalized = region.upper()
    try:
        return REGIONS[normalized]
    except KeyError as exc:
        known = ", ".join(sorted(REGIONS))
        raise ConfigurationError(f"Unsupported Amplitude region {region!r}. Use one of: {known}.") from exc

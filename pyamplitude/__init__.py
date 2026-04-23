"""Python client for current Amplitude Analytics APIs."""

from .cohorts import BehavioralCohortsApi, CohortsClient
from .credentials import AmplitudeCredentials, ProjectsHandler
from .dashboard import DashboardClient
from .exceptions import (
    AmplitudeAuthError,
    AmplitudeBadRequest,
    AmplitudeHTTPError,
    AmplitudeRateLimitError,
    AmplitudeServerError,
    ConfigurationError,
    PyAmplitudeError,
    ValidationError,
)
from .export import AmplitudeExportApi, ExportClient
from .ingestion import BatchClient, HTTPV2Client
from .models import AmplitudeEvent, CohortMembership, DashboardEvent, Event, Segment, UploadOptions
from .redshift import AmplitudeRedshift, RedshiftClient

__all__ = [
    "AmplitudeAuthError",
    "AmplitudeBadRequest",
    "AmplitudeCredentials",
    "AmplitudeEvent",
    "AmplitudeExportApi",
    "AmplitudeHTTPError",
    "AmplitudeRateLimitError",
    "AmplitudeRedshift",
    "AmplitudeServerError",
    "BatchClient",
    "BehavioralCohortsApi",
    "CohortMembership",
    "CohortsClient",
    "ConfigurationError",
    "DashboardClient",
    "DashboardEvent",
    "Event",
    "ExportClient",
    "HTTPV2Client",
    "ProjectsHandler",
    "PyAmplitudeError",
    "RedshiftClient",
    "Segment",
    "UploadOptions",
    "ValidationError",
]

__version__ = "2.0.0"

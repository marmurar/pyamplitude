"""Backward-compatible import path for Dashboard REST API."""

from .dashboard import DashboardClient


class AmplitudeRestApi(DashboardClient):
    """Compatibility wrapper preserving the original constructor names."""

    def __init__(self, project_handler, show_logs=False, show_query_cost=False, **kwargs):
        super().__init__(project_handler, show_query_cost=show_query_cost, **kwargs)

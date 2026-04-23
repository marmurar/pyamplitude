"""Backward-compatible request resources."""

from .credentials import ProjectsHandler
from .models import DashboardEvent, Event, Segment

__all__ = ["DashboardEvent", "Event", "ProjectsHandler", "Segment"]

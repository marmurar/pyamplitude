#!/usr/bin/env python3
"""Minimal MCP server exposing high-signal repository resources."""

from pathlib import Path

from mcp.server.fastmcp import FastMCP


ROOT = Path(__file__).resolve().parents[2]
mcp = FastMCP("pyamplitude-repo")


def _read(rel_path: str) -> str:
    path = ROOT / rel_path
    return path.read_text(encoding="utf-8")


@mcp.resource("pyamplitude://readme")
def readme() -> str:
    return _read("README.md")


@mcp.resource("pyamplitude://architecture")
def architecture() -> str:
    return _read("ai/architecture-map.md")


@mcp.resource("pyamplitude://docs/current-api")
def docs_current_api() -> str:
    return _read("docs/source/current_api.rst")


@mcp.resource("pyamplitude://docs/release")
def docs_release() -> str:
    return _read("docs/source/release.rst")


@mcp.resource("pyamplitude://tests/overview")
def tests_overview() -> str:
    return "\n".join(
        [
            _read("tests/conftest.py"),
            _read("tests/test_client.py"),
            _read("tests/test_dashboard.py"),
            _read("tests/test_export.py"),
            _read("tests/test_cohorts.py"),
            _read("tests/test_ingestion.py"),
            _read("tests/test_models.py"),
            _read("tests/test_redshift.py"),
            _read("tests/test_import_compatibility.py"),
        ]
    )


@mcp.resource("pyamplitude://module/dashboard")
def module_dashboard() -> str:
    return _read("pyamplitude/dashboard.py")


if __name__ == "__main__":
    mcp.run()


![PyAmplitude logo](https://raw.githubusercontent.com/marmurar/pyamplitude/v2.0.0/logo.png)

# PyAmplitude

[![CI](https://github.com/marmurar/pyamplitude/actions/workflows/ci.yml/badge.svg?branch=develop)](https://github.com/marmurar/pyamplitude/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/marmurar/pyamplitude/branch/develop/graph/badge.svg)](https://codecov.io/gh/marmurar/pyamplitude)
[![Git tag](https://img.shields.io/github/v/tag/marmurar/pyamplitude?sort=semver)](https://github.com/marmurar/pyamplitude/tags)
[![PyPI version](https://img.shields.io/pypi/v/pyamplitude.svg)](https://pypi.org/project/pyamplitude/)
[![PyPI downloads](https://img.shields.io/pypi/dm/pyamplitude.svg)](https://pypi.org/project/pyamplitude/)
[![Python versions](https://img.shields.io/pypi/pyversions/pyamplitude.svg)](https://pypi.org/project/pyamplitude/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE.txt)

`pyamplitude` is a modern, offline-testable Python client for Amplitude Analytics APIs.

This rewrite targets the current Amplitude API families instead of the legacy 2017
Dashboard-only surface:

- Dashboard REST API
- Export API
- Behavioral Cohorts API, including asynchronous cohort export requests
- HTTP V2 ingestion API
- Batch Event Upload API
- Optional Redshift helpers for historical Amplitude exports

The package is designed to be tested without real Amplitude credentials. Every
client accepts an injectable transport, so unit tests can validate URLs, auth,
query parameters, JSON payloads, response parsing and error handling locally.

## Installation

```bash
pip install pyamplitude
```

For local development:

```bash
python -m pip install -e ".[dev]"
python -m pytest
```

For optional Redshift support:

```bash
python -m pip install "pyamplitude[redshift]"
```

## Credentials

Dashboard, Export and Behavioral Cohorts use Basic Auth with an API key and secret key:

```python
from pyamplitude import AmplitudeCredentials

credentials = AmplitudeCredentials(
    api_key="AMPLITUDE_API_KEY",
    secret_key="AMPLITUDE_SECRET_KEY",
    project_name="production",
)
```

HTTP V2 and Batch ingestion only require the API key:

```python
from pyamplitude.ingestion import make_ingestion_credentials

credentials = make_ingestion_credentials("AMPLITUDE_API_KEY")
```

US and EU regions are supported:

```python
from pyamplitude import BatchClient

client = BatchClient(credentials, region="EU")
```

## Ingest Events

```python
from pyamplitude import AmplitudeEvent, HTTPV2Client
from pyamplitude.ingestion import make_ingestion_credentials

client = HTTPV2Client(make_ingestion_credentials("AMPLITUDE_API_KEY"))

client.upload([
    AmplitudeEvent(
        event_type="Signup",
        user_id="user-123",
        event_properties={"source": "docs"},
        insert_id="signup-user-123",
    )
])
```

## Query Dashboard Charts

```python
from pyamplitude import AmplitudeCredentials, DashboardClient, Segment

credentials = AmplitudeCredentials(api_key="key", secret_key="secret")
client = DashboardClient(credentials)

segment = Segment.user_property("country", "is", ["Uruguay"])

data = client.active_users(
    start="20240101",
    end="20240131",
    mode="active",
    interval=1,
    segments=[segment],
    group_by="country",
)
```

## Export Events

```python
from pyamplitude import AmplitudeCredentials, ExportClient

client = ExportClient(AmplitudeCredentials(api_key="key", secret_key="secret"))
events = client.export_events(start="20240101T00", end="20240101T23")
```

## Behavioral Cohorts

```python
from pyamplitude import AmplitudeCredentials, CohortsClient

client = CohortsClient(AmplitudeCredentials(api_key="key", secret_key="secret"))

job = client.request_cohort("cohort-id", include_properties=True)
status = client.request_status(job["request_id"])
archive = client.download_cohort(job["request_id"])
```

## Compatibility Imports

The old import paths still exist as wrappers:

```python
from pyamplitude.amplituderestapi import AmplitudeRestApi
from pyamplitude.behavioralcohortsapi import BehavioralCohortsApi
from pyamplitude.exportapi import AmplitudeExportApi
from pyamplitude.projectshandler import ProjectsHandler
```

New code should prefer `DashboardClient`, `CohortsClient`, `ExportClient`,
`HTTPV2Client` and `BatchClient`.

## Testing Without API Keys

The project does not require real Amplitude credentials for normal test runs.

```bash
python -m pytest
```

Integration tests should be marked with `@pytest.mark.integration` and skipped unless
these environment variables exist:

- `AMPLITUDE_API_KEY`
- `AMPLITUDE_SECRET_KEY`
- `AMPLITUDE_PROJECT_ID`

## Documentation

Sphinx documentation lives in `docs/source`.

```bash
python -m sphinx -b html docs/source docs/_build/html
```

Project status badges in this README and the Sphinx documentation track the
`develop` branch until a release branch is promoted.

Release builds use semantic version tags such as `v2.0.0`. The PyPI long
description is sourced from this README through `pyproject.toml`.

Current Amplitude API references:

- https://www.docs.developers.amplitude.com/analytics/apis/dashboard-rest-api/
- https://amplitude.com/docs/apis/analytics/export
- https://amplitude.com/docs/apis/analytics/behavioral-cohorts
- https://amplitude.com/docs/apis/analytics/http-v2
- https://amplitude.com/docs/apis/analytics/batch-event-upload

# PyAmplitude Architecture Map (AI-Oriented)

## 1) What this repository is

`pyamplitude` is a Python client library for Amplitude APIs with:

- modern package metadata (`pyproject.toml`)
- offline-first tests (`tests/` with fake transports)
- Sphinx docs (`docs/source/`)
- compatibility wrappers for legacy imports

## 2) Package layout

Core package folder: `pyamplitude/`

- `client.py`: base HTTP request layer (`BaseClient`)
- `transport.py`: transport abstraction (`RequestsTransport`)
- `credentials.py`: credentials models and legacy `ProjectsHandler`
- `regions.py`: endpoint registry for US/EU
- `exceptions.py`: typed exception hierarchy
- `models.py`: request/domain models used by clients
- `dashboard.py`: Dashboard REST API client
- `export.py`: Export API client
- `cohorts.py`: Behavioral Cohorts API client
- `ingestion.py`: HTTP V2 and Batch ingestion clients
- `redshift.py`: optional Redshift helper client

Legacy compatibility modules:

- `amplituderestapi.py`
- `behavioralcohortsapi.py`
- `exportapi.py`
- `amplituderedshift.py`
- `apiresources.py`
- `projectshandler.py`

These keep old import paths stable while delegating to the modern clients.

## 3) Runtime architecture

1. User code instantiates credentials (`AmplitudeCredentials`).
2. User code creates a concrete client (`DashboardClient`, `ExportClient`, etc).
3. Concrete client composes URL + params/body and calls `BaseClient`.
4. `BaseClient` sends request through injected transport.
5. Responses are mapped to JSON/bytes and normalized into typed errors.

Design seam for testing:

- All network calls go through `transport.request(...)`.
- Tests replace transport with fakes; no real network is required.

## 4) Testing architecture

Test root: `tests/`

- `conftest.py`: shared fake response/transport primitives
- client-level tests: `test_dashboard.py`, `test_export.py`, `test_cohorts.py`, `test_ingestion.py`, `test_redshift.py`
- model/contract tests: `test_models.py`, `test_client.py`
- compatibility tests: `test_import_compatibility.py`

Coverage gate is configured in `pyproject.toml`.

## 5) Documentation architecture

Docs root: `docs/source/`

- `index.rst`: entry point and badges
- `quickstart.rst`: usage examples
- `current_api.rst`: API family coverage
- `offline_testing.rst`: testing strategy
- `release.rst`: release and publish process
- `status.rst`: CI/coverage/repo status
- `reference.rst`: autodoc API reference

## 6) Release architecture

- version source of truth: `pyproject.toml`
- package constant: `pyamplitude/__init__.py` (`__version__`)
- CI workflow: `.github/workflows/ci.yml`
- publish workflow: `.github/workflows/publish.yml`
- release tags: `vX.Y.Z`

Current known release line includes `v2.0.0`.

## 7) How an AI agent should approach changes

1. Start by reading:
   - `README.md`
   - `ai/architecture-map.md`
   - `docs/source/current_api.rst`
2. Preserve compatibility wrappers unless explicitly removing legacy paths.
3. Prefer adding behavior in modern modules (`dashboard.py`, `cohorts.py`, etc).
4. Add/adjust tests in `tests/` for every user-visible behavior change.
5. Run:
   - `python3 -m pytest`
   - `python3 -m sphinx -b html docs/source docs/_build/html`
6. Keep `master` aligned to release policy used by maintainers.


# Skill: pyamplitude-repo-maintainer

## Purpose

Help an AI agent modify `pyamplitude` safely while preserving:

- API behavior
- compatibility wrappers
- testing and release quality bars

## Fast context load

Read in this order:

1. `README.md`
2. `ai/architecture-map.md`
3. `docs/source/current_api.rst`
4. `pyproject.toml`
5. target module + matching test file(s)

## Repository contracts

- Modern implementation is in:
  - `pyamplitude/dashboard.py`
  - `pyamplitude/export.py`
  - `pyamplitude/cohorts.py`
  - `pyamplitude/ingestion.py`
  - `pyamplitude/redshift.py`
- Compatibility paths must keep working:
  - `pyamplitude/amplituderestapi.py`
  - `pyamplitude/behavioralcohortsapi.py`
  - `pyamplitude/exportapi.py`
  - `pyamplitude/amplituderedshift.py`
  - `pyamplitude/apiresources.py`
  - `pyamplitude/projectshandler.py`

## Engineering rules for this repo

1. Prefer extending modern modules instead of wrappers.
2. Keep transport injection testable; avoid hard-coding network behavior.
3. Use typed errors from `pyamplitude/exceptions.py`.
4. Add tests for each behavior change.
5. Keep docs in sync when public API changes.

## Required verification

Run all:

```bash
python3 -m pytest
python3 -m sphinx -b html docs/source docs/_build/html
```

If release-facing changes are made, also run:

```bash
python3 -m build --no-isolation
python3 -m twine check dist/*
```

## Release expectations

- version comes from `pyproject.toml` (must match `pyamplitude/__init__.py`)
- release tags use `vX.Y.Z`
- workflows:
  - `.github/workflows/ci.yml`
  - `.github/workflows/publish.yml`


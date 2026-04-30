# PyAmplitude MCP (Starter)

This directory contains a minimal Model Context Protocol server that exposes
key repository files as MCP resources so AI tooling can load high-signal context
without scanning the whole tree.

## What it exposes

- `pyamplitude://readme`
- `pyamplitude://architecture`
- `pyamplitude://docs/current-api`
- `pyamplitude://docs/release`
- `pyamplitude://tests/overview`
- `pyamplitude://module/dashboard`

## Run locally

```bash
cd ai/mcp
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
python server.py
```

## Notes

- This is intentionally small and file-resource oriented.
- It is safe for repository onboarding and architecture discovery.
- Add tool endpoints only after agreeing on specific automation needs.


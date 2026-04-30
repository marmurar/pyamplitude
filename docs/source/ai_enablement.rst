AI Enablement
=============

The repository includes a starter AI onboarding bundle with:

- an architecture map
- a maintainer skill guide
- a minimal MCP server for high-signal repository resources

Files:

- ``ai/architecture-map.md``
- ``ai/skill/SKILL.md``
- ``ai/mcp/README.md``
- ``ai/mcp/server.py``

Architecture Map
----------------

The map documents package layout, runtime flow, testing design and release
contracts so an AI agent can orient quickly.

Skill
-----

The skill defines guardrails for safe changes:

- extend modern modules first
- preserve legacy wrappers
- update tests and docs for public behavior changes
- run repository verification commands

MCP
---

The MCP server is intentionally small and resource-focused. It exposes:

- ``pyamplitude://readme``
- ``pyamplitude://architecture``
- ``pyamplitude://docs/current-api``
- ``pyamplitude://docs/release``
- ``pyamplitude://tests/overview``
- ``pyamplitude://module/dashboard``

It is a practical base for future expansion to custom tools.


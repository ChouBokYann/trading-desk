---
name: tm-setup
description: Setup and initialize The Money execution engine. Use when the user requests to 'set up The Money', 'initialize tm', or 'install the quant engine'.
---

# The Money — Setup

## Overview

This skill initializes The Money quant execution engine — scaffolding the LLM wiki (Karpathy-style knowledge base), the quantitative signal database, collecting user configuration, validating external dependencies, and scaffolding the Python execution daemon project. It handles both fresh installs and upgrades (detects existing state and preserves data).

Act as a systems engineer setting up trading infrastructure. The user is a trader who wants to get from zero to paper-trading-ready. Be efficient — collect what's needed, validate it works, move on.

**Args:** None. Run interactively.

**Module:** `tm` (The Money). Expands the Trading Desk Companion.

## Conventions

- Bare paths (e.g. `references/guide.md`) resolve from the skill root.
- `{skill-root}` resolves to this skill's installed directory.
- `{project-root}`-prefixed paths resolve from the project working directory.

## On Activation

Load available config from `{project-root}/_bmad/config.yaml` and `{project-root}/_bmad/config.user.yaml` (root level and `tm` section). If config is missing, this IS the setup skill — proceed with defaults and create the config.

Detect install state:

- **Fresh install:** `{project-root}/_bmad/memory/tm/` does not exist → run all stages
- **Upgrade:** Wiki directory exists → preserve existing data, run only stages that need updating (skip scaffold, re-validate deps, offer to update config)

Route to stages:

1. **Infrastructure** — Load `references/01-infrastructure.md`. Scaffold wiki, create SQLite database, scaffold daemon project.
2. **Configuration** — Load `references/02-configuration.md`. Collect user preferences, validate MCP dependencies.
3. **Onboarding** — Load `references/03-onboarding.md`. Check desk integration, run wiki onboarding conversation to populate initial knowledge.

On completion, summarize what was created and suggest next steps: run `tm-regime` to get an initial regime assessment, then talk to The Quant for an initial strategy session.

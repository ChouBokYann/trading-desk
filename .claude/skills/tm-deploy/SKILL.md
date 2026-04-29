---
name: tm-deploy
description: Execute trades through the full pre-trade pipeline. Use when the user requests 'deploy signal', 'execute trade', 'pre-trade check', or 'manage positions'.
---

# The Money -- Deploy

## Overview

This skill takes a trade signal -- from the desk's `/analyze` output, an `/alpha` chain, or manual input -- and runs it through the full deployment pipeline: signal validation, seven pre-trade gates (ALL must pass), risk-based position sizing, correlation check, bracket order construction, and execution via Alpaca. Signals that don't clear every gate don't trade. No exceptions.

Beyond entry, this skill manages the full position lifecycle: trailing stop adjustments, pyramid entries on confirmed pullbacks, partial exits at profit targets, and time-based decay review for stale positions.

Act as a disciplined execution desk. Your job is to enforce the rules, not interpret them. When a gate fails, report what failed and why -- don't look for workarounds.

**Module:** `tm` (The Money)

**Capabilities:**

- **Deploy** (default) -- Full pipeline: intake -> checklist -> size -> execute. Accepts a ticker, signal JSON, or reference to an alpha-chain file.
- **Manage** -- Position lifecycle: trailing stops, pyramids, partial exits across all open positions.
- **Decay Check** -- Flag positions past their freshness window for thesis revalidation.
- **Queue** -- Show and act on pending Tier B confirmation queue.
- **Priority Rank** -- When multiple signals are pending, rank by edge x fit x regime and deploy the top pick.

**Args:** Capability name and/or ticker. Examples: `AAPL`, `manage`, `decay-check`, `queue`, `AAPL --manual`.

## Conventions

- Bare paths (e.g. `references/guide.md`) resolve from the skill root.
- `{project-root}`-prefixed paths resolve from the project working directory.

## On Activation

Load available config from `{project-root}/_bmad/config.yaml` and `{project-root}/_bmad/config.user.yaml` (root level and `tm` section). If config is missing, let the user know `tm-setup` can configure the module at any time. Use sensible defaults for anything not configured.

Load context:

1. Read `{project-root}/_bmad/memory/tm/wiki/index.md` -- orient to wiki state
2. Read the current regime state -- check for a recent regime snapshot in `{project-root}/_bmad/memory/tm/raw/regime-snapshots/` or invoke `tm-regime` if stale (>4 hours)
3. Query current positions via `alpaca:get_all_positions`
4. Query portfolio value via `alpaca:get_account_info`

Route by args:

- Ticker or signal -> **Deploy** (below)
- `manage` -> load `references/position-management.md`
- `decay-check` -> load `references/position-management.md`, run decay section only
- `queue` -> show pending Tier B orders from the confirmation queue, allow approve/reject
- `priority` or multiple signals -> load `references/execution-pipeline.md`, run priority ranking

## Deploy Pipeline

The core path. Load references progressively as each stage completes.

### Stage 1: Signal Intake

Load `references/signal-intake.md`. Normalize the signal into the standard schema regardless of source (desk output, alpha chain file, or manual input from user).

### Stage 2: Pre-Trade Checklist

Load `references/pre-trade-checklist.md`. Run all seven gates against the normalized signal. ALL must pass. Present results as an itemized go/no-go table with data for each gate.

If any gate fails: present the failure report, explain what would need to change, and stop. No partial deployment.

### Stage 3: Size, Construct, Execute

Load `references/execution-pipeline.md`. Calculate position size, check correlation, construct bracket order, and execute per autonomy tier.

### Output

Every deployment attempt (successful or failed) writes to:

- `{project-root}/_bmad/memory/tm/raw/trade-logs/` -- trade entry record or rejection record
- `tm-signals.db` -- signal history update
- `{project-root}/_bmad/memory/tm/wiki/log.md` -- append activity entry

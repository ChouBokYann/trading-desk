---
name: tm-synthesis
description: Periodic synthesis of trading performance and wiki knowledge. Use when the user requests 'weekly digest', 'strategy review', 'wiki lint', or 'quarterly review'.
---

# The Money -- Synthesis

## Overview

This skill runs periodic synthesis -- reading the quant layer and wiki to distill cross-trade patterns, update strategy EV, recalibrate signal source weights, and detect macro-level causality invisible at the individual trade level. A single trade review sees one data point; synthesis sees the pattern across twenty.

Act as a research analyst conducting a systematic review. Your job is to find the signal in the noise -- which strategies are actually working, which signal sources are predictive, and what regime patterns keep repeating.

**Module:** `tm` (The Money)

**Capabilities:**

- **Weekly Digest** (default) -- Performance summary with pattern highlights. The primary cadence.
- **Strategy EV** -- Recalculate expected value per setup type from the quant layer.
- **Source Recalibration** -- Update signal source accuracy rankings and conviction thresholds.
- **Regime Patterns** -- Extract regime insights from accumulated snapshots and trade outcomes.
- **Cross-Trade Causality** -- Find macro patterns across batches of recent post-mortems.
- **Quarterly Review** -- Comprehensive system health assessment with allocation recommendations.
- **Wiki Lint** -- Health check: contradictions, stale pages, orphans, missing cross-references.

**Args:** Capability name. No args = weekly digest. Examples: `weekly`, `strategy-ev`, `source-recal`, `regime-patterns`, `quarterly`, `lint`.

## Conventions

- Bare paths (e.g. `references/guide.md`) resolve from the skill root.
- `{project-root}`-prefixed paths resolve from the project working directory.

## On Activation

Load available config from `{project-root}/_bmad/config.yaml` and `{project-root}/_bmad/config.user.yaml` (root level and `tm` section). If config is missing, let the user know `tm-setup` can configure the module at any time. Use sensible defaults for anything not configured.

Load context:

1. Read `{project-root}/_bmad/memory/tm/wiki/index.md` -- orient to wiki state
2. Read `{project-root}/_bmad/memory/tm/wiki/overview.md` -- current system state
3. Read `{project-root}/_bmad/memory/tm/wiki/log.md` -- recent activity

Route by args:

- No args or `weekly` -> load `references/weekly-digest.md`
- `strategy-ev` -> load `references/strategy-analysis.md`, run EV section
- `source-recal` -> load `references/strategy-analysis.md`, run source recalibration section
- `regime-patterns` -> load `references/pattern-extraction.md`, run regime section
- `cross-causality` -> load `references/pattern-extraction.md`, run causality section
- `quarterly` -> load all references, run full quarterly review
- `lint` -> load `references/wiki-lint.md`

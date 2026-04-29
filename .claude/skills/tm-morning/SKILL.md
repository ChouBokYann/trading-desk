---
name: tm-morning
description: Automated morning trading workflow — regime scan, pre-market watchlist, signal evaluation, and deployment. Manages context via subagents and file-based artifact passing.
---

# The Money — Morning Workflow

## Overview

This skill orchestrates the full morning trading session as an automated pipeline. It chains regime scanning, pre-market scanning, signal evaluation, and trade deployment — each in isolated contexts to prevent context overflow.

**Module:** `tm` (The Money)

**Args:** Optional phase to start from. No args = run full pipeline from Phase 1.
- `full` — run complete pipeline (default)
- `scan` — skip regime (use existing), start at scanner
- `screen` — skip regime + scan, run qualitative screen on today's watchlist
- `evaluate` — skip to quantitative evaluation (uses existing qualitative data)
- `deploy` — skip to deploy, act on today's existing evaluations

## Architecture: Context-Managed Pipeline

The pipeline uses **subagents for heavy work** and **files for state passing**. The main context stays lean — it orchestrates, reads summaries, and makes decisions. It never carries raw MCP output or full strategy page content.

```
Phase 1: REGIME     ──→  writes wiki/regimes/YYYY-MM-DD.md
                           │
Phase 2: SCAN       ──→  writes raw/watchlists/YYYY-MM-DD.json
                           │
Phase 2.5: SCREEN   ──→  Desk agents (Nadia/Tara/Frank/Sage) evaluate candidates
  ├── 2.5a: Prefetch ──→  writes raw/prefetched/YYYY-MM-DD/TICKER.json
  └── 2.5b: Agents   ──→  writes raw/qualitative/YYYY-MM-DD/composite.json
                           │
Phase 3: EVALUATE   ──→  writes raw/evaluations/YYYY-MM-DD/TICKER.json
                           │
Phase 4: PRIORITIZE ──→  ranks GO signals, presents to user
                           │
Phase 5: DEPLOY     ──→  executes via Alpaca, writes raw/trade-logs/
                           │
Phase 6: SUMMARY    ──→  prints session recap
```

**Phase 2.5 bridges the Trading Desk into The Money.** Four BMad desk agents (Nadia, Tara, Frank, Sage) provide qualitative intelligence that the quant layer is blind to: catalysts, chart depth, fundamental quality, and crowding risk. See `references/qualitative-screen.md`.

Each arrow is a **file handoff** — the next phase reads artifacts from disk, not from conversation context.

## Conventions

- Bare paths (e.g. `references/workflow-phases.md`) resolve from the skill root.
- `{project-root}`-prefixed paths resolve from the project working directory.
- Dates use the format `YYYY-MM-DD` throughout.

## On Activation

1. Load config from `{project-root}/_bmad/config.yaml` and `{project-root}/_bmad/config.user.yaml`
2. Read `{project-root}/_bmad/memory/tm/wiki/index.md` — orient to wiki state
3. Check for existing artifacts from today:
   - Regime: `{project-root}/_bmad/memory/tm/wiki/regimes/` — any file from today?
   - Watchlist: `{project-root}/_bmad/memory/tm/raw/watchlists/YYYY-MM-DD.json`
   - Evaluations: `{project-root}/_bmad/memory/tm/raw/evaluations/YYYY-MM-DD/`
4. Route by args — skip phases that already have today's artifacts (unless `full` forces rerun)
5. Load `references/workflow-phases.md` for detailed phase instructions

Greet the user, report which phases have existing artifacts, and confirm the pipeline start point.

## Phase Execution

Load `references/workflow-phases.md` and follow each phase's instructions. Key principles:

### Subagent Rules

- **Regime scan** → 1 subagent (default model). Prompt includes methodology path and MCP tool names. Writes regime YAML to wiki.
- **Qualitative screen** → 3-4 parallel subagents (Nadia, Tara, Frank, optionally Sage). Each is a BMad desk agent running in pipeline subagent mode. See `references/qualitative-screen.md` for prompt templates and output schemas.
- **Signal evaluation** → 1 subagent per strategy that has candidates (max 6, usually 3-4). Each subagent evaluates all candidates for its strategy. Prompt includes strategy page path, regime summary, AND qualitative composite data.
- **Deployment** → 1 subagent per approved trade (or batched if autonomy=A). Prompt includes signal evaluation result and Alpaca instructions.

### File Artifact Paths

| Artifact | Path | Format |
|----------|------|--------|
| Regime snapshot | `{project-root}/_bmad/memory/tm/wiki/regimes/YYYY-MM-DD-*.md` | Markdown with YAML frontmatter |
| Watchlist | `{project-root}/_bmad/memory/tm/raw/watchlists/YYYY-MM-DD.json` | JSON |
| Prefetched data | `{project-root}/_bmad/memory/tm/raw/prefetched/YYYY-MM-DD/TICKER.json` | JSON per ticker (yfinance) |
| Qualitative scores | `{project-root}/_bmad/memory/tm/raw/qualitative/YYYY-MM-DD/composite.json` | JSON composite |
| Evaluations | `{project-root}/_bmad/memory/tm/raw/evaluations/YYYY-MM-DD/TICKER.json` | JSON per ticker |
| Trigger rules | `{project-root}/_bmad/memory/tm/raw/triggers/YYYY-MM-DD/TICKER.yaml` | YAML per ticker — read by daemon |
| Trade logs | `{project-root}/_bmad/memory/tm/raw/trade-logs/YYYY-MM-DD-TICKER.json` | JSON per trade |

### Context Budget

The orchestrator's main context should:
- Never load full strategy pages (subagents do that)
- Never carry raw MCP responses (subagents summarize)
- Read only the JSON summaries from artifact files
- Print concise progress updates between phases

### Autonomy Handling

Read `default_autonomy` from config:
- **A (full auto):** Deploy all GO signals without confirmation (paper mode only)
- **B (confirm):** Present ranked GO signals, wait for user approval before each deploy
- **C (advisory):** Present recommendations only, user deploys manually

### Error Handling

- If regime scan fails: use most recent existing regime (warn user it may be stale)
- If scanner fails: fall back to manual watchlist (ask user for tickers)
- If a signal evaluation subagent fails: skip that ticker, continue with others
- If deployment fails: log the failure, continue with remaining trades
- Never halt the entire pipeline for a single-ticker failure

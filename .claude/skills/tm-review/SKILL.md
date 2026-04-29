---
name: tm-review
description: Post-trade review with causal attribution. Use when the user requests 'review trade', 'post-mortem', 'thesis check', or 'contact trace'.
---

# The Money -- Review

## Overview

This skill closes the learning loop. Every closed trade gets a causal post-mortem: not just "did it win?" but "WHY did it win or lose?" using a 6-category factor taxonomy. The review writes immutable raw sources, updates the wiki with new evidence, records outcomes in the quant layer, and journals to Obsidian. A single review may touch 5-15 wiki pages.

For open positions, a live thesis check catches thesis breaks BEFORE the stop is hit -- the earlier you detect a broken thesis, the more capital you preserve.

Act as a forensic analyst. Your job is attribution, not judgment. Find the causal chain, tag the factors, file the evidence. Let the data speak.

**Module:** `tm` (The Money)

**Capabilities:**

- **Post-Mortem** (default) -- Full review of a closed trade: causal attribution, wiki update, quant layer update, Obsidian journal.
- **Thesis Check** -- Evaluate open positions for thesis integrity. Catches weakening or broken theses on live positions.
- **Contact Trace** -- After a significant loss, map causal factors across all open positions to identify contagion risk. Auto-triggers on losses >= 2% of portfolio.

**Args:** Ticker of the closed trade, or `thesis-check` / `contact-trace` for those capabilities. Examples: `AAPL`, `thesis-check`, `contact-trace AAPL`.

## Conventions

- Bare paths (e.g. `references/guide.md`) resolve from the skill root.
- `{project-root}`-prefixed paths resolve from the project working directory.

## On Activation

Load available config from `{project-root}/_bmad/config.yaml` and `{project-root}/_bmad/config.user.yaml` (root level and `tm` section). If config is missing, let the user know `tm-setup` can configure the module at any time. Use sensible defaults for anything not configured.

Load context:

1. Read `{project-root}/_bmad/memory/tm/wiki/index.md` -- orient to wiki state
2. Query current positions via `alpaca:get_all_positions`
3. Query portfolio value via `alpaca:get_account_info`
4. Read `{project-root}/_bmad/memory/tm/wiki/log.md` -- recent activity for context

Route by args:

- Ticker -> **Post-Mortem**: load `references/post-mortem.md`
- `thesis-check` -> **Thesis Check**: load `references/thesis-check.md`
- `contact-trace` (with optional ticker) -> **Contact Trace**: load `references/post-mortem.md`, run contact tracing section

## Post-Mortem Pipeline

The core path for closed trades.

### Stage 1: Gather Evidence

Load `references/post-mortem.md`. Reconstruct the full trade timeline: entry signal, checklist results, execution, price action during hold, exit trigger, and final outcome.

### Stage 2: Attribute Causes

Using the 6-category causal taxonomy, identify the dominant factors that drove the outcome. Gather concurrent market events and news to build the evidence chain.

### Stage 3: Update Everything

Load `references/wiki-integration.md`. Write the raw trade log, update wiki pages (ticker, regime, strategy, causal factors, post-mortem), update the quant layer, and write the Obsidian journal entry.

If the trade was a loss >= 2% of portfolio, automatically trigger contact tracing before finishing.

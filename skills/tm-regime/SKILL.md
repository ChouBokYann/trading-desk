---
name: tm-regime
description: Assess market regime across macro, sector, and stock layers. Use when the user requests 'regime check', 'market regime', or 'safety car status'.
---

# The Money — Regime Assessment

## Overview

This skill assesses the current market regime using a three-layer hierarchical model: macro (yield curve, VIX, breadth), sector (rotation, relative strength), and stock-level (momentum propagation). It produces a regime state object consumed by `tm-deploy` (as a pre-trade gate) and The Quant (for strategic decisions).

Act as a quantitative macro analyst. Report what the data shows — no spin, no narrative bias. When signals conflict across layers, say so explicitly rather than forcing a consensus.

**Module:** `tm` (The Money)

**Capabilities:**
- **Full Regime Scan** — default. Runs all layers, produces composite regime state.
- **Distribution Days** — standalone. IBD-method distribution day count for major indexes.
- **R0 Propagation** — standalone. Momentum spread velocity across sectors.
- **Safety Car Check** — standalone. Circuit breaker evaluation (VIX, daily moves, yield curve).
- **Breadth Analysis** — standalone. Advance/decline, new highs/lows, breadth score.
- **Regime Snapshot** — writes current regime state to `raw/regime-snapshots/` for wiki memory.

**Args:** Optional capability name to run standalone (e.g., `distribution-days`, `safety-car`). No args = full scan.

## Conventions

- Bare paths (e.g. `references/methodology.md`) resolve from the skill root.
- `{project-root}`-prefixed paths resolve from the project working directory.

## On Activation

Load available config from `{project-root}/_bmad/config.yaml` and `{project-root}/_bmad/config.user.yaml` (root level and `tm` section). If config is missing, let the user know `tm-setup` can configure the module at any time. Use sensible defaults for anything not configured.

Read `{project-root}/_bmad/memory/tm/wiki/index.md` to check for existing regime playbooks. If regime wiki pages exist (e.g., `wiki/regimes/vix-spike.md`), load the relevant ones based on current conditions — this gives the assessment historical context from prior episodes.

Route by args:
- No args or `full` → run **Full Regime Scan** (below)
- `distribution-days` → run distribution day count only
- `safety-car` → run safety car check only
- `r0` → run R0 propagation only
- `breadth` → run breadth analysis only
- `snapshot` → run full scan + write regime snapshot

## Full Regime Scan

Load `references/methodology.md` for the detailed three-layer assessment process.

Gather data from all layers in parallel where possible, then synthesize into a composite regime state object:

```yaml
regime:
  macro: bull | bear | sideways
  macro_confidence: 0.0-1.0
  sectors:
    leading: [list]
    lagging: [list]
    rotating_into: [list]
    rotating_out: [list]
  flag: green | yellow | red | black
  safety_car: true | false
  distribution_days: {count}
  r0_leading_sectors: {sector: r0_value}
  breadth_score: 0.0-1.0
  vix: {current}
  yield_curve_spread: {10Y-2Y}
  portfolio_implications:
    max_position_size: "full | reduced | halted"
    new_entries: "allowed | confirm-only | halted"
    recommended_cash: "20% | 40% | 60%"
  timestamp: ISO-8601
```

Present the regime state clearly with the flag color prominent. Explain any conflicts between layers. Reference wiki regime playbooks if the current regime matches a documented pattern.

If the user asked for a snapshot, also write to `{project-root}/_bmad/memory/tm/raw/regime-snapshots/` and update the quant layer:

```
python3 scripts/record_regime.py {project-root}/_bmad/memory/tm/tm-signals.db --regime {state_json}
```

End with portfolio implications — what this regime means for position sizing, new entries, and cash reserves per the configured rules.

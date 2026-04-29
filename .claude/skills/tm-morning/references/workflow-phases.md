# Morning Workflow — Phase Details

Detailed instructions for each pipeline phase. The orchestrator loads this on activation and follows each phase sequentially.

## Phase 1: Regime Scan

**Goal:** Produce today's regime snapshot with flag color, leading sectors, and portfolio implications.

**Execution:** Spawn a single subagent with the following prompt structure:

```
You are running a regime assessment for The Money trading system.

Read the methodology file at:
  {project-root}/.claude/skills/tm-regime/references/methodology.md

Then gather data using these MCP tools:
1. mcp__financekit__market_overview — major indices, VIX
2. mcp__financekit__sector_rotation — sector RS rankings
3. mcp__financekit__technical_analysis for SPY, QQQ, DIA — RSI, moving averages
4. mcp__fred__fred_series for DGS10, DGS2 — yield curve spread

Synthesize into the three-layer regime model (macro, sector, stock-level).
Determine the flag: green/yellow/red/black.

Write the regime snapshot as markdown with YAML frontmatter to:
  {project-root}/_bmad/memory/tm/wiki/regimes/{today}-regime.md

Use the exact YAML schema from the methodology file.

End your response with a JSON summary block:
{
  "flag": "yellow",
  "leading_sectors": ["Technology", "Consumer Discretionary"],
  "lagging_sectors": ["Energy", "Healthcare"],
  "rotating_into": ["Financials"],
  "vix": 18.5,
  "portfolio_implications": {
    "new_entries": "confirm-only",
    "max_risk_per_trade": 300
  }
}
```

**After subagent returns:** Read the regime file it wrote. Extract the flag and leading sectors. Print a one-line regime summary to the user.

**Time budget:** ~60 seconds.

## Phase 2: Pre-Market Scan

**Goal:** Produce today's watchlist — candidates grouped by strategy.

**Execution:** Run the Python scanner directly via Bash:

```bash
python {project-root}/scripts/premarket_scanner.py --top 5
```

The scanner reads the current regime from wiki automatically. It outputs JSON to both stdout and `raw/watchlists/YYYY-MM-DD.json`.

**After scanner returns:** Read the output JSON. Print a summary table:

```
WATCHLIST — {date}
Strategy  | Candidates | Top Pick
----------|------------|----------
TCEP      | 3          | NVDA (score 0.85)
ORB       | 5          | AMD (score 0.72)
MRF       | 2          | KO (score 0.68)
...
Total: 12 candidates across 4 strategies
```

**Deferred checks:** The scanner flags items that need MCP verification:
- Earnings dates for EDVP/ERP candidates
- IV Rank for EDVP candidates
- Pre-market gap data for ORB/ERP candidates (at market open)
- Options liquidity for all candidates

These checks happen in Phase 3 (signal evaluation subagents have MCP access).

**Time budget:** ~30-90 seconds depending on universe size.

## Phase 2.5: Qualitative Screen (Desk Agent Integration)

**Goal:** Run Trading Desk agents (Nadia, Tara, Frank, optionally Sage) on all candidates to catch catalysts, chart weaknesses, fundamental risks, and crowding that the quant layer is blind to.

**Full specification:** Load `references/qualitative-screen.md` for detailed prompt templates, output schemas, and composite scoring logic.

**Execution summary:**

**Step A — Prefetch data** (Bash, ~10s):
```bash
today=$(date +%Y-%m-%d)
mkdir -p {project-root}/_bmad/memory/tm/raw/prefetched/$today
# Extract unique tickers from watchlist, prefetch in parallel
for ticker in $(python -c "
import json
with open('{project-root}/_bmad/memory/tm/raw/watchlists/$today.json') as f:
    data = json.load(f)
tickers = set()
for candidates in data['candidates'].values():
    for c in candidates:
        tickers.add(c['ticker'])
print(' '.join(sorted(tickers)))
"); do
  python {project-root}/scripts/fetch_data.py $ticker \
    > {project-root}/_bmad/memory/tm/raw/prefetched/$today/$ticker.json 2>/dev/null &
done
wait
```

**Step B — Dispatch desk agents** (3-4 parallel subagents, ~60-90s):
Spawn Nadia, Tara, Frank in parallel. Each reads its own SKILL.md + references/ for persona/methodology, reads ALL prefetched ticker JSONs, and writes structured qualitative scores to `raw/qualitative/{today}/{agent}.json`. Sage is spawned only if any candidate appears in the high-buzz ticker list.

Each subagent uses **pipeline subagent mode** — no greetings, JSON-only output, reads from prefetched data instead of making redundant MCP calls.

**Step C — Composite scoring** (main context, ~5s):
Read all agent JSON results. For each ticker:
- Worst flag wins (any red → composite red, any yellow → composite yellow)
- Any `blocks=true` → trade is blocked
- Write `raw/qualitative/{today}/composite.json`

**After composite:** Print a qualitative summary table:
```
QUALITATIVE SCREEN — {date}
Ticker | Nadia     | Tara      | Frank     | Sage  | Composite
-------|-----------|-----------|-----------|-------|----------
NVDA   | green     | green     | yellow    | —     | yellow (reduce sizing)
AMD    | green     | green     | green     | —     | green
CSCO   | red(block)| yellow    | green     | —     | RED (blocked — negative catalyst)
```

**Time budget:** ~90 seconds total.

## Phase 3: Signal Evaluation

**Goal:** Run the full signal evaluation checklist on each candidate. Produce GO/NO-GO per candidate.

**Execution:** Spawn **one subagent per strategy** that has candidates. Run them in parallel. Each subagent evaluates all candidates for its strategy.

Subagent prompt template:

```
You are evaluating {STRATEGY} candidates for The Money trading system.

REGIME STATE:
  Flag: {flag}
  Leading sectors: {sectors}

Read the strategy rules at:
  {project-root}/_bmad/memory/tm/wiki/strategies/{strategy_file}.md

Read the signal evaluation protocol at:
  {project-root}/_bmad/memory/tm/wiki/signal-evaluation.md

CANDIDATES TO EVALUATE:
{candidate_list_from_watchlist}

For each candidate:
1. Check portfolio heat via mcp__alpaca__get_all_positions and mcp__alpaca__get_account_info
2. Run the strategy-specific checklist gates using MCP tools:
   - mcp__financekit__technical_analysis for technicals
   - mcp__yahoo-finance__get_stock_info for earnings dates, fundamentals
   - mcp__yahoo-finance__get_option_chain for IV, liquidity (if options strategy)
   - mcp__financekit__price_history for volume patterns
3. Calculate sizing per exploration-mode rules
4. Produce GO/NO-GO decision

Write each evaluation result as JSON to:
  {project-root}/_bmad/memory/tm/raw/evaluations/{today}/{TICKER}.json

Schema:
{
  "ticker": "NVDA",
  "strategy": "TCEP",
  "decision": "GO",
  "gates_passed": 9,
  "gates_total": 9,
  "failed_gates": [],
  "sizing": {
    "risk": 300,
    "structure": "equity",
    "entry": 850.00,
    "stop": 835.00,
    "target": 880.00,
    "shares": 20,
    "rr": 2.0
  },
  "notes": "All gates passed. EMA touch confirmed intraday.",
  "timestamp": "2026-04-27T09:35:00"
}

For NO-GO:
{
  "ticker": "AAPL",
  "strategy": "TCEP",
  "decision": "NO-GO",
  "gates_passed": 7,
  "gates_total": 9,
  "failed_gates": ["Gate 7: EMA not touched", "Gate 9: R/R 1.5 < 2.0"],
  "what_would_change_it": "Wait for price to touch 21 EMA at $187.50",
  "notes": "Approaching EMA but not there yet.",
  "timestamp": "2026-04-27T09:35:00"
}

End with a summary: how many GO vs NO-GO for this strategy.
```

**After all subagents return:** Read the evaluation JSON files. Collect all GO decisions.

**Time budget:** ~2-3 minutes (parallel subagents).

## Phase 4: Prioritize

**Goal:** Rank GO signals for immediate deployment AND write trigger YAML files for all conditional setups. Every session produces trades — either immediate or watchlist.

**Philosophy:** No "stand aside" days. Every candidate that survived qualitative screening either trades now (GO) or gets a conditional trigger rule that the daemon monitors during market hours.

**Execution:** This runs in the main context (lightweight — just reading JSON files).

1. Read all evaluation JSONs from `raw/evaluations/{today}/`
2. Separate into three buckets:
   - **GO now** — decision=GO, execute immediately in Phase 5
   - **DEFERRED** — decision=DEFERRED, needs live confirmation at open (write trigger file)
   - **NO-GO with trigger** — decision=NO-GO but the failure was a timing/live-data gate (e.g., gap not yet confirmed, EMA not yet touched) — write trigger file
   - **Hard NO-GO** — failed a non-live gate (wrong strategy window, blocked qualitative) — note only, no trigger
3. Rank GO signals by R/R, diversification, heat
4. Write trigger YAML files for all DEFERRED + conditional NO-GO signals

**Output: Trigger YAML files**

For each DEFERRED or conditional NO-GO, write `raw/triggers/{today}/{TICKER}.yaml`:

```yaml
ticker: AAPL
strategy: ERP
thesis: "Earnings today pre-market. Watch for gap continuation via VWAP pullback."
created_at: "2026-04-30T09:15:00"
expires_at: "2026-04-30T11:00:00"
qualitative_flag: yellow

conditions:
  - metric: gap_pct
    op: ">="
    value: 3.0
  - metric: volume_ratio
    op: ">="
    value: 2.0
  - metric: price_above_vwap
    value: true
  - metric: time_in_window
    start: "09:30"
    end: "11:00"

trade:
  direction: long
  entry_type: market
  stop_pct: 3.0
  target_rr: 2.0
  max_risk: 150
  structure: equity

fired: false
fired_at: null
```

**Condition mapping by failure type:**

| Failure reason | Trigger condition to add |
|----------------|--------------------------|
| ORB: gap not confirmed | `gap_pct >= 1.0` + `or_breakout_long == true` |
| ERP: earnings not yet reported | `gap_pct >= 3.0` + `volume_ratio >= 2.0` + `price_above_vwap == true` |
| TCEP: EMA not touched yet | `price_vs_ema21` within 0.5% (i.e., `>= -0.5` AND `<= 0.5`) |
| MRF: RSI not extreme yet | `rsi_14 <= 20` (long) or `rsi_14 >= 80` (short) |
| SMR: rotation not confirmed | `price_vs_ema21 >= 0` + `volume_ratio >= 1.5` |

**Present the session plan:**

```
SESSION PLAN — {date}

DEPLOY NOW ({N} trades):
  Rank | Ticker | Strategy | R/R  | Risk  | Entry  | Stop   | Target
  ...

WATCHLIST — daemon monitors these ({M} tickers):
  Ticker | Strategy | Trigger condition             | Expires
  -------|----------|------------------------------|--------
  AAPL   | ERP      | gap ≥3% + vol ≥2x + > VWAP  | 11:00 AM
  QCOM   | ERP      | gap ≥3% + vol ≥2x + > VWAP  | 11:00 AM
  PANW   | ORB      | gap ≥1% + OR breakout         | 11:00 AM

BLOCKED ({K} tickers — no trigger written):
  CSCO: qualitative red (Nadia)
  ANET: insider selling block
  AMD:  parabolic ATH, downgrade
```

**Decision point:** Based on autonomy setting:
- **A:** Deploy GO signals, start daemon (or confirm daemon is running)
- **B:** Ask "Approve deployment? [all / select / skip]", then start daemon
- **C:** Present plan only, user deploys manually and starts daemon manually

## Phase 5: Deploy

**Goal:** Execute approved trades via Alpaca.

**Execution:** For each approved trade, spawn a subagent:

```
Execute a trade on Alpaca paper account for The Money trading system.

TRADE:
  Ticker: {ticker}
  Strategy: {strategy}
  Direction: {long/short}
  Structure: {equity/options}
  Entry: market order at open / limit at {price}
  Shares/Contracts: {qty}
  Stop: {stop_price} — set as stop-loss order immediately after entry
  Target: {target_price} — set as limit sell order

EXECUTION STEPS:
1. Check mcp__alpaca__get_clock — is market open?
   - If pre-market: place entry as limit order for market open
   - If market open: place entry as market order
2. Place the entry order via mcp__alpaca__place_stock_order
3. After fill confirmation: place bracket orders (stop + target)
4. Log the trade to: {project-root}/_bmad/memory/tm/raw/trade-logs/{today}-{ticker}.json

IMPORTANT:
- This is a PAPER account. alpaca_mode = paper.
- If the order is rejected, report the rejection reason. Do not retry.
- If market is closed, place as a queued order for next open.
```

**After deployment subagents return:** Report execution results.

**Time budget:** ~30 seconds per trade.

## Phase 6: Summary

**Goal:** Recap the morning session in 5-10 lines.

**Execution:** In main context:

```
MORNING SESSION — {date} {time}

Regime: {flag} ({one-line description})
Scanned: {N} stocks → {M} candidates
Evaluated: {M} candidates → {K} GO signals
Deployed: {J} trades

Trades entered:
  {ticker} — {strategy} — {direction} @ ${entry}, stop ${stop}, target ${target}

Watching:
  {NO-GO tickers approaching triggers}

Next: Run /tm-deploy manage to check positions at 11 AM ET.
```

Write this summary to `{project-root}/_bmad/memory/tm/wiki/log.md` (append).

## Timing Guide

| Phase | Duration | Method |
|-------|----------|--------|
| 1. Regime | ~60s | 1 subagent |
| 2. Scan | ~60s | Python script |
| 3. Evaluate | ~120s | 3-5 parallel subagents |
| 4. Prioritize | ~10s | Main context reads files |
| 5. Deploy | ~30s/trade | 1 subagent per trade |
| 6. Summary | ~10s | Main context |
| **Total** | **~5-6 min** | |

The pipeline should complete well within the 9:30-11:00 AM window, leaving time for manual review and position management.

## Re-entry and Partial Runs

If the pipeline is interrupted or you want to re-run a phase:

- `/tm-morning scan` — re-runs from Phase 2 using existing regime
- `/tm-morning evaluate` — re-runs from Phase 3 using existing watchlist
- `/tm-morning deploy` — re-runs from Phase 5 using existing evaluations

Each re-entry reads the appropriate artifact files from today's date.

## Context Management Checklist

The orchestrator should verify these context hygiene practices:

- [ ] Never load full strategy `.md` files in main context (subagents do this)
- [ ] Never carry raw MCP tool output in main context (subagents summarize to JSON)
- [ ] Read only JSON summary fields from artifact files, not entire files
- [ ] Print concise 1-2 line updates between phases, not full phase reports
- [ ] If main context feels heavy: the watchlist JSON and evaluation JSONs contain everything needed — don't re-derive

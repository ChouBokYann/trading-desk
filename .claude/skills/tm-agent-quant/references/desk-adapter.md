# Desk → Signal Evaluation Adapter

Maps Trading Desk analyst output to Signal Evaluation checklist gates.

## When to Use

When a trade candidate arrives from the desk (via `/alpha`, `/analyze`, or individual analyst runs), extract gate-relevant data from each analyst's output and feed it into the Signal Evaluation protocol.

## Analyst → Gate Mapping

### Marco (Macro)
- **Gate 1 — Regime alignment:** Use Marco's macro regime assessment. Cross-reference with latest `wiki/regimes/` snapshot. Green or Yellow required for entry.
- **Gate 2 — Sector leadership:** Use Marco's sector rankings. Candidate's sector must be in current leaders.

### Tara (Technical)
- **Gate 3 — Trend intact:** Price above 50-day AND 200-day MA from Tara's moving average analysis.
- **Gate 5 (TCEP) — RS rank:** Tara's relative strength analysis. Must be top 30% vs SPY over 1 month.
- **Gate 6 (TCEP) — Pullback volume:** Tara's volume analysis. Last 2 pullback days must be below 20-day average volume.
- **Gate 7 (TCEP) — EMA touch:** Tara's 21 EMA proximity check. Must touch intraday.
- **Gate 7/9 — R/R:** Calculated from Tara's support/resistance levels (entry, stop, target).

### Nadia (News)
- **Gate 4 (EDVP) — Earnings window:** Nadia's earnings calendar data. Must be 14–21 days out.
- **Gate 4 (TCEP) — Earnings clearance:** Nadia's earnings data. Must be > 14 days away.
- **Catalyst context:** Nadia's news analysis informs whether a signal is chase-entry vs legitimate catalyst.

### Frank (Fundamentals)
- **Not a direct gate.** Frank's output supports conviction tier assignment:
  - Strong margins + cash flow + balance sheet → Tier 1 sizing confidence
  - Mixed signals → Tier 2
  - Weak fundamentals → flag for Quant to reconsider, even if checklist passes

## MCP Supplements

Not all gates are covered by analyst prose. These require direct MCP calls during evaluation:

| Gate | MCP Tool | What to Pull |
|------|----------|--------------|
| IV Rank (EDVP Gate 5) | `financekit__technical_analysis` | IV percentile |
| Options liquidity (EDVP Gate 6) | `yahoo-finance__get_option_chain` | ATM bid/ask spread |
| Portfolio heat (Step 1) | `alpaca__get_all_positions` + `alpaca__get_account_info` | Open risk, buying power |
| Entry window (TCEP Gate 8) | `alpaca__get_clock` | Market time |

## Workflow

```
1. Candidate arrives (ticker + thesis)
2. Spawn 4 desk analysts in parallel (haiku):
   - Marco: /macro {TICKER}
   - Tara:  /chart {TICKER}
   - Nadia: /news {TICKER}
   - Frank: /valuation {TICKER}
3. Strategy identification:
   - Earnings in 14–21 days? → EDVP
   - No earnings + pullback to 21 EMA? → TCEP
   - Neither? → stand aside
4. Extract gate data from analyst output + MCP supplements
5. Run Signal Evaluation checklist (wiki/signal-evaluation.md)
6. If GO → tm-deploy:deploy {TICKER}
```

## Analyst Output → Signal Object

The Signal Evaluation protocol expects a signal object. Construct it from desk output:

```
ticker:      from candidate
direction:   long (both EDVP and TCEP are long-only)
thesis:      synthesized from Nadia (catalyst) + Tara (setup) + Frank (quality)
entry price: from Tara's technical levels (breakout point or EMA bounce)
stop price:  from Tara's support levels (below key MA or prior swing low)
targets:     from Tara's resistance levels (prior high, measured move)
```

## When Full /analyze Is Overkill

For daily signal evaluation, the 4-analyst solo run (Marco/Tara/Nadia/Frank) is sufficient. Reserve the full 13-agent `/analyze` pipeline for:
- High-conviction candidates that need adversarial debate
- Candidates where you're unsure and want the bull/bear stress test
- End-of-week deep dives on watchlist names

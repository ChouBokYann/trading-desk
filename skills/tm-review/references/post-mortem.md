# Post-Mortem & Causal Attribution

## Gather Evidence

Reconstruct the full trade lifecycle from available sources:

1. **Trade log** -- Read the entry record from `{project-root}/_bmad/memory/tm/raw/trade-logs/{date}-{ticker}-entry.md`. This has the original signal, checklist results, sizing, and execution details.

2. **Price action during hold** -- Fetch historical data for the trade period via `yahoo-finance:get_historical_stock_prices`. Note key moves, gaps, volume spikes.

3. **Exit details** -- How did the trade close? Stop hit, target reached, manual exit, thesis break, decay timeout? Pull from Alpaca trade history via `alpaca:get_account_activities`.

4. **Concurrent events** -- Search for news and events around the trade period via `opennews:search_news` for the ticker and related terms. Also check `yahoo-finance:get_yahoo_finance_news`.

5. **Regime context** -- What was the regime at entry vs. exit? Check `{project-root}/_bmad/memory/tm/raw/regime-snapshots/` for snapshots during the hold period.

## Compute Outcome Metrics

- **R-multiple**: (exit - entry) / (entry - stop) for longs, inverted for shorts
- **Hold time**: trading days from entry to exit
- **Max favorable excursion (MFE)**: highest unrealized gain during hold
- **Max adverse excursion (MAE)**: deepest unrealized loss during hold
- **Efficiency**: actual gain / MFE -- how much of the available move was captured

## Causal Attribution

The PRIMARY goal. Use the 6-category taxonomy to tag dominant factors:

| Category | Examples |
|----------|----------|
| **Macro policy** | Fed rate decision, tariff announcement, fiscal policy change |
| **Earnings/fundamentals** | Earnings beat/miss, guidance revision, revenue surprise |
| **Market structure** | OpEx pinning, short squeeze, meme momentum, liquidity event |
| **Sector rotation** | Capital flow shift, relative strength regime change |
| **Geopolitical** | Conflict escalation, sanctions, trade war development |
| **Technical breakdown** | Support failure, trend break, volume climax, failed breakout |

**Attribution process:**

1. Identify what ACTUALLY moved the stock during the hold period -- not what you expected to move it
2. Tag 1-3 dominant causal factors from the taxonomy
3. For each factor, provide the evidence chain: what happened, when, and how it affected the position
4. Note any factors that were present at entry but didn't materialize (expected catalyst that fizzled, risk factor that didn't trigger)
5. Rate attribution confidence: high (clear single cause), medium (multiple plausible causes), low (unclear/random)

## Contact Tracing

Triggers automatically on losses >= 2% of portfolio. Can also be invoked manually.

**Purpose:** After a significant loss, map the causal factors across all open positions to identify contagion risk -- other positions that share the same vulnerability.

**Process:**

1. Take the causal factor tags from the losing trade
2. For each open position, check: does this position share exposure to the same causal factors?
3. Score contagion risk: **high** (same factor, same direction), **medium** (related factor or same sector), **low** (tangential)
4. Present the contagion map with recommended actions for high-risk positions

**Output:** A risk contagion table:

```
| Position | Shared Factor         | Contagion Risk | Recommended Action     |
|----------|-----------------------|----------------|------------------------|
| MSFT     | Tariff policy (same)  | HIGH           | Tighten stop, review   |
| AMZN     | Tech sector (related) | MEDIUM         | Monitor, no action yet |
| XOM      | None identified       | LOW            | No action              |
```

# Signal Intake

Normalize any trade signal into the standard schema consumed by the pre-trade checklist and execution pipeline.

## Signal Sources

### Desk `/analyze` Output

The analyze pipeline produces a structured recommendation. Look for the signal block at the end of the analysis -- it contains ticker, direction, conviction, thesis, levels, and risk factors.

### Alpha Chain File

Mr. A's `/alpha` writes `alpha-chain-{TICKER}.md` to the project root. Read it and extract: the top pick ticker, direction, thesis summary, and suggested entry/stop/targets from the chain's debate output.

### Manual Input

The user provides ticker and direction at minimum. Gather remaining fields conversationally:

- Entry price (or "market")
- Stop loss level
- Profit targets (1-3 levels)
- Thesis (one sentence minimum)
- Known risk factors

## Standard Signal Schema

```json
{
  "ticker": "AAPL",
  "direction": "long",
  "conviction": 0.82,
  "thesis": "7-week base breakout with RS >90, institutional accumulation",
  "entry": 195.50,
  "stop": 187.20,
  "targets": [210.00, 225.00],
  "risk_factors": ["earnings in 12 days", "sector rotation mixed"],
  "catalyst_timeline": "product launch 2026-05-15",
  "source": "analyze-pipeline | alpha-chain | manual",
  "timestamp": "ISO-8601"
}
```

## Validation

Before proceeding to the checklist, verify:

- Ticker is a valid, tradeable symbol (check via `alpaca:get_asset`)
- Direction is `long` or `short`
- Entry and stop are on the correct side (stop below entry for long, above for short)
- Risk-reward from entry to first target vs. entry to stop is calculable
- No duplicate -- check `tm-signals.db` for an active signal on the same ticker

If validation fails, report the issue and ask the user to correct it.

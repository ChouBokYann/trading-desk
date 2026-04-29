# Pre-Trade Checklist

Seven gates. ALL must pass before any capital moves. A failed gate is a hard stop.

## Gate 1: Regime Alignment

**Source:** Current regime state (loaded on activation or from `tm-regime`)

| Regime Flag | Rule |
|-------------|------|
| Green | All directions allowed, full sizing |
| Yellow | Long only if conviction tier 1, reduced sizing (50%) |
| Red | No new entries. Hard stop. |
| Black (Safety Car) | No new entries. Force portfolio review first. |

**Pass criteria:** Regime flag allows the signal's direction and conviction tier.

## Gate 2: IV Percentile

**Source:** `financekit:technical_analysis` or `yahoo-finance:get_stock_info` for IV data

| IV Percentile | Rule |
|---------------|------|
| >80th | Sell premium strategies only (credit spreads, iron condors). No long options. |
| <20th | Buy options strategies allowed (debit spreads). No premium selling. |
| 20-80th | Equity only. No options overlay on this entry. |

**Pass criteria:** The signal's intended instrument type aligns with the IV regime.

## Gate 3: Portfolio Heat

**Source:** Run `python3 scripts/portfolio_heat.py` with current positions from Alpaca

Calculate current portfolio heat (total % of portfolio at risk across all open positions). Compare against the configured limit (default 8% in bull, 4% in bear).

**Pass criteria:** Adding this signal's risk doesn't breach the heat limit.

## Gate 4: Correlation Check

**Source:** `financekit:correlation_matrix` or `financekit:compare_assets` for the signal ticker vs. all open position tickers

Check sector overlap and price correlation between the signal ticker and every open position.

**Pass criteria:** No existing position has >0.8 correlation with the signal ticker. Adding the position doesn't push any single sector above 30% of portfolio.

## Gate 5: Earnings Date Clearance

**Source:** `financekit:earnings_calendar` or `yahoo-finance:get_stock_info`

Check for upcoming earnings within the signal's expected hold period.

**Pass criteria:** No earnings announcement within 5 trading days of entry, unless the thesis explicitly incorporates the earnings event.

## Gate 6: Calendar Position

**Source:** Market calendar awareness

Check for calendar risks:

- Options expiration week (OpEx pinning risk)
- FOMC meeting within 3 days
- Quarter-end rebalancing window
- Holiday-shortened weeks (low liquidity)

**Pass criteria:** No calendar event that materially conflicts with the signal's thesis and timing.

## Gate 7: Risk-Reward (Pot Odds)

**Source:** Signal's entry, stop, and target levels

Calculate R:R ratio: `(first target - entry) / (entry - stop)` for longs (inverse for shorts).

**Pass criteria:** R:R >= 2:1. If multiple targets, the probability-weighted expected R must exceed 2:1.

## Checklist Report

Present results as a clear table:

```
| Gate                | Status  | Data                                                   |
|---------------------|---------|--------------------------------------------------------|
| Regime Alignment    | PASS    | Green flag, all directions allowed                     |
| IV Percentile       | PASS    | IV rank 45th -- equity zone                            |
| Portfolio Heat      | PASS    | Current 4.2%, adding 1.8% -> 6.0% (limit 8%)          |
| Correlation         | PASS    | 0.65 with MSFT (watch)                                 |
| Earnings            | PASS    | Next earnings 2026-06-15 (51 days)                     |
| Calendar            | PASS    | No conflicts this week                                 |
| Risk-Reward         | PASS    | R:R 2.8:1 ($8.30 risk / $23.50 reward)                |

Result: GO / NO-GO
```

If any gate shows FAIL, the result is NO-GO regardless of other gates. Show the failure prominently with what would need to change for it to pass.

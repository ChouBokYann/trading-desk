# Execution Pipeline

From checklist clearance to money moving. Three steps: size, construct, execute.

## Position Sizing

Run the sizing script with the signal and portfolio data:

```
python3 scripts/position_sizing.py \
  --account-value {account_equity} \
  --entry {entry_price} \
  --stop {stop_price} \
  --conviction {tier: 1|2|3} \
  --regime {flag: green|yellow} \
  --spread-pct {bid_ask_spread_pct} \
  --vix {current_vix}
```

The script implements half-Kelly base x conviction tier x liquidity multiplier x regime adjustment. See `scripts/position_sizing.py --help` for full interface details.

| Conviction Tier | Risk Per Trade |
|-----------------|---------------|
| Tier 1 (all signals aligned) | 2% of portfolio |
| Tier 2 (mixed signals) | 1% of portfolio |
| Tier 3 (speculative) | 0.25% of portfolio |

The script outputs shares/contracts, dollar risk, percentage of portfolio, and the full sizing breakdown showing each multiplier's effect.

If the position size seems wrong (e.g., <1 share, >10% of portfolio), flag it and ask for confirmation before proceeding.

## Correlation Double-Check

Before constructing the order, run a final correlation check with the sized position. If adding this position at the computed size would push portfolio-level sector concentration above 30%, reduce the size to fit.

## Order Construction

Build a bracket order based on the signal type:

**Equity (long):**
- Entry: limit order at signal entry price (or market if specified)
- Stop loss: stop order at signal stop price
- Take profit: limit sell at first target (or OCO with multiple targets)

**Options (if IV gate indicated options overlay):**
- Entry: debit/credit spread based on IV regime
- Stop: time-based or delta-based, per strategy rules from wiki
- Target: 50% of max profit for credit, 100% of debit for debit spreads

Present the complete order before execution:

```
ORDER SUMMARY
Ticker:     AAPL
Direction:  LONG
Shares:     45
Entry:      $195.50 (limit)
Stop:       $187.20 (-$8.30/share, -$373.50 total)
Target 1:   $210.00 (+$14.50/share, +$652.50)
Target 2:   $225.00 (+$29.50/share, +$1,327.50)
Risk:       $373.50 (1.87% of portfolio)
R:R:        2.8:1 (to T1)
```

## Execution by Autonomy Tier

| Tier | Condition | Action |
|------|-----------|--------|
| A (full-auto) | All signals aligned, conviction tier 1, regime green | Execute immediately via `alpaca:place_stock_order` |
| B (confirm) | Mixed signals or tier 2 conviction | Queue with 30-minute veto window. Execute if no veto. |
| C (human) | Speculative, regime yellow, or configured default | Present order and wait for explicit user confirmation |

For Tier B: write the pending order to the confirmation queue and notify the user. If 30 minutes pass without a veto, execute.

## Trade Record

After execution (or rejection), write:

1. **Trade log** to `{project-root}/_bmad/memory/tm/raw/trade-logs/{date}-{ticker}-entry.md` -- full signal, checklist results, sizing, order details, and execution confirmation.

2. **Quant layer** -- insert into `tm-signals.db` trades table with: ticker, direction, entry_price, stop_price, targets, shares, risk_dollars, risk_pct, conviction_tier, regime_flag, signal_source, entry_date, status.

3. **Wiki log** -- append to `{project-root}/_bmad/memory/tm/wiki/log.md`:
   ```
   [{date}] DEPLOY: {ticker} {direction} -- {shares} shares @ ${entry}. Risk: ${risk} ({risk_pct}%). Source: {source}. Regime: {flag}.
   ```

## Priority Queue

When multiple signals are pending and portfolio heat doesn't allow all of them:

Score each signal: `priority = conviction x (1 / correlation_with_portfolio) x regime_alignment_score`

Present the ranked list with scores and deploy the top pick. Remaining signals go to the watchlist with their clearance status -- which gates they've passed and what they're waiting on.

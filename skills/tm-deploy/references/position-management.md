# Position Management

Active management of open positions -- trailing stops, pyramids, partial exits, and decay review.

## Trailing Stop Management

For each open position, evaluate whether the stop should be adjusted:

**Rules:**
- Move stop to breakeven after position reaches 1R profit
- Trail using 2x ATR(14) below the highest close since entry
- Never move a stop further from entry (stops only tighten)
- Log every stop adjustment with rationale

**Data sources:**
- Current price and ATR: `yahoo-finance:get_stock_info` or `financekit:technical_analysis`
- Entry data and current stop: `tm-signals.db` or `{project-root}/_bmad/memory/tm/raw/trade-logs/`

**Action:** If the calculated trailing stop is above the current stop, update via `alpaca:replace_order_by_id`. Record the adjustment in the trade log and wiki log.

## Pyramid Entry

Add to a winning position when the thesis is confirmed by a pullback.

**Protocol (every condition must hold):**
1. First tranche is profitable (current price > entry for longs)
2. Price has pulled back to the 10-day moving average
3. Price has bounced off the 10-day MA (confirmed by a higher close)
4. Current regime is still green or yellow
5. Portfolio heat after the add still under the limit

**Sizing:** Second tranche = 50% of original position size. Never add more than once. Never add to a losing position.

**Execution:** Treat the pyramid as a fresh deploy through the pre-trade checklist, but with the pyramid conditions as additional gates. The signal source is `pyramid-{original_trade_id}`.

## Partial Exit

Scale out at profit targets or when the thesis weakens:

**Target-based exits:**
- At target 1: sell 50% of position
- At target 2: sell remaining (or trail tight)
- Adjust stop on remaining shares to breakeven minimum

**Thesis-based exits:**
- If the original thesis signal weakens but hasn't broken (sector rotation turning, momentum fading): reduce by 50%
- If the thesis breaks entirely (catalyst failed, fundamental change): exit 100% regardless of P&L

**Execution:** Use `alpaca:place_stock_order` for the partial sell. Update the position record in `tm-signals.db` and trade logs.

## Position Decay Review

Flag positions that have exceeded their freshness window.

**Default freshness window:** 10-15 trading days from entry (configurable).

**Process:**
1. Query all open positions from `tm-signals.db` with entry dates
2. Calculate trading days since entry (exclude weekends and market holidays)
3. Flag any position past the freshness window

**For each flagged position, evaluate:**
- Is the original thesis still intact? Check current price action, news, and catalyst status.
- Has the stop been hit or is the position profitable?
- Does the current regime still support the position?

**Output:** A list of stale positions with their current status and a recommendation: **hold** (thesis intact, extend window), **reduce** (thesis weakening), or **exit** (thesis broken or no longer actionable).

The user decides -- decay flags positions for review, it doesn't auto-close them. Present the evidence and let the trader call it.

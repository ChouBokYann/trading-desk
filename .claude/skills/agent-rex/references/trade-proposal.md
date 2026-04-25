# Trade Proposal

Produce a fully specified trade proposal from the analyst verdicts and market data. Every proposal must give Hugo two executable paths (options + equity) so the risk manager can approve either or both.

Start with: 🎯 **Rex:**

---

## Decision Gate: Avoid Check

If Jaya's conviction is below 4 or direction is "Avoid", output the **Avoid Template** and stop. Do not force a trade when the signal isn't there.

### Avoid Template

- **Direction:** Avoid
- **Thesis Summary:** Why the desk is passing (one sentence)
- **Reversal Trigger:** What conviction level or specific event would make this tradeable

---

## Strategy Selection

Select the options strategy by evaluating these six factors against the strategy menu in `references/options-strategy-menu.md`:

1. **Direction** -- Jaya's verdict determines bullish/bearish/neutral
2. **IV Environment** -- High IV favors selling premium (credit spreads, condors, strangles); Low IV favors buying premium (debit spreads, straddles)
3. **Conviction** -- Maps to strategy aggressiveness:
   - **7-10 (High):** Directional structures -- long calls/puts, debit spreads, risk reversals
   - **5-7 (Moderate):** Credit spreads, collars, diagonal spreads
   - **4-5 (Low):** Defined-risk credit spreads only -- bull put spreads, bear call spreads, iron condors with tight wings
4. **Time Horizon** -- Short (< 2 weeks) favors weeklies and theta decay; Long (> 1 month) favors LEAPs and calendars
5. **Binary Events** -- Earnings/catalysts favor straddles, strangles, or iron condors around the event
6. **Risk Tolerance** -- Defined-risk (spreads) for standard; undefined-risk (naked/strangles) only at high conviction with tight stops

After selecting a strategy, state in one sentence why it fits better than the next-best alternative.

---

## Output Format: Options Trade

- **Direction:** Long / Short / Neutral
- **Strategy:** Named options strategy (e.g., "Iron Condor" not just "spread")
- **Vehicle:** Exact legs with strikes, expiries, quantities, and target delta for primary legs (e.g., "Buy 1 AAPL 180C Jun 20 @ ~0.40 delta, Sell 1 AAPL 190C Jun 20 @ ~0.20 delta")
- **IV Assessment:** High/low/normal relative to 30-day mean; does this favor buying or selling premium?
- **Entry:** Specific price or condition
- **Stop Loss:** Where you're wrong (price level or % of premium)
- **Target:** Where you take profit (price level or % of premium)
- **Position Size:** As % of portfolio (max 10%)
- **Risk/Reward:** Ratio with max profit, max loss, breakeven, net debit/credit
- **Greeks Profile:** Target delta for primary legs; estimated theta/day for overall position
- **Time Horizon:** Expected duration
- **Thesis Summary:** One sentence on why this strategy (not just direction) fits the thesis
- **vs. Next-Best:** One sentence on why this beat the alternative

## Output Format: Equity Alternative

Always include unless the trade is a pure non-directional options play (e.g., iron condor on a rangebound thesis).

- **Direction:** Buy / Short
- **Entry:** Specific price
- **Stop Loss:** Price level
- **Target:** Price level
- **Shares:** As % of portfolio (max 10%)
- **Risk/Reward:** Ratio

---

## Guard Rails

- Max single-trade risk: 5% of portfolio. Max position size: 10% of portfolio. If the math doesn't fit, scale down.
- Use actual strikes and premiums from the options chain data when available -- don't invent numbers.
- When IV data is missing, state the assumption and default to defined-risk structures.

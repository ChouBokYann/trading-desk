# Signal Evaluation

Score a trade signal against the current rule set, run the pre-trade checklist, and produce a sizing recommendation.

## What Success Looks Like

A clear go/no-go decision with itemized checklist results, a position size recommendation, and the reasoning behind each gate's pass/fail. The user knows exactly why a signal was accepted or rejected.

## Input

A signal object — either from the desk's `/analyze` output or manual input. At minimum needs: ticker, direction (long/short), thesis, entry price, stop price, target(s).

## Pre-Trade Checklist Gates

Evaluate each gate against current data. ALL must pass for a go decision:

1. **Regime alignment** — invoke `tm-regime` or read latest regime state. Flag color must permit new entries.
2. **IV percentile** — if options involved: >80th = sell premium only, <20th = buy options, 20-80 = equity only.
3. **Portfolio heat** — current total risk across all positions must be under the configured limit after this trade.
4. **Correlation check** — new position's sector/factor correlation with existing holdings. Reject if it pushes sector correlation above threshold.
5. **Earnings clearance** — no unresolved earnings within the planned hold period (unless the thesis specifically targets earnings).
6. **Calendar position** — prefer entries after OpEx, FOMC, or other uncertainty-resolving events.
7. **Pot odds** — expected R:R must meet minimum (default 2:1), dynamically adjusted by setup probability from quant layer EV tables.

## Position Sizing

If checklist passes, calculate: half-Kelly base × conviction tier (Tier 1: 2%, Tier 2: 1%, Tier 3: 0.25%) × liquidity multiplier × regime adjustment. Present the math transparently.

## Output

Present as a structured assessment: each gate with pass/fail and data, the composite decision, and the sizing recommendation. If any gate fails, explain what would need to change for it to pass. Update wiki ticker page if new thesis information was provided.

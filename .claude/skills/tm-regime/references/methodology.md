# Regime Assessment Methodology

Three independent layers vote on the market regime. A stock only gets full position sizing when all three align. Disagreement between layers is itself a signal — it means reduced conviction.

## Layer 1: Macro Regime

Assess the broad market environment using these data sources:

**FRED data** (via `fred` MCP):
- 10Y-2Y Treasury spread (yield curve) — inversion = recession signal
- Federal funds rate — direction and velocity of change
- Unemployment claims — leading labor indicator

**Market volatility**:
- VIX current level and term structure (via `financekit`)
- VIX >20 = elevated, >30 = crisis territory

**Breadth indicators** (via `financekit` or `yahoo-finance`):
- Advance/decline ratio for NYSE/NASDAQ
- New 52-week highs vs. lows
- Percentage of stocks above 50-day and 200-day moving averages

**Classification:**
- **Bull**: yield curve normal, VIX <20, breadth expanding (>60% above 200-day MA), A/D ratio positive
- **Bear**: yield curve inverted or flattening, VIX >25, breadth contracting (<40% above 200-day MA), A/D ratio negative
- **Sideways**: mixed signals, VIX 20-25, breadth neutral (40-60%), no clear direction

Assign confidence 0.0-1.0 based on signal agreement within the layer.

## Layer 2: Sector Regime

Assess sector rotation and relative strength:

**Sector rotation** (via `financekit` sector_rotation):
- Which sectors are leading/lagging on 1-month and 3-month relative strength
- Rotation direction: early-cycle (tech, consumer disc) → mid-cycle (industrials, materials) → late-cycle (energy, utilities, staples) → recession (utilities, healthcare)

**Relative strength rankings**:
- Top 3 and bottom 3 sectors by RS
- Week-over-week RS change direction — accelerating or decelerating

Identify sectors rotating into leadership and out of leadership. This determines where new entries should focus.

## Layer 3: Stock-Level Momentum

Assess the momentum health of individual stocks within the universe:

**Distribution day counting** — use the script for deterministic calculation:

Run: `python3 scripts/distribution_days.py --index SPY --index QQQ --index DIA --days 25`

The script accepts JSON price/volume data from stdin. Pipe the historical data from yahoo-finance MCP:
1. Fetch 30 trading days of daily OHLCV for SPY, QQQ, DIA
2. Pass as JSON to the script
3. Script returns distribution day count per index

Distribution day thresholds: 4+ distribution days in 25 trading days = yellow flag. 6+ = red flag.

**R0 Propagation Rate** — measure how momentum is spreading:
- Count new breakouts (52-week high on above-average volume) per sector in the last 5 trading days
- R0 >1 per sector = momentum spreading (bullish)
- R0 <1 = momentum fading (early warning)
- Track week-over-week change in R0

**Stalling days**: index closes in the upper half of its range but on volume higher than the previous day, with a gain of less than 0.2%. This signals institutional distribution disguised as a flat day.

## Synthesis

Combine all three layers into the composite regime state:

**Flag determination:**
- **Green**: all three layers agree bullish → full position sizing, new entries allowed
- **Yellow**: one layer disagrees or distribution days ≥ 4 → reduce sizing to 50%, confirm new entries
- **Red**: two layers bearish or distribution days ≥ 6 → halt new entries, tighten existing stops
- **Black (Safety Car)**: any circuit breaker triggered → halt everything, force portfolio review

**Safety Car triggers** (any one = black flag):
- VIX closes above 30
- Any major index (SPY, QQQ, DIA) drops ≥ 3% in a single session
- Yield curve inverts (10Y-2Y goes negative) when it was positive the prior session

**Portfolio implications by flag:**

| Flag | Position Size | New Entries | Cash Reserve | Stop Width |
|------|--------------|-------------|--------------|------------|
| Green | Full (per conviction tier) | Allowed, any tier | 20% minimum | Standard ATR |
| Yellow | 50% of normal | Tier 1 only, with confirmation | 30% minimum | Tighten to 1.5x ATR |
| Red | No new positions | Halted | 40% minimum | Tighten to 1x ATR |
| Black | Emergency review | Halted + review all open | 60% target | Immediate review all stops |

## Wiki Integration

After completing the assessment, check if the current regime matches any documented pattern in `wiki/regimes/`. If a matching playbook exists, surface its historical notes — "Last time we saw this pattern (VIX spike + yield curve flattening), the playbook says..."

If this is a new regime pattern not yet documented, note it as a candidate for wiki expansion during the next synthesis cycle.

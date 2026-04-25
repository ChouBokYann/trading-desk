# Options Strategy Menu

Full 18-strategy reference organized by conviction and thesis type. Consult this before every trade to ensure the selected strategy matches the setup.

---

## Directional -- High Conviction (7-10)

| Strategy | When | Structure |
|---|---|---|
| **Long Call** | Bullish, want leverage, IV low | Buy call |
| **Long Put** | Bearish, want leverage, IV low | Buy put |
| **Bull Call Spread** | Bullish, want to cap cost | Buy lower call, sell higher call |
| **Bear Put Spread** | Bearish, want defined risk | Buy higher put, sell lower put |

## Directional -- Moderate Conviction (5-7)

| Strategy | When | Structure |
|---|---|---|
| **Bull Put Spread** (credit) | Lean bullish, sell premium, IV high | Sell higher put, buy lower put |
| **Bear Call Spread** (credit) | Lean bearish, sell premium, IV high | Sell lower call, buy higher call |
| **Risk Reversal** | Strong directional, willing to take assignment | Sell put + buy call (bullish) or sell call + buy put (bearish) |
| **Collar** | Protect existing long, cap upside | Long stock + buy put + sell call |

## Directional -- Low Conviction (4-5)

| Strategy | When | Structure |
|---|---|---|
| **Bull Put Spread** (credit, narrow) | Slight bullish lean, want high probability | Sell put near support, buy lower put; keep width tight |
| **Bear Call Spread** (credit, narrow) | Slight bearish lean, want high probability | Sell call near resistance, buy higher call; keep width tight |
| **Iron Condor** (tight wings) | Lean neutral with slight directional bias, IV elevated | Bull put spread + bear call spread; skew wing width toward directional lean |

Low-conviction trades must use defined-risk structures only. No naked positions. Keep max loss under 2% of portfolio.

## Neutral / Rangebound

| Strategy | When | Structure |
|---|---|---|
| **Iron Condor** | Rangebound, high IV, sell premium | Bull put spread + bear call spread |
| **Short Strangle** | Rangebound, high IV, want max premium (higher risk) | Sell OTM put + sell OTM call |
| **Iron Butterfly** | Pinning to specific price, high IV | Sell ATM call + sell ATM put + buy OTM wings |
| **Calendar Spread** | Rangebound near-term, directional long-term | Sell near-term, buy far-term same strike |

## Volatility Plays

| Strategy | When | Structure |
|---|---|---|
| **Long Straddle** | Expecting big move, direction unknown, IV low | Buy ATM call + ATM put |
| **Long Strangle** | Expecting big move, cheaper than straddle | Buy OTM call + OTM put |
| **Butterfly** | Pinning to target, cheap bet | Buy 1 lower + buy 1 higher + sell 2 middle |
| **Ratio Spread** | Skewed probability, partial hedge | Unequal legs (e.g., buy 1, sell 2). Note: also usable as a directional play when the thesis has a specific price target with high confidence -- the free/credit leg adds leverage toward that target. |
| **Diagonal Spread** | Directional + theta, different strikes and expiries | Buy far-term, sell near-term at different strike |
| **Jade Lizard** | Bullish, collect premium, no upside risk | Short put + short call spread |
| **PMCC (Poor Man's Covered Call)** | Bullish long-term, generate income | Buy deep ITM LEAP + sell OTM near-term call |

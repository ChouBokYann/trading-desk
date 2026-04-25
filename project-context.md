# Trading Desk — Project Context

## Account

- **Type**: Paper trading (Alpaca paper account)
- **Size**: $100,000
- **Status**: Simulation — no real capital at risk; recommendations should still be risk-disciplined

## Instrument Priority

1. **Options** — primary instrument; all agents should default to options-based trade structures when viable
2. **Equity** — secondary; used when options liquidity is poor or the setup doesn't warrant leverage

## Position Sizing Defaults

Agents should recommend sizing unless overridden by user instruction:

- **Max risk per trade**: 2% of account ($2,000)
- **Max position size**: 10% of account ($10,000 notional)
- **Max concurrent positions**: 10 (keeping ~10% cash reserve)
- **Options premium budget per trade**: up to $1,000–$2,000 (defined-risk structures preferred)

## Risk Preferences

- **Defined-risk structures preferred** — spreads, debit spreads, protective puts over naked short exposure
- **No hard sector or instrument exclusions**
- **Sizing and strike selection** are part of the trade recommendation — agents should not defer this to the user

## Holding Period

- No fixed constraint; let the setup dictate
- Swing (days–weeks) and position (weeks–months) are both acceptable
- Day-trading is low priority

## Output Expectations

- All dollar amounts should reflect the $100k account size
- Options recommendations must include: structure, strikes, expiry, max loss, max gain, breakeven
- Risk/reward should be stated explicitly; vague directional calls are not sufficient

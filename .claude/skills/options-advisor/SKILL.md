---
name: options-advisor
description: Analyze options strategies with Black-Scholes pricing, Greeks, P/L simulation, and IV analysis. Usage: /options-advisor AAPL bull call spread 180/185 30d
---

# Options Strategy Advisor

Comprehensive options strategy analysis — pricing, Greeks, P/L simulation, and strategy selection.

## Arguments

Ticker + strategy description. Examples:
- `/options-advisor AAPL covered call`
- `/options-advisor TSLA iron condor 380/385/395/400`
- `/options-advisor NVDA straddle before earnings`

## Supported Strategies (18)

**Income:** Covered Call, Cash-Secured Put, Poor Man's Covered Call
**Protection:** Protective Put, Collar
**Directional:** Bull Call Spread, Bull Put Spread, Bear Call Spread, Bear Put Spread
**Volatility:** Long/Short Straddle, Long/Short Strangle
**Range-Bound:** Iron Condor, Iron Butterfly
**Advanced:** Calendar Spread, Diagonal Spread, Ratio Spread

## Workflow

### Step 1: Gather Data

Use MCP tools:
- `mcp__financekit__stock_quote` — current price
- `mcp__financekit__technical_analysis` — support/resistance for strike selection
- `mcp__yahoo-finance__get_option_expiration_dates` — available expiries
- `mcp__yahoo-finance__get_option_chain` — live quotes, IV

### Step 2: IV Assessment

Compare implied volatility to historical:
- **IV > HV by 20%+**: Options expensive → favor selling premium (credit spreads, iron condors, short strangles)
- **IV < HV by 20%+**: Options cheap → favor buying premium (debit spreads, straddles, long calls/puts)
- **IV ≈ HV**: Fairly priced → any strategy appropriate

### Step 3: Strategy Analysis

For the selected strategy, calculate:
- **Theoretical price** for each leg (Black-Scholes if needed)
- **Net debit/credit** from live quotes
- **Max profit, max loss, breakeven(s)**
- **Position Greeks** (Delta, Gamma, Theta, Vega)
- **Probability of profit** (simplified from delta)

### Step 4: Present Report

```
# Options Analysis: {Strategy} on {TICKER}
**Price:** ${X} | **IV:** {X}% | **IV Percentile:** {high/normal/low}

## Setup
| Leg | Type | Strike | Exp | Price | Position |
|-----|------|--------|-----|-------|----------|

**Net Debit/Credit:** ${X}

## P/L Profile
- Max Profit: ${X} (at ${price})
- Max Loss: ${X} (at ${price})
- Breakeven: ${X}
- Risk/Reward: {ratio}

## Greeks
- Delta: {X} | Gamma: {X} | Theta: {X}/day | Vega: {X}

## Trade Management
- Profit target: {50-75%} of max
- Stop loss: {criteria}
- Adjustment trigger: {criteria}

## Alternatives
| Strategy | Max Profit | Max Loss | When Better |
|----------|-----------|----------|-------------|
```

Information only — not a trade signal.

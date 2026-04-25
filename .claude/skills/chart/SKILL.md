---
name: chart
description: Quick technical analysis for a ticker. Tara reads price action, levels, and indicators. Usage: /chart AAPL
---

# Technical Chart Check

Tara reads the chart for the given ticker. Information only — not a trade signal.

## Arguments

The first argument is the ticker symbol (required). Example: `/chart AAPL`

## Execution

### Step 1: Load Persona

Read Tara's BMad agent skill: `{project-root}/.claude/skills/agent-tara/SKILL.md` and `{project-root}/.claude/skills/agent-tara/references/technical-analysis.md`.

### Step 2: Gather Data (parallel)

Run both of these in parallel:

1. **Full market data** — run `python scripts/fetch_data.py <TICKER>` via Bash to get price history, technicals (SMA, RSI, MACD, ATR, volume), and 52-week range
2. **Risk metrics** — use the `financekit` MCP server to get additional technical indicators for `<TICKER>` (Bollinger Bands, ADX, Stochastic if available) and risk metrics (Beta, volatility)

### Step 3: Spawn Tara

Spawn a single Agent with Tara's persona and all gathered data:

```
{contents of agent-tara SKILL.md}

{contents of agent-tara references/technical-analysis.md}

## Market Data for {TICKER}
{Full MARKET_DATA JSON from fetch_data.py — especially price history, technicals, and volume}

## Additional Indicators
{Risk metrics and additional indicators from financekit}

## Your Task
Analyze {TICKER} technically using your full output format. Use the actual numbers — cite exact RSI values, MACD state, specific support/resistance levels from recent price history, MA positions, and volume trends. Be direct about what the chart says. Keep your analysis under 400 words.

End with: *📈 Information only — not a trade signal.*
```

Use model `haiku` for the agent.

### Step 4: Present

Present Tara's full response directly to the user. After her response, add:

> **Follow up?** Ask Tara anything, or run `/analyze <TICKER>` for the full 13-agent desk.

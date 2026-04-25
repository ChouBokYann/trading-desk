---
name: valuation
description: Quick fundamentals and valuation check for a ticker. Frank digs into the numbers — PE, margins, balance sheet, cash flow. Usage: /valuation AAPL
---

# Fundamentals & Valuation Check

Frank digs into the numbers for the given ticker. Information only — not a trade signal.

## Arguments

The first argument is the ticker symbol (required). Example: `/valuation AAPL`

## Execution

### Step 1: Load Persona

Read Frank's BMad agent skill: `{project-root}/.claude/skills/agent-frank/SKILL.md` and `{project-root}/.claude/skills/agent-frank/references/fundamentals-analysis.md`.

### Step 2: Gather Data (parallel)

Run all of these in parallel:

1. **Market data** — run `python scripts/fetch_data.py <TICKER>` via Bash to get fundamentals (PE, PEG, EPS, margins, ROE, debt-to-equity, current ratio, FCF, revenue, EBITDA)
2. **SEC financials** — use the `edgartools` MCP server to pull the most recent 10-K or 10-Q financial statements for the ticker (income statement, balance sheet, cash flow)
3. **Additional metrics** — use the `financekit` MCP server to get valuation ratios, profitability metrics, and risk metrics for the ticker

### Step 3: Spawn Frank

Spawn a single Agent with Frank's persona and all gathered data:

```
{contents of agent-frank SKILL.md}

{contents of agent-frank references/fundamentals-analysis.md}

## Market Data for {TICKER}
{Full MARKET_DATA JSON from fetch_data.py — especially the fundamentals section}

## SEC Financial Statements
{Recent 10-K/10-Q data from edgartools — income statement, balance sheet, cash flow}

## Additional Metrics
{Valuation and risk metrics from financekit}

## Your Task
Analyze {TICKER} fundamentals using your full output format. Use the actual numbers — cite exact PE ratios, margins, debt levels, and cash flow figures. Compare to what you'd consider reasonable for this sector. Be skeptical of growth narratives that aren't backed by the financials. Keep your analysis under 400 words.

End with: *💰 Information only — not a trade signal.*
```

Use model `haiku` for the agent.

### Step 4: Present

Present Frank's full response directly to the user. After his response, add:

> **Follow up?** Ask Frank anything, or run `/analyze <TICKER>` for the full 13-agent desk.

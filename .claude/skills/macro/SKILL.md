---
name: macro
description: Quick macro-economic context check for a ticker. Marco reads the regime, sector positioning, and macro forces. Usage: /macro AAPL
---

# Macro Environment Check

Marco reads the macro environment for the given ticker. Information only — not a trade signal.

## Arguments

The first argument is the ticker symbol (required). Example: `/macro AAPL`

## Execution

### Step 1: Load Persona

Read Marco's BMad agent skill: `{project-root}/.claude/skills/agent-marco/SKILL.md` and `{project-root}/.claude/skills/agent-marco/references/macro-analysis.md`.

### Step 2: Gather Data (parallel)

Run all of these in parallel:

1. **Market data** — run `python scripts/fetch_data.py <TICKER>` via Bash to get price context, beta, sector, and 52-week range
2. **Macro context** — use the `omnisearch` MCP server (web_search tool) to search for:
   - `"macro economic outlook today Fed rates"` (current regime)
   - `"<TICKER> sector rotation"` (sector positioning)
3. **Risk metrics** — use the `financekit` MCP server to get beta, sector performance, and correlation data for the ticker if available

### Step 3: Spawn Marco

Spawn a single Agent with Marco's persona and all gathered data:

```
{contents of agent-marco SKILL.md}

{contents of agent-marco references/macro-analysis.md}

## Market Data for {TICKER}
{Full MARKET_DATA JSON from fetch_data.py — especially fundamentals section for beta, sector info, and 52-week range}

## Current Macro Environment
{Search results about Fed, rates, macro outlook from omnisearch}

## Sector & Risk Context
{Sector rotation info and risk metrics from financekit}

## Your Task
Analyze {TICKER} from a macro perspective using your full output format. Start with the regime — don't jump to the ticker. Use actual beta values, 52-week positioning, and current macro data. Be specific about what macro forces are acting on this name. Keep your analysis under 400 words.

End with: *🌍 Information only — not a trade signal.*
```

Use model `haiku` for the agent.

### Step 4: Present

Present Marco's full response directly to the user. After his response, add:

> **Follow up?** Ask Marco anything, or run `/analyze <TICKER>` for the full 13-agent desk.

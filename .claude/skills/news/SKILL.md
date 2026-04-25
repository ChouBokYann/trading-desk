---
name: news
description: Quick news and catalyst scan for a ticker. Nadia finds what's new, what's priced in, and what insiders are doing. Usage: /news AAPL
---

# News & Catalyst Scan

Nadia runs a wire-speed news scan for the given ticker. Information only — not a trade signal.

## Arguments

The first argument is the ticker symbol (required). Example: `/news AAPL`

## Execution

### Step 1: Load Persona

Read Nadia's BMad agent skill: `{project-root}/.claude/skills/agent-nadia/SKILL.md` and `{project-root}/.claude/skills/agent-nadia/references/news-catalyst-analysis.md`.

### Step 2: Gather Data (parallel)

Run all of these in parallel to collect data for Nadia:

1. **Market data** — run `python scripts/fetch_data.py <TICKER>` via Bash to get price context and recent news from yfinance
2. **SEC filings** — use the `edgartools` MCP server to search for recent insider transactions (Form 4) and material filings (8-K) for the ticker
3. **Live news search** — use the `omnisearch` MCP server (web_search tool) to search for `"<TICKER> stock news today"` and `"<TICKER> catalyst earnings"` to find breaking stories
4. **News feed** — if the `opennews` MCP server is available, fetch recent financial news mentioning the ticker

### Step 3: Spawn Nadia

Spawn a single Agent with Nadia's persona and all gathered data:

```
{contents of agent-nadia SKILL.md}

{contents of agent-nadia references/news-catalyst-analysis.md}

## Market Data for {TICKER}
{MARKET_DATA from fetch_data.py — price, news, insider sections}

## SEC Filings
{insider transactions and recent 8-K filings from edgartools}

## Live News
{search results from omnisearch and opennews}

## Your Task
Analyze {TICKER} using your full output format. Use the actual data above — cite specific headlines, insider names, and dollar amounts. Flag what's genuinely new information vs recycled narrative. Keep your analysis under 400 words.

End with: *📰 Information only — not a trade signal.*
```

Use model `haiku` for the agent.

### Step 4: Present

Present Nadia's full response directly to the user. After her response, add:

> **Follow up?** Ask Nadia anything, or run `/analyze <TICKER>` for the full 13-agent desk.

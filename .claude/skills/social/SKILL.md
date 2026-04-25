---
name: social
description: Quick social media sentiment scan for a ticker. Sage reads the crowd across Reddit and fintwit. Usage: /social AAPL
---

# Social Sentiment Scan

Sage reads the crowd for the given ticker. Information only — not a trade signal.

## Arguments

The first argument is the ticker symbol (required). Example: `/social AAPL`

## Execution

### Step 1: Load Persona

Read Sage's BMad agent skill: `{project-root}/.claude/skills/agent-sage/SKILL.md` and `{project-root}/.claude/skills/agent-sage/references/sentiment-analysis.md`.

### Step 2: Gather Data (parallel)

Run all of these in parallel:

1. **Reddit sentiment** — use the `reddit` MCP server to:
   - Search r/wallstreetbets for posts mentioning `<TICKER>` (recent, top 10)
   - Search r/stocks for posts mentioning `<TICKER>` (recent, top 5)
   - Search r/options for posts mentioning `<TICKER>` (recent, top 5)
2. **Fintwit / web sentiment** — use the `omnisearch` MCP server (web_search tool) to search for `"$<TICKER> stock twitter sentiment"` and `"<TICKER> reddit wallstreetbets"`
3. **Basic price context** — run `python scripts/fetch_data.py <TICKER>` via Bash (Sage needs price context to assess whether sentiment leads or lags the move)

### Step 3: Spawn Sage

Spawn a single Agent with Sage's persona and all gathered data:

```
{contents of agent-sage SKILL.md}

{contents of agent-sage references/sentiment-analysis.md}

## Price Context for {TICKER}
{price and volume data from fetch_data.py — just the price section, not full JSON}

## Reddit Activity
{Reddit posts and comments from r/wallstreetbets, r/stocks, r/options}

## Web Sentiment
{Search results from omnisearch — fintwit mentions, sentiment articles}

## Your Task
Analyze {TICKER} social sentiment using your full output format. Cite specific Reddit posts, upvote counts, and sentiment patterns you observe. Distinguish between informed retail conviction and meme-driven noise. Keep your analysis under 400 words.

End with: *💬 Information only — not a trade signal.*
```

Use model `haiku` for the agent. Give the agent `WebSearch` permission so it can do additional lookups if the initial data is thin.

### Step 4: Present

Present Sage's full response directly to the user. After her response, add:

> **Follow up?** Ask Sage anything, or run `/analyze <TICKER>` for the full 13-agent desk.

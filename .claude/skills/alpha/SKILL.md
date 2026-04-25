---
name: alpha
description: Hunt for alpha opportunities across equities, options, and crypto. Mr. A screens multiple signal sources and auto-chains the top pick into /analyze. Usage: /alpha
---

# Alpha Hunter

Mr. A screens for asymmetric opportunities across equities, options, and crypto using MCP tools, then auto-chains the top equity pick into the full 13-agent `/analyze` pipeline.

## Arguments

Optional: focus area (e.g., `/alpha crypto`, `/alpha tech`, `/alpha options`). Default: scan all asset classes.

## Execution Flow

### Stage 1: Market Environment

Use `mcp__financekit__market_overview` to get current conditions (indices, VIX, sector performance, top movers).

Set the regime context for scoring:
- **Risk-on** (VIX < 18, broad advance) — favor breakout and momentum signals
- **Neutral** (VIX 18-25) — favor convergence plays with multiple confirming signals
- **Risk-off** (VIX > 25) — favor defensive rotation, put flow, and short-side alpha

### Stage 2: Multi-Source Signal Sweep (parallel)

Run all of these in parallel to build the raw signal pool:

**Equity signals:**
1. `mcp__alpaca__get_most_active_stocks` — volume leaders
2. `mcp__alpaca__get_market_movers` — biggest movers (gainers and losers)
3. `mcp__financekit__sector_rotation` — sectors showing relative strength shifts
4. `mcp__opennews__get_news_by_signal` with signal `SMART_MONEY_TRADE` — institutional flow detection
5. `mcp__opennews__get_news_by_signal` with signal `PRICE_SPIKE` — breakout detection
6. `mcp__opennews__get_news_by_signal` with signal `INSIDER_PATTERN` — insider activity clusters
7. `mcp__opennews__get_high_score_news` — highest-impact news (score > 70)

**Options signals:**
8. `mcp__opennews__get_news_by_signal` with signal `WHALE_POSITION` — large positioning
9. `mcp__opennews__get_news_by_engine` with engine `MARKET` — funding rates, liquidation, OI changes

**Crypto signals:**
10. `mcp__financekit__crypto_trending` — trending coins
11. `mcp__opennews__get_news_by_engine` with engine `ONCHAIN` — whale trades, KOL activity
12. `mcp__opennews__get_news_by_engine` with engine `LISTING` — new exchange listings
13. `mcp__opennews__get_news_by_signal` with signal `NEW_WALLET_TRADE` — new wallet accumulation

If user specified a focus area, skip irrelevant signal groups.

### Stage 3: Candidate Selection & Enrichment

From the signal pool, identify the top 10-15 unique tickers/coins that appear across multiple signal sources. Prioritize **convergence** — candidates that show up in 2+ signal categories.

For each equity candidate (top 8), gather enrichment data in parallel:
- `mcp__financekit__stock_quote` — current price, volume, change
- `mcp__financekit__technical_analysis` — RSI, MACD, moving averages, Bollinger Bands
- `mcp__yahoo-finance__get_stock_info` — PE, EPS growth, institutional ownership

For each crypto candidate (top 4), gather:
- `mcp__financekit__crypto_price` — current price and 24h metrics

### Stage 4: Spawn Mr. A

Read Mr. A's BMad agent skill files:
- `{project-root}/.claude/skills/agent-mr-a/SKILL.md`
- `{project-root}/.claude/skills/agent-mr-a/references/alpha-scan.md`
- `{project-root}/.claude/skills/agent-mr-a/references/scoring-rubric.md`

Spawn a single Agent with Mr. A's full agent definition and all gathered data:

```
{contents of agent-mr-a SKILL.md}

{contents of agent-mr-a references/alpha-scan.md}

{contents of agent-mr-a references/scoring-rubric.md}

## Market Environment
{market overview from Stage 1}
{regime assessment}

## Raw Signal Pool
### Equity Signals
{all equity signal results from Stage 2}

### Options Signals
{options signal results from Stage 2}

### Crypto Signals
{crypto signal results from Stage 2}

## Enrichment Data
{per-candidate enrichment from Stage 3}

## Your Task
Analyze the signal pool and produce your Alpha Watchlist using the scoring rubric. Rank the top 5-8 candidates across all asset classes. Label each as EQUITY, OPTIONS FLOW, or CRYPTO.

Name your single top equity pick for the auto-chain into /analyze. Include a Chain Context sentence summarizing why this pick has edge.

If nothing scores above 50, say so — "Nothing clean today. Patience is a position."
```

Use model `haiku` for the agent.

### Stage 5: Present & Auto-Chain

Present Mr. A's full Alpha Watchlist to the user.

Then, if Mr. A named a top equity pick with score >= 50:

**Write the chain context file** before invoking `/analyze`. Use the Write tool to create `.cache/alpha-chain-{TOP_TICKER}.md` with:

```
# Alpha Chain Context

**Ticker:** {TOP_TICKER}
**Score:** {score}/100
**Scan Date:** {today's date}
**Chain Context:** {Mr. A's chain context sentence verbatim}

## Key Signals
{bullet list of 2-3 convergent signals Mr. A identified — e.g., insider cluster, unusual options flow, technical setup}
```

Display:
> **Auto-chaining top pick into full desk analysis...**

Invoke the `/analyze` skill with the top equity ticker. This runs the full 13-agent pipeline (analysts, debate, trade, risk review) on Mr. A's best find.

If no equity pick scored >= 50, or Mr. A said "nothing clean today," skip the auto-chain and end with:

> **No alpha above threshold today.** Run `/alpha` again tomorrow, or `/analyze <TICKER>` on any watchlist candidate manually.

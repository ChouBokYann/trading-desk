# Phase 2.5: Qualitative Screen — Desk Agent Integration

This phase bridges the Trading Desk's analytical intelligence into The Money's execution pipeline. Four desk agents evaluate scanner candidates before quantitative signal evaluation — catching catalysts, fundamental risks, chart weaknesses, and crowding that the quant layer is blind to.

## Architecture

```
Watchlist (Phase 2)
    ↓
Step A: Prefetch market data (Python batch — no LLM)
    ↓
Step B: Dispatch 3-4 desk agents in parallel (subagents)
    ├── Nadia  — catalyst/news screen
    ├── Tara   — deep technical validation
    ├── Frank  — fundamental quality check
    └── Sage   — social sentiment (selective)
    ↓
Step C: Composite scoring (main context — reads JSONs)
    ↓
Signal Evaluation (Phase 3) — now includes qualitative gates
```

## Step A: Prefetch Market Data

Run `fetch_data.py` for each candidate to give desk agents all the raw data they need without separate MCP calls. This keeps each subagent lean.

```bash
# Orchestrator runs this loop
today=$(date +%Y-%m-%d)
mkdir -p {project-root}/_bmad/memory/tm/raw/prefetched/$today

for ticker in $(jq -r '.candidates | to_entries[] | .value[] | .ticker' watchlist.json | sort -u); do
  python {project-root}/scripts/fetch_data.py $ticker \
    > {project-root}/_bmad/memory/tm/raw/prefetched/$today/$ticker.json 2>/dev/null &
done
wait
```

This batches ~10-15 tickers in parallel, completing in ~5-10 seconds.

## Step B: Desk Agent Subagents

Spawn **3 agents in parallel** (4 if Sage is warranted). Each evaluates ALL candidates for its domain.

### Why batch by agent, not by ticker

- Each agent loads one persona + one methodology file = fixed context cost
- Agent evaluating 10 tickers with prefetched data = ~60s each
- vs. 10 separate subagents per agent = 30-40 subagent spawns = very slow
- Batching: 3-4 subagents total. Efficient.

### Subagent: Nadia (News/Catalysts)

**What she catches that The Money misses:**
- Negative catalysts (FDA rejections, lawsuits, downgrades)
- "Already priced in" situations where momentum is stale
- Insider selling clusters that signal institutional exit

**Prompt template:**
```
You are Nadia, the trading desk's wire-speed news analyst, running in
pipeline subagent mode.

Read your persona and methodology:
  {project-root}/.claude/skills/agent-nadia/SKILL.md
  {project-root}/.claude/skills/agent-nadia/references/news-catalyst-analysis.md

You are screening candidates for The Money's morning pipeline. For each
ticker below, analyze the prefetched market data and supplement with MCP
tools as needed:
  - mcp__opennews__search_news for breaking/recent news
  - mcp__edgartools__edgar_ownership for insider transactions

CANDIDATES: {ticker_list}
PREFETCHED DATA: {project-root}/_bmad/memory/tm/raw/prefetched/{today}/{TICKER}.json

For each candidate, produce a JSON assessment. Do NOT write your normal
free-text analysis — output ONLY the JSON array.

Write the results to:
  {project-root}/_bmad/memory/tm/raw/qualitative/{today}/nadia.json

Schema per ticker:
{
  "ticker": "NVDA",
  "agent": "nadia",
  "verdict": "bullish|bearish|neutral",
  "flag": "green|yellow|red",
  "catalyst": "one-line description of key catalyst or 'none'",
  "priced_in": "not|partially|fully",
  "insider_signal": "buying_cluster|routine_selling|unusual_selling|none",
  "blocks": false,
  "reason": "one sentence — why this flag color"
}

RED FLAG triggers (blocks=true):
- Imminent negative catalyst (FDA rejection, earnings warning, lawsuit filed)
- Insider selling cluster (3+ insiders selling in last 30 days)
- Fully priced in + stock at 52-week high (no upside catalyst remaining)

YELLOW FLAG triggers:
- Mixed catalyst picture (positive + negative competing)
- Partially priced in (some move already occurred)
- Single unusual insider sale

GREEN FLAG triggers:
- Positive catalyst not yet priced in
- Insider buying cluster
- No material negative news
```

### Subagent: Tara (Technical Depth)

**What she catches that the scanner misses:**
- Support/resistance levels (scanner only checks EMAs)
- Volume pattern quality (accumulation vs distribution)
- Chart pattern context (breakout from base vs random bounce)

**Prompt template:**
```
You are Tara, the trading desk's technical analyst, running in pipeline
subagent mode.

Read your persona and methodology:
  {project-root}/.claude/skills/agent-tara/SKILL.md
  {project-root}/.claude/skills/agent-tara/references/technical-analysis.md

You are screening candidates for The Money's morning pipeline. For each
ticker, read the prefetched market data and use MCP tools for additional
technical analysis:
  - mcp__financekit__technical_analysis for RSI, MACD, Bollinger Bands, MAs
  - mcp__financekit__price_history for recent OHLCV pattern analysis

CANDIDATES: {ticker_list}
PREFETCHED DATA: {project-root}/_bmad/memory/tm/raw/prefetched/{today}/{TICKER}.json

Write results to:
  {project-root}/_bmad/memory/tm/raw/qualitative/{today}/tara.json

Schema per ticker:
{
  "ticker": "NVDA",
  "agent": "tara",
  "verdict": "bullish|bearish|neutral",
  "flag": "green|yellow|red",
  "trend": "up|down|sideways",
  "support": 835.00,
  "resistance": 880.00,
  "setup_exists": true,
  "setup_type": "EMA pullback bounce|breakout|breakdown|none",
  "volume_pattern": "accumulation|distribution|neutral",
  "blocks": false,
  "reason": "one sentence — what the chart says"
}

RED FLAG triggers (blocks=true):
- Active breakdown: price below key support on >1.5x volume
- Distribution pattern: 3+ days of down volume > 1.5x average in last 10 days
- Death cross (50 MA crossing below 200 MA) in last 5 days

YELLOW FLAG triggers:
- Overbought (RSI >75) with diverging volume (price up, volume down)
- At resistance without breakout confirmation
- Sideways chop with no clear setup

GREEN FLAG triggers:
- Clean uptrend with accumulation volume
- Setup exists with defined entry/stop/target
- Breakout confirmed on volume
```

### Subagent: Frank (Fundamental Quality)

**What he catches that The Money is completely blind to:**
- Overvalued stocks priced for perfection
- Deteriorating cash flow / earnings quality
- Dangerous debt levels
- Margin compression trends

**Prompt template:**
```
You are Frank, the trading desk's fundamentals analyst, running in
pipeline subagent mode.

Read your persona and methodology:
  {project-root}/.claude/skills/agent-frank/SKILL.md
  {project-root}/.claude/skills/agent-frank/references/fundamentals-analysis.md

You are screening candidates for The Money's morning pipeline. For each
ticker, read the prefetched market data (which includes fundamentals from
yfinance). Supplement with MCP tools as needed:
  - mcp__yahoo-finance__get_stock_info for detailed fundamentals
  - mcp__yahoo-finance__get_financial_statement for income/balance/cash flow
  - mcp__edgartools__edgar_company for SEC filings context

CANDIDATES: {ticker_list}
PREFETCHED DATA: {project-root}/_bmad/memory/tm/raw/prefetched/{today}/{TICKER}.json

Write results to:
  {project-root}/_bmad/memory/tm/raw/qualitative/{today}/frank.json

Schema per ticker:
{
  "ticker": "NVDA",
  "agent": "frank",
  "verdict": "bullish|bearish|neutral",
  "flag": "green|yellow|red",
  "pe_forward": 34.0,
  "pe_vs_sector": "premium|inline|discount",
  "fcf_positive": true,
  "margin_trend": "expanding|stable|compressing",
  "debt_concern": false,
  "earnings_quality": "high|medium|low",
  "blocks": false,
  "reason": "one sentence — do the numbers justify the price?"
}

RED FLAG triggers (blocks=true):
- Negative free cash flow for 2+ consecutive quarters
- Debt-to-equity >2.0 AND interest coverage <3.0
- Earnings quality low: net income significantly exceeds operating cash flow
- Stock priced at >3x sector median PE with decelerating revenue growth

YELLOW FLAG triggers:
- Forward PE >2x sector median (priced for perfection)
- Margin compression trend (declining gross or operating margins)
- Debt-to-equity >1.5 (elevated but not critical)

GREEN FLAG triggers:
- FCF positive and growing
- Valuation at or below sector median
- Margins stable or expanding
- Strong balance sheet (net cash, current ratio >2)
```

### Subagent: Sage (Social Sentiment) — SELECTIVE

Deploy Sage only when candidates include **high-retail-attention names**. The orchestrator checks: if any candidate is in the top-50 by social volume (WSB darlings like NVDA, TSLA, AMD, PLTR, META, GME, etc.), spawn Sage. Otherwise skip.

**Prompt template:**
```
You are Sage, the trading desk's social sentiment analyst, running in
pipeline subagent mode.

Read your persona and methodology:
  {project-root}/.claude/skills/agent-sage/SKILL.md
  {project-root}/.claude/skills/agent-sage/references/sentiment-analysis.md

Screen these candidates for crowding risk and sentiment positioning:
  - mcp__reddit__reddit_search_subreddit for ticker mentions in r/wallstreetbets, r/stocks
  - mcp__opennews__search_news_by_coin or search_news for social buzz
  - WebSearch for broader fintwit sentiment

CANDIDATES: {ticker_list}
PREFETCHED DATA: {project-root}/_bmad/memory/tm/raw/prefetched/{today}/{TICKER}.json

Write results to:
  {project-root}/_bmad/memory/tm/raw/qualitative/{today}/sage.json

Schema per ticker:
{
  "ticker": "NVDA",
  "agent": "sage",
  "verdict": "bullish|bearish|neutral|mixed",
  "flag": "green|yellow|red",
  "buzz_level": "quiet|warming|trending|viral",
  "sentiment": "bullish|bearish|confused",
  "signal_vs_noise": "signal|noise|mixed",
  "crowding_risk": "low|moderate|high",
  "blocks": false,
  "reason": "one sentence — what the crowd is doing and whether it matters"
}

RED FLAG triggers (blocks=true):
- Viral + Bullish + stock at 52-week high (classic exit liquidity)
- Extreme crowding: call/put ratio >4:1 with sentiment unanimous

YELLOW FLAG triggers:
- Trending + strong directional lean (moderate crowding risk)
- Sentiment lagging price by >1 week (crowd is late)

GREEN FLAG triggers:
- Quiet or warming (no crowding risk)
- Signal classification (informed conviction, not hype)
```

## Step C: Composite Scoring

After all subagents return, the orchestrator reads the JSON results and computes a composite assessment per ticker.

**Composite logic (in main context):**

```python
# Pseudocode — executed by the orchestrator reading JSON files

for each ticker in candidates:
    flags = [nadia.flag, tara.flag, frank.flag]
    if sage_ran: flags.append(sage.flag)
    
    # Worst flag wins
    if "red" in flags:
        composite_flag = "red"
        sizing_adjustment = "block"
    elif "yellow" in flags:
        composite_flag = "yellow"
        sizing_adjustment = "reduce"  # 50% of exploration sizing
    else:
        composite_flag = "green"
        sizing_adjustment = "none"
    
    # Any single blocks=true → block the trade
    if any(agent.blocks for agent in [nadia, tara, frank, sage]):
        composite_flag = "red"
        sizing_adjustment = "block"
    
    write composite to raw/qualitative/{today}/composite.json
```

**Output: `composite.json`**
```json
{
  "date": "2026-04-27",
  "assessments": [
    {
      "ticker": "NVDA",
      "composite_flag": "yellow",
      "sizing_adjustment": "reduce",
      "blocks_trade": false,
      "flags": {
        "nadia": "green",
        "tara": "green",
        "frank": "yellow",
        "sage": null
      },
      "summary": "Technically clean (Tara), no negative catalyst (Nadia), valuation stretched at 34x fwd PE (Frank)"
    }
  ]
}
```

## How Phase 3 Uses Qualitative Data

The signal evaluation subagents (Phase 3) receive the composite.json as additional context. Two new gates are added to every strategy checklist:

**Qualitative Gate A: No Red Flags**
- Read composite_flag for this ticker
- If "red" or blocks_trade=true → FAIL
- This is a hard gate — red qualitative flag = no trade

**Qualitative Gate B: Sizing Adjustment**
- If composite_flag = "yellow" → reduce exploration sizing by 50%
- If composite_flag = "green" → full exploration sizing
- This is a soft gate — yellow doesn't block, it reduces conviction

## High-Buzz Ticker List (for Sage dispatch)

Maintain a list of tickers that warrant social sentiment screening. Default:

```
NVDA, TSLA, AMD, PLTR, META, AMZN, AAPL, MSFT, GME, AMC,
SOFI, RIVN, LCID, NIO, COIN, MARA, RIOT, SQ, SHOP, SNOW
```

If any candidate from the watchlist appears in this list, dispatch Sage. Otherwise skip Sage to save a subagent context.

## Timing Budget

| Step | Duration | Method |
|------|----------|--------|
| A: Prefetch | ~10s | Parallel Python processes |
| B: Desk agents | ~60-90s | 3-4 parallel subagents |
| C: Composite | ~5s | Main context reads JSON |
| **Total Phase 2.5** | **~90s** | |

Total pipeline with qualitative screen: ~7-8 minutes (was ~5-6 without).

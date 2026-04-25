---
name: screen
description: Screen for stocks using CANSLIM methodology or market movers. Usage: /screen [universe]. Finds growth stocks with strong earnings momentum, relative strength, and institutional support.
---

# Stock Screener

Screen US stocks for trading candidates using CANSLIM methodology and MCP market data tools.

## Arguments

Optional: sector or universe (e.g., `/screen Technology`, `/screen S&P500`). Default: top 40 S&P 500 by market cap.

## Execution Flow

### Stage 1: Market Environment Check

Use `mcp__financekit__market_overview` to get current market conditions (indices, VIX, top movers).

If VIX > 30 or market is in clear downtrend, warn: "Bear market conditions — CANSLIM recommends raising cash."

### Stage 2: Get Candidates

Use multiple MCP tools in parallel to build a candidate list:
- `mcp__alpaca__get_most_active_stocks` — volume leaders
- `mcp__alpaca__get_market_movers` — biggest movers
- `mcp__financekit__sector_rotation` — sectors showing strength
- `mcp__opennews__get_news_by_signal` — AI prediction signals (SMART_MONEY_TRADE, PRICE_SPIKE)

### Stage 3: Screen Each Candidate

For each candidate (top 10-15), gather data using:
- `mcp__financekit__stock_quote` — current price, volume
- `mcp__financekit__technical_analysis` — RSI, MACD, moving averages
- `mcp__yahoo-finance__get_stock_info` — PE, EPS, margins, institutional ownership
- `mcp__yahoo-finance__get_financial_statement` — quarterly earnings growth

Score each stock on the CANSLIM framework (0-100):
- **C** (Current Earnings): Quarterly EPS growth > 25% YoY
- **A** (Annual Growth): 3-year EPS CAGR > 25%
- **N** (Newness): Within 15% of 52-week high, breakout pattern
- **S** (Supply/Demand): Above-average volume on up days
- **L** (Leadership): Relative strength vs S&P 500 in top 20%
- **I** (Institutional): Growing institutional ownership, 40-70% range
- **M** (Market Direction): Broad market in confirmed uptrend

### Stage 4: Rank and Present

Present top 5-10 candidates ranked by composite score:

```
# Stock Screening Results — {date}
**Market Condition:** {trend} | **VIX:** {level} | **Stocks Screened:** {N}

## Top Candidates

### 1. {TICKER} — {Company Name}
**CANSLIM Score:** {X}/100 ({rating})
**Price:** ${X} | **RSI:** {X} | **Volume:** {X vs avg}

| Component | Score | Detail |
|-----------|-------|--------|
| C (Earnings) | {X} | {EPS growth}% QoQ |
| A (Growth) | {X} | {CAGR}% 3yr |
| N (Newness) | {X} | {dist}% from 52w high |
| S (Supply) | {X} | {volume ratio} |
| L (Leadership) | {X} | RS {rank} |
| I (Institutional) | {X} | {ownership}% |
| M (Market) | {X} | {trend} |

**Catalyst:** {upcoming event or news}
```

### Stage 5: Offer Next Steps

End with:
"Run `/analyze {TICKER}` on any candidate for full 13-agent analysis, or `/chart {TICKER}` for quick technicals."

Information only — not a trade signal.

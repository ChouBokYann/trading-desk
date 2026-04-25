# Trading Desk Companion

Interactive trading analysis via Claude Code skills — 14 named agent personas across 3 tiers.

## Commands

### Tier 1 — Quick Solo Checks (information only)
- `/news <TICKER>` — 📰 Nadia: news catalysts, insider signals, "is it priced in?"
- `/social <TICKER>` — 💬 Sage: Reddit/fintwit sentiment, crowd psychology
- `/chart <TICKER>` — 📈 Tara: technicals, levels, indicators, price action
- `/macro <TICKER>` — 🌍 Marco: macro regime, sector context, tailwinds/headwinds
- `/valuation <TICKER>` — 💰 Frank: PE, margins, balance sheet, cash flow quality
- `/screen [universe]` — CANSLIM stock screening with market movers
- `/options-advisor <TICKER>` — Options strategy analysis with Black-Scholes
- `/market-top` — Market top probability detection (distribution days, breadth, rotation)
- `/position-size <TICKER>` — Risk-based position sizing calculator

### Tier 2 — Alpha Discovery (auto-chains into Tier 3)
- `/alpha [focus]` — 🔍 Mr. A: multi-source alpha scan → auto-chains top pick into /analyze

### Tier 3 — Full Pipeline
- `/analyze <TICKER>` — All 14 agents: analysts → debate → trade → risk review

## Project Structure

- `.claude/skills/agent-{name}/` — 14 BMad agent skills (canonical), each with SKILL.md, customize.toml, and references/
- `.claude/skills/` — Orchestrator and solo skills (alpha, analyze, chart, edge-pipeline, macro, market-top, news, options-advisor, position-size, screen, social, valuation)
- `personas/` — Legacy persona files (kept for reference, agent skills are canonical)
- `scripts/fetch_data.py` — Market data prefetch (yfinance, outputs JSON to stdout)
- `.claude/vendor/` — Cloned reference repos (gitignored)
- `.mcp.json` — MCP server configs (gitignored, contains API keys)

## MCP Servers

Configured in `.mcp.json` (9 servers):
- **yahoo-finance** — Stock prices, fundamentals, options, earnings
- **reddit** — Social sentiment (WSB, r/stocks, r/options)
- **financekit** — Technical indicators, sector rotation, crypto prices
- **edgartools** — SEC filings, insider transactions, 13F
- **omnisearch** — Multi-engine web search (Tavily/Brave/Exa)
- **opennews** — Real-time news from 84+ sources with AI scoring
- **maverick-mcp** — Stock screening (S&P 500), backtesting, portfolio tracking, research agents (needs Tiingo key)
- **alpaca** — Paper trading, positions, orders, portfolio history (paper keys in .env)
- **fred** — Federal Reserve economic data (rates, CPI, unemployment, yield curve)

API keys stored in `.env` (gitignored). Keys needed: Tiingo, Alpaca, FRED, FMP.

## Conventions

- Persona files use YAML frontmatter + markdown body
- fetch_data.py outputs JSON to stdout — skills capture it via Bash
- Subagent model selection: haiku for solo analysts, default for debate/trade/risk
- Tier 1 skills always end with "Information only — not a trade signal"

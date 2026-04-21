# Trading Desk Companion

Interactive trading analysis via Claude Code skills. Type `/analyze AAPL` to run a full multi-agent analysis.

## How It Works

1. `/analyze <TICKER>` fetches market data via `scripts/fetch_data.py`
2. Five analyst subagents (Marco, Tara, Sage, Nadia, Frank) analyze in parallel
3. Bull/Bear researchers (Blaine, Vera) debate; Judge (Jaya) renders verdict
4. Trader (Rex) proposes a trade; Risk team (Axel, Nina, Cass) reviews; Risk Manager (Hugo) gives final call
5. You're now in a conversation — address any agent by name for follow-ups

## Project Structure

- `personas/` — Agent persona definitions (read at runtime by the /analyze skill)
- `scripts/fetch_data.py` — Standalone market data prefetch (yfinance)
- `.claude/skills/analyze/` — The /analyze skill definition

## Conventions

- Persona files use YAML frontmatter + markdown body
- fetch_data.py outputs JSON to stdout — the skill captures it via Bash
- Subagent model selection: haiku for analysts, default for debate/trade/risk stages

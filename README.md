# Trading Desk

AI-powered trading analysis for [Claude Code](https://claude.ai/code) — 14 named analyst personas, a full 14-agent debate pipeline, and an automated morning workflow.

---

## What It Does

Drop these skills into Claude Code and get a complete trading desk in your terminal:

- **14 analyst agents** — each with a distinct specialty (news, technicals, macro, valuation, risk, etc.)
- **`/analyze <TICKER>`** — chains all 14 agents: analysts → debate → trade recommendation → risk review
- **`/alpha`** — multi-source alpha scan that auto-chains into `/analyze` on the top pick
- **`/tm-morning`** — fully automated morning workflow: regime check → scan universe → evaluate setups → deploy orders

---

## Agents

| Skill | Persona | Specialty |
|-------|---------|-----------|
| `agent-nadia` | Nadia | News catalysts, SEC filings, "is it priced in?" |
| `agent-sage` | Sage | Reddit/fintwit sentiment, crowd psychology |
| `agent-tara` | Tara | Technicals, price action, key levels |
| `agent-marco` | Marco | Macro regime, sector context, tailwinds/headwinds |
| `agent-frank` | Frank | Valuation, PE, margins, balance sheet quality |
| `agent-hugo` | Hugo | Options flow, skew, unusual activity |
| `agent-jaya` | Jaya | Quantitative signals, momentum, mean reversion |
| `agent-axel` | Axel | Risk management, position sizing, stop placement |
| `agent-blaine` | Blaine | Debate moderator, synthesizes analyst views |
| `agent-cass` | Cass | Devil's advocate, stress-tests the thesis |
| `agent-rex` | Rex | Trade structuring (options first, equity second) |
| `agent-nina` | Nina | Portfolio-level risk review, correlation, concentration |
| `agent-vera` | Vera | Final trade verdict with entry/exit/sizing |
| `agent-mr-a` | Mr. A | Alpha hunter, multi-source opportunity scanner |

---

## Commands

### Tier 1 — Solo Checks (information only)

```
/news <TICKER>          Nadia: news catalysts, insider signals
/social <TICKER>        Sage: Reddit/fintwit sentiment
/chart <TICKER>         Tara: technicals, levels, indicators
/macro <TICKER>         Marco: macro regime, sector context
/valuation <TICKER>     Frank: PE, margins, balance sheet
/screen [universe]      CANSLIM screening with market movers
/options-advisor        Options strategy with Black-Scholes
/market-top             Market top probability detection
/position-size          Risk-based position sizing
```

### Tier 2 — Alpha Discovery

```
/alpha [focus]          Mr. A scans multiple sources → auto-chains top pick into /analyze
```

### Tier 3 — Full Pipeline

```
/analyze <TICKER>       All 14 agents: analysts → debate → trade → risk review
```

### The Money — Automated Morning Workflow

```
/tm-morning             Full pipeline: regime → scan → evaluate → deploy
/tm-morning scan        Re-run from scanner with existing regime
/tm-morning evaluate    Re-evaluate today's watchlist
/tm-morning deploy      Deploy from today's evaluations
```

---

## Install

### Option A — npx (easiest, no clone needed)

Requires Node 18+. Copies skills to `~/.claude/skills/` so they're available globally in Claude Code.

```bash
npx trading-desk
```

After running, follow the printed instructions to configure MCP servers and add the command block to your `CLAUDE.md`.

### Option B — Clone

```bash
git clone https://github.com/ChouBokYann/trading-desk.git
cd trading-desk
```

Open the cloned directory in Claude Code — the `.claude/skills/` folder is picked up automatically.

---

## Requirements

### Claude Code

Install from: https://claude.ai/code

### MCP Servers

Configure these in your project's `.mcp.json`. See [MCP server setup](https://modelcontextprotocol.io/docs/tools/desktop#configuration) for the format.

| Server | What It Powers | Keys Needed |
|--------|---------------|-------------|
| `yahoo-finance` | Prices, fundamentals, options, earnings | None (free) |
| `financekit` | Technical indicators, sector rotation | None (free) |
| `reddit` | Social sentiment (WSB, r/stocks) | Reddit API key |
| `edgartools` | SEC filings, insider transactions, 13F | None (free) |
| `opennews` | Real-time news from 84+ sources | OpenNews API key |
| `alpaca` | Paper/live trading, orders, positions | Alpaca API key |
| `fred` | Federal Reserve economic data | FRED API key |

Minimum working set: `yahoo-finance` + `financekit` + `opennews`. Add others progressively.

### CLAUDE.md Template

Add this block to your project's `CLAUDE.md` to wire up the commands:

```markdown
## Trading Desk Commands

### Tier 1 — Quick Solo Checks (information only)
- `/news <TICKER>` — Nadia: news catalysts, insider signals, "is it priced in?"
- `/social <TICKER>` — Sage: Reddit/fintwit sentiment, crowd psychology
- `/chart <TICKER>` — Tara: technicals, levels, indicators, price action
- `/macro <TICKER>` — Marco: macro regime, sector context, tailwinds/headwinds
- `/valuation <TICKER>` — Frank: PE, margins, balance sheet, cash flow quality
- `/screen [universe]` — CANSLIM stock screening with market movers
- `/options-advisor <TICKER>` — Options strategy analysis with Black-Scholes
- `/market-top` — Market top probability detection
- `/position-size <TICKER>` — Risk-based position sizing

### Tier 2 — Alpha Discovery
- `/alpha [focus]` — Mr. A: multi-source alpha scan → auto-chains top pick into /analyze

### Tier 3 — Full Pipeline
- `/analyze <TICKER>` — All 14 agents: analysts → debate → trade → risk review

### The Money — Automated Workflow
- `/tm-morning` — Full morning pipeline: regime → scan → evaluate → deploy
```

---

## Project Structure

```
.claude/skills/
  agent-{name}/      14 agent personas (SKILL.md + references/)
  alpha/             Alpha discovery orchestrator
  analyze/           Full 14-agent pipeline orchestrator
  chart/             Technicals solo skill
  macro/             Macro solo skill
  news/              News solo skill
  options-advisor/   Options strategy skill
  position-size/     Position sizing skill
  screen/            CANSLIM screener
  social/            Sentiment skill
  valuation/         Valuation skill
  tm-morning/        Morning workflow orchestrator
  tm-regime/         Regime detection
  tm-agent-quant/    Quant signal generator
  tm-deploy/         Order deployment
  tm-review/         Post-trade review
  tm-dashboard/      Portfolio dashboard
  tm-synthesis/      Daily synthesis

scripts/
  fetch_data.py          Market data prefetch (yfinance → JSON stdout)
  premarket_scanner.py   Batch pre-market scanner (6 strategies)
  universe.json          Curated ~110 stock universe by sector
```

---

## License

MIT

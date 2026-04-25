---
title: The Money Wiki Schema
type: schema
created: {today}
updated: {today}
---

# Wiki Conventions

This document defines the conventions for The Money's LLM wiki. The Quant and all workflows follow these rules when reading and writing wiki pages.

## Three-Layer Architecture

1. **Raw sources** (`raw/`) — Immutable. Trade logs, macro event snapshots, earnings data, regime snapshots. Never modified after creation. The source of truth.
2. **Wiki** (`wiki/`) — LLM-maintained compiled knowledge. Summaries, playbooks, ticker pages, post-mortems. The Quant owns this layer — creates pages, updates them, maintains cross-references.
3. **Schema** (this file) — Conventions for how the wiki is structured. Co-evolves over time as The Money learns what works.

## Page Types

| Type | Directory | Purpose | Example |
|------|-----------|---------|---------|
| `regime` | `wiki/regimes/` | Regime-specific playbooks with accumulated history | `vix-spike.md`, `bull-market.md` |
| `strategy` | `wiki/strategies/` | Strategy knowledge, rules, accumulated EV | `momentum-breakout.md` |
| `sector` | `wiki/sectors/` | Sector-level patterns and rotation knowledge | `technology.md`, `energy.md` |
| `causal-factor` | `wiki/causal-factors/` | Macro event factor pages | `tariff-policy.md`, `fed-rate-cycle.md` |
| `ticker` | `wiki/tickers/` | Per-ticker evolving thesis, trade history, key levels | `AAPL.md`, `NVDA.md` |
| `post-mortem` | `wiki/post-mortems/` | Trade post-mortem syntheses | `2026-04-25-AAPL-breakout.md` |

## Page Frontmatter

Every wiki page uses this YAML frontmatter:

```yaml
---
title: Page Title
type: regime | strategy | sector | causal-factor | ticker | post-mortem
sources:
  - raw/trade-logs/...
  - raw/macro-events/...
related:
  - "[[page-name]]"
  - "[[page-name|Display Text]]"
causal_factors:
  - macro-policy
  - earnings
created: YYYY-MM-DD
updated: YYYY-MM-DD
confidence: high | medium | low
---
```

## Causal Factor Taxonomy

Every trade outcome and wiki entry is tagged with one or more causal factors:

| Factor | Shortcode | Examples |
|--------|-----------|---------|
| Macro policy | `macro-policy` | Fed rate decision, tariff action, fiscal policy |
| Earnings/fundamentals | `earnings` | Earnings beat/miss, guidance change, revenue surprise |
| Market structure | `market-structure` | Options expiration pinning, short squeeze, meme momentum |
| Sector rotation | `sector-rotation` | Capital flow shift, relative strength regime change |
| Geopolitical | `geopolitical` | Conflict escalation, sanctions, trade war |
| Technical breakdown | `technical` | Support failure, trend break, volume climax |

## Confidence Levels

| Level | Meaning | Decay |
|-------|---------|-------|
| `high` | Multiple confirming episodes, recent data | Decays to medium after 90 days without reinforcement |
| `medium` | Some evidence, limited episodes | Decays to low after 60 days without reinforcement |
| `low` | Single observation, old data, or conflicting evidence | Candidate for removal during lint |

## Cross-Linking

Use wikilink syntax: `[[page-name]]` or `[[page-name|Display Text]]`. Pages referenced but not yet created are expected — they signal future wiki growth.

## Log Format

`wiki/log.md` is append-only. Each entry:

```markdown
## [YYYY-MM-DD] {action} | {brief description}
Source: raw/path/to/file.md (if applicable)
Pages created: wiki/path/page1.md
Pages updated: wiki/path/page2.md, wiki/path/page3.md
Notes: Additional context
```

Actions: `setup`, `ingest`, `review`, `synthesis`, `lint`, `strategy-update`, `regime-change`.

## File Naming

- Kebab-case for all files
- Ticker pages: uppercase ticker as filename (`AAPL.md`, `NVDA.md`)
- Post-mortems: `YYYY-MM-DD-TICKER-brief-description.md`
- Regime snapshots (raw): `YYYY-MM-DD-regime-snapshot.md`
- Trade logs (raw): `YYYY-MM-DD-TICKER-{entry|exit}.md`

## Three Core Operations

1. **Ingest** — After trade close or macro event: write raw source, then update all relevant wiki pages (may touch 5-15 pages), append to log.
2. **Synthesis** — Periodic (weekly/quarterly): read quant layer stats, cross-reference with wiki, distill patterns into regime/strategy/factor pages.
3. **Lint** — Periodic health check: contradictions, stale claims (confidence decay), orphan pages, missing cross-references, data gaps.

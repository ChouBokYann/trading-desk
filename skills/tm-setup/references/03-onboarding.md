# Stage 3: Onboarding

Check for the trading desk integration and run the wiki onboarding conversation to populate The Money's initial knowledge base.

## Desk Integration Check

Detect whether the Trading Desk Companion is installed by checking for the presence of desk agent skills (e.g., `{project-root}/.claude/skills/agent-rex/SKILL.md`).

**If desk is installed:**
- Note that Rex (risk) and Hugo (portfolio) are available as advisors to The Money
- Record in config: `desk_installed: true`
- The structured output adapters for Rex/Hugo will be built separately — note this as a future integration step

**If desk is not installed:**
- Configure standalone mode: The Money accepts manual signal input only
- Record in config: `desk_installed: false`
- Note that installing the desk later will enable richer signal flow

## Wiki Onboarding

Have a focused conversation to populate `wiki/overview.md` with the user's trading profile. This is the foundation The Quant reads on every activation — it needs to capture who this trader is.

Gather through natural conversation (not a form):

- **Capital and account**: approximate portfolio size, account type (margin/cash), any constraints
- **Risk appetite**: how much drawdown is acceptable before it affects sleep? Conservative, moderate, aggressive?
- **Trading style**: swing trader, position trader, day trader? Typical hold time?
- **Experience level**: how long trading, which markets (equities, options, both), any strategies they already use
- **Goals**: income generation, capital growth, learning? Timeline?
- **Known biases**: do they tend to hold losers too long? Cut winners too early? Overtrade? Self-awareness here is gold for The Quant.
- **Time commitment**: how much time per day/week can they spend on active trading decisions?

Write the conversation results to `wiki/overview.md` in a structured format that The Quant can parse on activation. Include frontmatter:

```yaml
---
title: Trader Profile & System Overview
type: overview
created: {today's date}
updated: {today's date}
confidence: medium
---
```

Also create the first `wiki/log.md` entry:

```markdown
## [{today's date}] setup | System Initialized
Pages created: wiki/overview.md, wiki/index.md, schema.md
Config: {summary of key settings}
Dependencies: {summary of status}
Notes: Fresh install. Onboarding complete.
```

## Completion

Summarize the full setup:
- Infrastructure created (wiki, database, daemon scaffold)
- Config values set
- Dependencies validated
- Trader profile captured

**Next steps for the user:**
1. Run `/tm-regime` to get an initial market regime assessment
2. Talk to The Quant (`/tm-agent-quant`) for an initial strategy session — it will read the wiki overview and help set up your first strategy rules
3. When ready, use `/tm-deploy` with a signal to paper-trade your first position

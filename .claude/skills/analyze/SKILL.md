---
name: analyze
description: Full 13-agent trading desk analysis pipeline. Use when user says '/analyze' followed by a ticker symbol.
---

# Trading Desk Analysis

## Overview

This skill orchestrates a 13-agent trading desk that mirrors an institutional investment committee workflow. Five analysts examine a ticker through independent lenses (macro, technical, sentiment, news, fundamentals), then three researchers debate the bull and bear cases before a neutral judge sets conviction. A trader proposes executable trades based on the verdict, three risk analysts with different risk appetites review the proposal, and a risk manager renders the final go/no-go decision with executable trade specs.

Stages are ordered to build cumulative conviction: broad analysis → adversarial debate → precise trade → risk scrutiny → execution. Parallel stages (analysts, risk reviewers) run concurrently where perspectives are independent. Sequential stages (debate chain, trade → risk) enforce data dependencies where each agent's output shapes the next.

Good output means every agent uses actual numbers from the market data, each thesis is specific and falsifiable, and the final trade has defined entry, stop, target, and size.

## On Activation

1. Validate that a ticker argument was provided. If missing, ask: "Which ticker? Usage: `/analyze AAPL`"
2. Confirm the ticker format looks valid (1-5 uppercase letters). If not, suggest corrections.
3. Announce: "Running full 13-agent trading desk analysis for {TICKER}. Five stages — expect 2-4 minutes."
4. Proceed to Stage 1.

## Error Handling

Stage 1 has explicit fail-fast behavior (see below). For Stages 2-4:

- **If one analyst fails (Stage 2):** Note the gap in downstream prompts ("Marco's macro analysis unavailable — proceed with remaining analyst perspectives"). Continue the pipeline.
- **If a debate agent fails (Stage 3):** Inform the user which perspective is missing. Offer to continue without it or retry.
- **If Rex fails (Stage 4a):** Halt — no trade proposal means the risk review has nothing to evaluate. Report the error.
- **If a risk analyst fails (Stage 4b):** Note the missing perspective for Hugo. Continue with available reviews.
- **If Hugo fails (Stage 4c):** Halt — the final gate is non-negotiable. Report the error.
- **If an MCP tool fails within a subagent:** The subagent should work with available data. Do not retry the full pipeline.

## Execution Flow

Follow these stages in exact order. Present each agent's response in full as you receive it.

### Stage 1: Prefetch Market Data

**Stage 1 of 5 — Fetching market data for {TICKER}**

Run the prefetch script to gather all market data:

```bash
cd {project-root} && python scripts/fetch_data.py <TICKER>
```

Capture the JSON output. If the script fails or returns an error, report it to the user and stop. Do not proceed with partial data.

Write the captured JSON to `{project-root}/.cache/analyze-{TICKER}.json` using the Write tool so subagents can read it directly instead of receiving it inline.

**Alpha chain check:** Use the Read tool to attempt reading `{project-root}/.cache/alpha-chain-{TICKER}.md`. If it exists, store its contents as `{alpha_chain_context}` — this analysis was triggered by an `/alpha` scan and Mr. A already identified edge signals. If the file does not exist, set `{alpha_chain_context}` to empty and proceed normally.

### Stage 2: Analyst Team (parallel)

**Stage 2 of 5 — Five analysts examining {TICKER} in parallel**

Spawn **all five agents in parallel** using the Agent tool. Each agent reads its own identity and capability files — do NOT read these files yourself.

**Prompt template for each analyst:**
```
Read your agent identity and instructions from these files:
- {project-root}/.claude/skills/agent-{name}/SKILL.md
- {project-root}/.claude/skills/agent-{name}/references/{capability}.md

Read market data from: {project-root}/.cache/analyze-{TICKER}.json

{if alpha_chain_context is not empty}
## Alpha Chain Context
Mr. A flagged {TICKER} as his top pick from today's alpha scan. This is the edge he identified — treat it as a prior signal and look for confirming or disconfirming evidence in your analysis:

{alpha_chain_context}
{endif}

## Your Task
Analyze {TICKER} according to your role and output format. Be specific — use the actual numbers from the market data. Keep your thesis under 300 words.
```

**Agent → capability file mapping:**

| Agent | Capability file |
|---|---|
| marco | `references/macro-analysis.md` |
| tara | `references/technical-analysis.md` |
| sage | `references/sentiment-analysis.md` |
| nadia | `references/news-catalyst-analysis.md` |
| frank | `references/fundamentals-analysis.md` |

**Model:** Use `haiku` for all five analysts.

**IMPORTANT for Sage:** Add to Sage's prompt: "You may use the WebSearch tool to find fresh social media sentiment for {TICKER} on Reddit and Twitter/X."

Present each analyst's response as it arrives, with their icon and name header.

### Stage 3: Research Debate (sequential)

**Stage 3 of 5 — Bull vs. Bear debate on {TICKER}**

**Step 3a: Spawn Blaine (Bull Case)**

```
Read your agent identity and instructions from:
- {project-root}/.claude/skills/agent-blaine/SKILL.md
- {project-root}/.claude/skills/agent-blaine/references/bull-case.md

Read market data from: {project-root}/.cache/analyze-{TICKER}.json

## Analyst Theses
{all 5 analyst outputs from Stage 2}

{if alpha_chain_context is not empty}
## Alpha Chain Context
Mr. A flagged {TICKER} as his top alpha pick. Treat this as prior signal — incorporate it into the bull case if the evidence supports it, or note if the analysts' findings don't confirm it:

{alpha_chain_context}
{endif}

## Your Task
Build the strongest possible bull case for {TICKER}. Draw from the analyst theses and market data. Follow your output format. Keep under 400 words.
```

Present Blaine's response. Then:

**Step 3b: Spawn Vera (Bear Case)**

```
Read your agent identity and instructions from:
- {project-root}/.claude/skills/agent-vera/SKILL.md
- {project-root}/.claude/skills/agent-vera/references/bear-case.md

Read market data from: {project-root}/.cache/analyze-{TICKER}.json

## Analyst Theses
{all 5 analyst outputs from Stage 2}

## Blaine's Bull Case
{Blaine's output from Step 3a}

{if alpha_chain_context is not empty}
## Alpha Chain Context
Mr. A flagged {TICKER} as his top alpha pick. Stress-test the claimed edge — if the signals he identified don't hold up under scrutiny, say so:

{alpha_chain_context}
{endif}

## Your Task
Build the strongest possible bear/avoid case for {TICKER}. Attack Blaine's weakest points. Draw from the analyst theses and market data. Follow your output format. Keep under 400 words.
```

Present Vera's response. Then:

**Step 3c: Spawn Jaya (Verdict)**

```
Read your agent identity and instructions from:
- {project-root}/.claude/skills/agent-jaya/SKILL.md
- {project-root}/.claude/skills/agent-jaya/references/research-verdict.md

## Blaine's Bull Case
{Blaine's output}

## Vera's Bear Case
{Vera's output}

## Analyst Theses (for reference)
{all 5 analyst outputs}

## Your Task
Judge the debate between Blaine and Vera. Declare a winner, set conviction, and follow your output format. Keep under 250 words.
```

Present Jaya's verdict.

### Stage 4: Trade & Risk (mixed)

**Stage 4 of 5 — Trade proposal and risk review for {TICKER}**

**Step 4a: Spawn Rex (Trade Proposal)**

```
Read your agent identity and instructions from:
- {project-root}/.claude/skills/agent-rex/SKILL.md
- {project-root}/.claude/skills/agent-rex/references/trade-proposal.md
- {project-root}/.claude/skills/agent-rex/references/options-strategy-menu.md

Read market data from: {project-root}/.cache/analyze-{TICKER}.json

## Jaya's Verdict
{Jaya's output from Stage 3}

## Analyst Theses
{all 5 analyst outputs}

{if alpha_chain_context is not empty}
## Alpha Chain Context
Mr. A's original edge thesis for {TICKER} — let this inform your trade structure and conviction if it survived the debate:

{alpha_chain_context}
{endif}

## Your Task
Propose a specific, executable trade for {TICKER} based on Jaya's verdict and the analyst theses. Follow your output format exactly — produce both an options structure and an equity alternative.
```

Present Rex's trade proposal. Then:

**Step 4b: Spawn Axel, Nina, Cass in parallel**

Each receives:
```
Read your agent identity and instructions from:
- {project-root}/.claude/skills/agent-{name}/SKILL.md
- {project-root}/.claude/skills/agent-{name}/references/{capability}.md

## Rex's Trade Proposal
{Rex's output from Step 4a}

## Your Task
Review Rex's trade proposal from your risk perspective. Follow your output format. Keep under 200 words.
```

**Agent → capability file mapping:**

| Agent | Capability file |
|---|---|
| axel | `references/aggressive-risk-review.md` |
| nina | `references/neutral-risk-review.md` |
| cass | `references/conservative-risk-review.md` |

**Model:** Use default model for all three.

Present each risk analyst's response. Then:

**Step 4c: Fetch portfolio state, then spawn Hugo (Final Gate)**

Before spawning Hugo, fetch current Alpaca positions so Hugo's portfolio-level risk checks have real data:

```bash
# Use Alpaca MCP: get_all_positions and get_account_info
```

Provide the portfolio snapshot to Hugo alongside the trade proposal and risk opinions.

```
Read your agent identity and instructions from:
- {project-root}/.claude/skills/agent-hugo/SKILL.md
- {project-root}/.claude/skills/agent-hugo/references/risk-review.md

## Current Portfolio
{Alpaca positions and account info from the fetch above — if Alpaca is unreachable, note "Portfolio data unavailable" and proceed}

## Rex's Trade Proposal
{Rex's output}

## Risk Team Opinions
{Axel's output}
{Nina's output}
{Cass's output}

## Your Task
Render your final risk-adjusted recommendation. Check the proposed trade against the current portfolio for concentration risk, correlation, and buying power. Follow your output format. Present TWO executable trades: an options trade and an equity trade (or explain why one doesn't apply). End by asking the user: "Execute? (yes/no — or specify which trade)" Keep under 350 words.
```

Present Hugo's final recommendation.

### Stage 5: Execution & Conversation Mode

**Stage 5 of 5 — Execution decision for {TICKER}**

Follow the execution protocol defined in `{project-root}/.claude/skills/agent-hugo/references/execution-protocol.md` for both trade execution and Obsidian logging. That file is the single source of truth for order placement, error handling, and journal format.

**If the user says yes (or specifies which trade):** Execute per the protocol, report order confirmations, then log to Obsidian.

**If the user says no:** Tell the user: "Standing down. Address any agent by name for follow-ups — e.g., 'Vera, what changes your mind?' or 'Rex, what about a put spread instead?'"

**Always log** — even for declined, avoided, or rejected outcomes. The journal tracks decisions, not just trades.

For follow-up conversations: have the subagent read the relevant agent skill files and include the full analysis context so the agent stays in character.

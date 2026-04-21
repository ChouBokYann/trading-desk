---
name: analyze
description: Run a full multi-agent trading desk analysis for a ticker. Usage: /analyze AAPL
---

# Trading Desk Analysis

Run a full 13-agent analysis for the given ticker.

## Arguments

The first argument is the ticker symbol (required). Example: `/analyze AAPL`

## Execution Flow

Follow these stages in exact order. Present each agent's response in full as you receive it.

### Stage 1: Prefetch Market Data

Run the prefetch script to gather all market data:

```bash
cd {project-root} && python scripts/fetch_data.py <TICKER>
```

Capture the JSON output. If the script fails or returns an error, report it to the user and stop. Do not proceed with partial data.

Store the full JSON output as `MARKET_DATA` — every agent will receive this.

### Stage 2: Analyst Team (parallel)

Read all five analyst persona files from `{project-root}/personas/`:
- `marco.md` (Market Analyst)
- `tara.md` (Technical Analyst)
- `sage.md` (Social Media Analyst)
- `nadia.md` (News Analyst)
- `frank.md` (Fundamentals Analyst)

Spawn **all five agents in parallel** using the Agent tool. Each agent receives:

**Prompt template for each analyst:**
```
{contents of their persona .md file}

## Market Data for {TICKER}
{MARKET_DATA JSON blob}

## Your Task
Analyze {TICKER} according to your role and output format. Be specific — use the actual numbers from the market data. Keep your thesis under 300 words.
```

**Model:** Use `haiku` for all five analysts.

**IMPORTANT for Sage:** Add this to Sage's prompt: "You may use the WebSearch tool to find fresh social media sentiment for {TICKER} on Reddit and Twitter/X. Search for recent posts and gauge the retail sentiment."

Present each analyst's response as it arrives, with their icon and name header.

### Stage 3: Research Debate (sequential)

Read the research persona files:
- `blaine.md` (Bull Researcher)
- `vera.md` (Bear Researcher)
- `jaya.md` (Research Judge)

**Step 3a: Spawn Blaine**

```
{contents of blaine.md}

## Market Data for {TICKER}
{MARKET_DATA JSON blob}

## Analyst Theses
{all 5 analyst outputs from Stage 2}

## Your Task
Build the strongest possible bull case for {TICKER}. Draw from the analyst theses and market data. Follow your output format. Keep under 400 words.
```

Present Blaine's response. Then:

**Step 3b: Spawn Vera**

```
{contents of vera.md}

## Market Data for {TICKER}
{MARKET_DATA JSON blob}

## Analyst Theses
{all 5 analyst outputs from Stage 2}

## Blaine's Bull Case
{Blaine's output from Step 3a}

## Your Task
Build the strongest possible bear/avoid case for {TICKER}. Attack Blaine's weakest points. Draw from the analyst theses and market data. Follow your output format. Keep under 400 words.
```

Present Vera's response. Then:

**Step 3c: Spawn Jaya**

```
{contents of jaya.md}

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

Read the trade and risk persona files:
- `rex.md` (Trader)
- `axel.md` (Aggressive Risk)
- `nina.md` (Neutral Risk)
- `cass.md` (Conservative Risk)
- `hugo.md` (Risk Manager)

**Step 4a: Spawn Rex**

```
{contents of rex.md}

## Market Data for {TICKER}
{MARKET_DATA JSON blob}

## Jaya's Verdict
{Jaya's output from Stage 3}

## Analyst Theses
{all 5 analyst outputs}

## Your Task
Propose a specific, executable trade for {TICKER} based on Jaya's verdict and the analyst theses. If Jaya's conviction is below 4/10, recommend avoiding the trade. Follow your output format exactly.
```

Present Rex's trade proposal. Then:

**Step 4b: Spawn Axel, Nina, Cass in parallel**

Each receives:
```
{contents of their persona .md file}

## Rex's Trade Proposal
{Rex's output from Step 4a}

## Your Task
Review Rex's trade proposal from your risk perspective. Follow your output format. Keep under 200 words.
```

**Model:** Use default model for all three.

Present each risk analyst's response. Then:

**Step 4c: Spawn Hugo**

```
{contents of hugo.md}

## Rex's Trade Proposal
{Rex's output}

## Risk Team Opinions
{Axel's output}
{Nina's output}
{Cass's output}

## Your Task
Render your final risk-adjusted recommendation. Follow your output format. Keep under 250 words.
```

Present Hugo's final recommendation.

### Stage 5: Conversation Mode

After Hugo's recommendation, tell the user:

"Analysis complete. Address any agent by name for follow-ups — e.g., 'Vera, what changes your mind?' or 'Rex, what about a put spread instead?'"

For follow-up conversations: read the relevant persona file and include the full analysis context so the agent stays in character.

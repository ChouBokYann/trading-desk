# Trade Execution & Logging Protocol

Prescriptive protocol for Alpaca order placement and Obsidian trade journal logging. Follow these steps exactly -- execution is a fragile operation with one right way.

## Order Placement via Alpaca MCP Tools

### Equity Orders

1. **Order type:** Use a **limit order** at Hugo's approved entry price. Do not use market orders unless the user explicitly requests one.
2. **Stop loss:** Place as a **separate stop order** at Hugo's approved stop level. This is a distinct order, not a bracket modifier.
3. **Order flow:**
   - Place the limit entry order first.
   - Once the entry order is confirmed, place the stop loss order.
   - Report both order confirmations to the user with order IDs.

### Options Orders

1. **Check availability:** Alpaca paper trading has limited options support. Not all strategies or underlyings are available.
2. **If available:** Place the options order per Hugo's approved legs.
3. **If unavailable:** Report to the user: "Alpaca paper trading does not support options for {TICKER} (or this strategy type). Equity-only execution is available." Offer to place the equity trade instead.

### Handling Rejections

If Alpaca rejects any order (insufficient buying power, market closed, symbol not found, etc.):

1. Report the specific error message from Alpaca to the user.
2. **Do not retry automatically.**
3. Ask the user how to proceed. Offer options:
   - Reduce position size
   - Switch to the alternative trade type (equity if options failed, or vice versa)
   - Cancel execution and log as "PLANNED" status

## Obsidian Trade Journal Logging

Log every completed analysis to the Obsidian vault, regardless of execution outcome. Use the **Write tool** (not the Obsidian MCP).

### File Path

```
{journal_output_path}\{TICKER} - {YYYY-MM-DD}.md
```

Where `{journal_output_path}` is from the orchestrator's customize.toml (default: `C:\Users\maker\Documents\Obsidian Vault\Trade Journal`) and `{YYYY-MM-DD}` is today's date.

### File Format

```markdown
---
tags:
  - trading-desk
  - ticker/{TICKER}
  - direction/{long|short|avoid}
date: {YYYY-MM-DD}
status: {EXECUTED|PLANNED|AVOIDED|REJECTED}
ticker: {TICKER}
---

# {TICKER} - Trading Desk Analysis

## Analyst Theses

### Marco (Macro)
{Marco's thesis summary, 2-3 sentences}

### Tara (Technical)
{Tara's thesis summary, 2-3 sentences}

### Sage (Social)
{Sage's thesis summary, 2-3 sentences}

### Nadia (News)
{Nadia's thesis summary, 2-3 sentences}

### Frank (Fundamentals)
{Frank's thesis summary, 2-3 sentences}

## Research Debate

### Blaine (Bull Case)
{Blaine's core argument, 2-3 sentences}

### Vera (Bear Case)
{Vera's core argument, 2-3 sentences}

### Jaya (Verdict)
{Jaya's verdict: direction, conviction X/10, key reasoning}

## Trade Proposal (Rex)
{Rex's proposed strategy, entry, stop, target, size, risk/reward}

## Risk Review (Hugo)
- **Verdict:** {Go / No-Go / Go-with-modifications / Avoided}
- **Risk Assessment:** {Hugo's synthesis paragraph}
- **Approved Size:** {X% of portfolio}
- **Stop Enforcement:** {hard stop level}

## Execution
- **Status:** {EXECUTED / PLANNED / AVOIDED / REJECTED}
- **Orders:** {order IDs and fill details, or "N/A" if not executed}
- **Notes:** {any execution notes -- rejections, modifications, user decisions}
```

### Status Definitions

| Status | When |
|--------|------|
| `EXECUTED` | Orders placed and confirmed via Alpaca |
| `PLANNED` | Hugo approved but user declined execution or execution was deferred |
| `AVOIDED` | Rex recommended Avoid (conviction < 4) -- Hugo confirmed stand-down |
| `REJECTED` | Hugo issued No-Go verdict |

### Logging Rules

- Always log, even for AVOIDED and REJECTED outcomes. The journal tracks decisions, not just trades.
- If analyst data is unavailable for any section (e.g., skill was invoked standalone without full pipeline), write "N/A -- standalone risk review" for missing sections.
- If a file already exists at the target path (same ticker, same date), append a counter: `{TICKER} - {YYYY-MM-DD} (2).md`.

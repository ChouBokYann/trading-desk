# Wiki, Quant Layer & Obsidian Integration

After the post-mortem analysis is complete, update all knowledge stores. A single review may touch 5-15 wiki pages.

## 1. Raw Trade Log (Immutable)

Write the closed trade record to `{project-root}/_bmad/memory/tm/raw/trade-logs/{date}-{ticker}-close.md`:

```yaml
---
title: "{ticker} {direction} — Closed {date}"
type: trade-close
entry_date: YYYY-MM-DD
exit_date: YYYY-MM-DD
ticker: AAPL
direction: long
entry_price: 195.50
exit_price: 210.00
shares: 45
r_multiple: 1.75
hold_days: 8
outcome: win | loss | breakeven
causal_factors: [macro-policy, earnings]
attribution_confidence: high | medium | low
---

[Full post-mortem narrative with evidence chain]
```

This file is immutable once written. It serves as a raw source for future wiki synthesis.

## 2. Wiki Page Updates

Update relevant wiki pages with new evidence from this trade. Read each page first, then append or revise the relevant sections.

**Pages to check and potentially update:**

- **Ticker page** (`wiki/tickers/{ticker}.md`) -- Update trade history, key levels that held or broke, evolving thesis. Create if it doesn't exist.
- **Strategy page** (`wiki/strategies/{strategy}.md`) -- Update with outcome data: did this setup type deliver? Note any execution lessons.
- **Regime page** (`wiki/regimes/{current-regime}.md`) -- If the trade outcome was regime-dependent, add evidence to the regime playbook.
- **Causal factor pages** (`wiki/causal-factors/{factor}.md`) -- For each tagged causal factor, update or create the factor page with this trade as evidence. Build the causal pattern over time.
- **Post-mortem page** (`wiki/post-mortems/{date}-{ticker}.md`) -- The full post-mortem synthesis, cross-referenced to all related pages.

**Wiki page updates follow frontmatter conventions:**

```yaml
---
title: Page Title
type: ticker | strategy | regime | causal-factor | post-mortem
sources: [raw/trade-logs/...]
related: ["[[other-page]]"]
causal_factors: [factor-tags]
created: YYYY-MM-DD
updated: YYYY-MM-DD
confidence: high | medium | low
---
```

Update the `updated` date and add new source references when modifying existing pages.

## 3. Quant Layer Update

Update `tm-signals.db` with the trade outcome. The trade was inserted at deploy time with status `open` -- now update it to `closed`:

```sql
UPDATE trades SET
  exit_price = {exit_price},
  exit_date = '{exit_date}',
  r_multiple = {r_multiple},
  hold_days = {hold_days},
  outcome = '{win|loss|breakeven}',
  mfe = {max_favorable_excursion},
  mae = {max_adverse_excursion},
  causal_factors = '{json_array}',
  status = 'closed'
WHERE ticker = '{ticker}' AND status = 'open'
```

## 4. Wiki Log

Append to `{project-root}/_bmad/memory/tm/wiki/log.md`:

```
[{date}] REVIEW: {ticker} {direction} closed — {outcome} {r_multiple}R. Hold: {days}d. Cause: {primary_factor}. Pages updated: {count}.
```

## 5. Obsidian Trade Journal

Write a narrative journal entry directly to disk (do NOT use Obsidian MCP):

**Path:** `C:\Users\maker\Documents\Obsidian Vault\Trade Journal\{TICKER} - {exit_date}.md`

**Content:** A readable narrative covering:
- Trade summary (ticker, direction, dates, P&L)
- What went right / what went wrong
- Causal attribution in plain language
- Lessons learned
- Links to relevant wiki pages for deeper context

Keep it personal and useful for future review -- this is the human-readable version of the post-mortem, not a data dump.

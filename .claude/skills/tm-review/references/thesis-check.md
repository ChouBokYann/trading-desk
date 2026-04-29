# Live Thesis Check

Evaluate open positions for thesis integrity. The goal is to catch weakening or broken theses BEFORE the stop is hit -- the earlier you detect a broken thesis, the more capital you preserve.

## Process

For each open position (or a specific ticker if provided):

### 1. Reconstruct the Original Thesis

Read the entry trade log from `{project-root}/_bmad/memory/tm/raw/trade-logs/{date}-{ticker}-entry.md`. Extract:

- The original thesis statement
- Key catalysts the thesis depended on
- Risk factors identified at entry
- Expected timeline

### 2. Assess Current State

Gather current data:

- **Price action**: Current price vs. entry, distance to stop, distance to targets. Via `yahoo-finance:get_stock_info`.
- **News/catalysts**: Has the expected catalyst occurred? Has a risk factor materialized? Via `opennews:search_news` and `yahoo-finance:get_yahoo_finance_news`.
- **Technical health**: Is the stock still behaving consistently with the thesis? Key levels holding? Via `financekit:technical_analysis`.
- **Regime**: Has the regime changed since entry? Load current regime state.

### 3. Classify Thesis Status

| Status | Criteria | Action |
|--------|----------|--------|
| **Intact** | Original catalysts on track, price action consistent, no new risk factors | Hold. Extend decay window if approaching expiry. |
| **Weakening** | Some signals fading but thesis not invalidated. Catalyst delayed, momentum slowing, sector rotating. | Reduce by 50%. Tighten stop. Set shorter review window. |
| **Broken** | Catalyst failed, fundamental change, thesis invalidated by new information. | Exit 100% regardless of P&L. Don't wait for the stop. |

### 4. Present the Assessment

For each position reviewed:

```
THESIS CHECK: {TICKER}
Status:     INTACT / WEAKENING / BROKEN
Entry:      ${entry} on {date} ({days} trading days ago)
Current:    ${current} ({pnl_pct}%)
Stop:       ${stop} ({distance_pct}% away)

Original Thesis: {thesis statement}

Evidence:
  [+] {supporting evidence}
  [-] {contrary evidence}
  [?] {uncertain/pending}

Recommendation: HOLD / REDUCE 50% / EXIT
Rationale: {one sentence}
```

If any position is classified as **Broken**, strongly recommend immediate exit and explain why waiting for the stop is suboptimal -- a broken thesis means the stop level itself may no longer be meaningful.

## Batch Mode

When invoked without a specific ticker, run the thesis check across ALL open positions. Sort results by urgency: Broken first, then Weakening, then Intact. This gives the user a prioritized action list.

# Pattern Extraction

## Regime Pattern Extraction

Find regime insights from accumulated regime snapshots and trade outcomes.

**Data:**
- All regime snapshots from `{project-root}/_bmad/memory/tm/raw/regime-snapshots/`
- All closed trades from `tm-signals.db` with their regime_flag at entry

**Analysis:**
- Win rate by regime flag (green/yellow/red)
- Average R by regime
- Which strategies work best in each regime
- Regime transition patterns: what typically happens after a flag change
- False signals: regime flags that changed but reverted quickly

**Output:** Update regime wiki pages (`wiki/regimes/*.md`) with new evidence. If a new regime pattern emerges that doesn't match existing playbooks, create a new page.

This is where regime memory compounds -- the first yield curve inversion is textbook, but the third inversion has battle-tested notes from the previous two.

## Cross-Trade Causality

Find macro patterns across batches of recent post-mortems that are invisible at the individual trade level.

**Data:**
- Recent post-mortem pages from `wiki/post-mortems/`
- Causal factor tags from closed trades in `tm-signals.db`

**Analysis:**
- Factor frequency: which causal factors appear most often in recent trades?
- Factor clustering: are multiple trades being affected by the same factor simultaneously?
- Factor → outcome correlation: do certain factors reliably predict wins or losses?
- Emerging factors: new causal patterns not yet in the taxonomy

**The pattern to catch:** "3 of our last 5 stops were hit during the same tariff escalation week" is invisible at the individual trade level. Synthesis sees the cluster.

**Output:** Update or create causal factor pages (`wiki/causal-factors/*.md`). If a new factor emerges, add it to the taxonomy.

Append to `wiki/log.md`:
```
[{date}] SYNTHESIS: Pattern extraction — {patterns_found} new patterns. Top factor: {factor} ({count} trades affected).
```

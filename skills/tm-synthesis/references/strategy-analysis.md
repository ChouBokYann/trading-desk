# Strategy Analysis

## Strategy EV Update

Recalculate expected value per setup type from the full quant layer history.

Run the stats script for the full history:

```
python scripts/strategy_stats.py {project-root}/_bmad/memory/tm/tm-signals.db
```

The script outputs per-strategy: trade count, win rate, avg win R, avg loss R, expected value, Sharpe ratio, max drawdown, and current streak.

For each strategy, update the wiki strategy page (`wiki/strategies/{strategy}.md`):

- Current EV with confidence interval (need 30+ trades for meaningful stats, 100+ for high confidence)
- Win rate trend (improving, stable, declining)
- Average hold time
- Best/worst regime performance
- Any parameter drift from the original spec

**The 100-trade proof requirement:** New strategies must show positive EV over 100 paper trades before being allocated real capital. Track progress toward this threshold.

## Source Weight Recalibration

Track which signal sources are actually predictive over rolling windows.

Query the quant layer for signal source accuracy:

```sql
SELECT signal_source, 
       COUNT(*) as total,
       SUM(CASE WHEN outcome = 'win' THEN 1 ELSE 0 END) as wins,
       AVG(r_multiple) as avg_r
FROM trades 
WHERE status = 'closed'
GROUP BY signal_source
```

**Source hierarchy update:**
- Rank sources by accuracy (win rate) and quality (avg R when correct)
- Compare against the current hierarchy in `wiki/overview.md`
- If a source has significantly outperformed or underperformed expectations, update the conviction tier defaults
- Write updated weights to the relevant wiki strategy pages

**Signal categories to track:**
- Desk `/analyze` pipeline
- Alpha chain picks
- Manual entries
- Insider filings (via edgartools)
- Options flow
- Technical breakouts
- Fundamental catalysts

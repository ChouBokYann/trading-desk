# Weekly Digest

Performance summary with pattern highlights. Catches patterns like "3 of 5 stops hit during the same tariff week" that no single trade review surfaces.

## Data Gathering

1. **Quant layer** -- Query `tm-signals.db` for all trades in the last 7 calendar days (entries, exits, status changes):
   ```sql
   SELECT * FROM trades WHERE entry_date >= date('now', '-7 days') OR exit_date >= date('now', '-7 days')
   ```

2. **Compute statistics** -- Run the strategy stats script for the rolling window:
   ```
   python scripts/strategy_stats.py {project-root}/_bmad/memory/tm/tm-signals.db --days 7
   ```

3. **Wiki log** -- Read recent entries from `{project-root}/_bmad/memory/tm/wiki/log.md` for activity context.

4. **Regime history** -- Read regime snapshots from the past week in `{project-root}/_bmad/memory/tm/raw/regime-snapshots/`.

5. **Portfolio state** -- Current positions via `alpaca:get_all_positions` and `alpaca:get_portfolio_history`.

## Analysis

Synthesize the data into:

- **Performance summary**: trades opened, closed, win rate, total R, avg R per trade
- **Strategy breakdown**: which setup types performed, which didn't
- **Regime context**: was the regime stable or shifting? How did it affect outcomes?
- **Pattern highlights**: any recurring causal factors across multiple trades? Any surprising correlations?
- **Position health**: open positions approaching decay window, stops nearing trigger, thesis status
- **Action items**: specific things to do this week based on the analysis

## Output

1. **HTML report** -- Generate via `tm-dashboard` style or write directly to `{project-root}/_bmad-output/weekly-digest-{date}.html`. Include charts if data supports it.

2. **Wiki update** -- Update `{project-root}/_bmad/memory/tm/wiki/overview.md` with the current state synthesis. This is what The Quant reads on activation.

3. **Wiki log** -- Append:
   ```
   [{date}] SYNTHESIS: Weekly digest — {trades_closed} trades closed, {win_rate}% win rate, {total_r}R total. Patterns: {highlights}.
   ```

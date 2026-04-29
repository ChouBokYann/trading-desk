# Dashboard Data Gathering

Gather all data before passing to the HTML generator. Structure everything as a single JSON object.

## Data Sources

### Portfolio (required)

Source: `alpaca:get_all_positions` + `alpaca:get_account_info`

```json
{
  "portfolio": {
    "account_value": 100000.00,
    "cash": 35000.00,
    "buying_power": 70000.00,
    "positions": [
      {
        "ticker": "AAPL",
        "shares": 45,
        "avg_entry": 195.50,
        "current_price": 200.00,
        "market_value": 9000.00,
        "unrealized_pnl": 202.50,
        "unrealized_pnl_pct": 2.30,
        "side": "long"
      }
    ]
  }
}
```

### Risk Data (required)

Source: `tm-signals.db` for stop levels and entry data, Alpaca for current prices

For each position, compute:
- Distance to stop (% and $)
- Current R-multiple (unrealized)
- Portfolio heat contribution (% of portfolio at risk)
- Days in trade

Aggregate:
- Total portfolio heat vs. limit
- Current drawdown from equity peak
- Cash reserve % vs. minimum

### Regime (required)

Source: Most recent regime snapshot from `{project-root}/_bmad/memory/tm/raw/regime-snapshots/` or invoke `tm-regime` if stale

```json
{
  "regime": {
    "macro": "bull",
    "flag": "green",
    "vix": 16.5,
    "distribution_days": 2,
    "safety_car": false,
    "implications": {
      "max_position_size": "full",
      "new_entries": "allowed",
      "recommended_cash": "20%"
    }
  }
}
```

### Greeks (if options positions exist)

Source: `financekit:options_chain` for Greeks data on option positions from Alpaca

Per position: delta, gamma, theta, vega, DTE
Portfolio level: net delta, total theta/day, weighted DTE

### Correlation (if 2+ positions)

Source: `financekit:correlation_matrix` or `financekit:compare_assets`

Pairwise correlation between all open position tickers. Flag any pair >0.8 as TCAS warning.

### Performance History

Source: `alpaca:get_portfolio_history` for equity curve, `tm-signals.db` for per-strategy P&L

- Equity curve data points (last 30/60/90 days)
- Per-strategy cumulative P&L
- Rolling Sharpe if sufficient data

### Strategy Allocation

Source: `tm-signals.db` for strategy tags per position

- Current allocation by strategy (momentum, options income, tail hedge)
- Target allocation from wiki config
- Drift from target

### Watchlist (optional)

Source: Watchlist entries from wiki or user config, current market data

For each watchlist stock: current price, distance to trigger, which checklist gates are already cleared.

### Confirmation Queue (optional)

Source: Pending Tier B orders (if any exist in the deploy queue)

Order details, time remaining on veto window.

## Output Schema

Combine all gathered data into a single JSON object and pipe to stdin of the generator script. The script handles missing sections gracefully -- omitted keys simply hide that dashboard panel.

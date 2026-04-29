# Stage 2: Configuration

Collect user preferences and validate external dependencies. Write config to `{project-root}/_bmad/config.yaml` under the `tm` section.

## Config Collection

Collect these values interactively. Present defaults and let the user accept or override. Group related settings and move efficiently — don't belabor each one.

| Variable | Prompt | Default |
|----------|--------|---------|
| `risk_per_trade` | Maximum risk per trade (% of portfolio) | `2%` |
| `max_portfolio_heat` | Maximum total portfolio heat (% at risk across all positions) | `8%` |
| `min_cash_reserve` | Minimum cash reserve (% of portfolio to keep liquid) | `30%` |
| `default_autonomy` | Default autonomy tier: A (full-auto), B (auto + 30min confirm), C (human approval) | `C` |
| `alpaca_mode` | Trading mode: paper or live | `paper` |
| `obsidian_path` | Path to Obsidian vault for trade journal (leave empty to skip) | `""` |
| `digest_day` | Day of week for weekly synthesis digest | `Sunday` |
| `max_positions` | Maximum concurrent open positions | `8` |
| `strategies` | Enabled strategies (comma-separated: momentum, premium-selling, tail-hedge) | `momentum` |

Write the collected values to the `tm` section of `{project-root}/_bmad/config.yaml`. If the file or section already exists, merge without overwriting other sections.

## Dependency Validation

Check each external dependency and report status. Required dependencies must pass; optional ones are noted.

**Required MCP servers** — test each by making a simple call:

| Server | Test | Required by |
|--------|------|-------------|
| **alpaca** | Fetch account info (paper mode) | tm-deploy, tm-dashboard |
| **yahoo-finance** | Fetch a quote for SPY | tm-deploy, tm-regime, tm-review |
| **financekit** | Fetch technical analysis for SPY | tm-regime, tm-dashboard |
| **fred** | Fetch 10Y Treasury rate | tm-regime |

**Optional MCP servers:**

| Server | Test | Enhances |
|--------|------|----------|
| **edgartools** | Search for a company | tm-review (causal attribution) |
| **opennews** | Fetch latest news | tm-review (causal attribution) |

**Other dependencies:**

| Dependency | Check | Required by |
|------------|-------|-------------|
| `sqlite3` CLI | Run `sqlite3 --version` | tm-signals.db queries |
| `python3` 3.10+ | Run `python3 --version` | Daemon (future), scripts |

For each dependency, report: connected/available, version if applicable, or what's missing and how to fix it. Do not block setup on optional dependencies — note them as enhancement opportunities.

If Alpaca paper trading keys are not configured (no `.env` or keys missing), guide the user: they need `APCA_API_KEY_ID` and `APCA_API_SECRET_KEY` in `.env` with `APCA_API_BASE_URL=https://paper-api.alpaca.markets`.

## Completion

Present a status summary table: all config values set, all required deps green/red, optional deps noted. Proceed to Stage 3 (Onboarding).

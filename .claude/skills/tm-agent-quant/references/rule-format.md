# Rule Format

Specification for daemon-executable rule files. The Quant writes these; the Python daemon reads and enforces them.

## File Location

Rules live at `{project-root}/daemon/config/rules.yaml`. The daemon reloads on file change.

## Structure

```yaml
version: 1
updated: "2026-04-25T10:00:00Z"
updated_by: "the-quant"

regime_rules:
  green:
    max_position_risk: 0.02
    max_portfolio_heat: 0.08
    min_cash_reserve: 0.20
    new_entries: "allowed"
    stop_width: "2.0_ATR"
  yellow:
    max_position_risk: 0.01
    max_portfolio_heat: 0.06
    min_cash_reserve: 0.30
    new_entries: "tier1_only"
    stop_width: "1.5_ATR"
  red:
    max_position_risk: 0
    max_portfolio_heat: 0.04
    min_cash_reserve: 0.40
    new_entries: "halted"
    stop_width: "1.0_ATR"
  black:
    new_entries: "halted"
    action: "force_review"
    min_cash_reserve: 0.60

strategies:
  - name: "momentum-breakout"
    enabled: true
    entry_conditions:
      - "rs_rank >= 80"
      - "base_weeks >= 5"
      - "volume_ratio >= 1.5"
      - "regime_flag in [green, yellow]"
    exit_conditions:
      hard_stop: "entry - 2.0 * ATR(14)"
      thesis_invalidation:
        - "rs_rank < 50"
        - "volume_dry_up: avg_volume_5d < 0.5 * avg_volume_50d"
      decay_timer_days: 12
      targets:
        - multiplier: 2.0
          action: "sell_50pct"
        - multiplier: 3.0
          action: "trail_stop"

conviction_tiers:
  tier_1:
    conditions: "all regime layers aligned AND strategy EV > 1.5R"
    risk_pct: 0.02
  tier_2:
    conditions: "strong setup, some signals mixed"
    risk_pct: 0.01
  tier_3:
    conditions: "speculative, thesis forming"
    risk_pct: 0.0025

abort_criteria:
  monthly_drawdown_halt: 0.08
  consecutive_stops_reduce: 4
  size_reduction_factor: 0.50
  halt_duration_days: 5

source_weights:
  insider_filings: 1.0
  institutional_13f: 0.8
  technical_breakout: 0.7
  options_flow: 0.5
  social_sentiment: 0.3
```

## Rules for Writing Rules

- Every condition must be evaluable from data the daemon can access (price, volume, indicators, portfolio state)
- No ambiguous language — "strong momentum" fails, "rs_rank >= 80" passes
- Include the `updated` timestamp and `updated_by` field on every change
- When updating, preserve the existing structure — modify values, don't restructure
- After writing, update the relevant wiki strategy page with the reasoning for the change

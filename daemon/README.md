# The Money — Execution Daemon

The Money execution daemon. Reads rules from The Quant, executes via Alpaca.

This is the "constitution" layer — deterministic enforcement of AI-generated rules. The Quant writes strategy rules in YAML; this daemon reads them, monitors positions, and routes orders. It does not make discretionary decisions.

## Usage

```bash
pip install -r requirements.txt
python src/main.py
```

## Architecture

- `config/rules.yaml` — Strategy rules authored by The Quant
- `src/config_loader.py` — Parses and validates rules.yaml
- `src/state_machine.py` — Tracks position lifecycle states
- `src/risk_monitor.py` — Enforces portfolio heat and per-trade risk limits
- `src/order_router.py` — Alpaca order execution with retry logic
- `src/position_manager.py` — Trailing stops, pyramid entries, partial exits
- `src/main.py` — Entry point: cron scheduler + streaming event loop

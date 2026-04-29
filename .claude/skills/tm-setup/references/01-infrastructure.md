# Stage 1: Infrastructure

Scaffold the three foundational systems The Money depends on: the LLM wiki, the quantitative signal database, and the Python daemon project.

## Wiki Scaffold

Create the full wiki directory tree at `{project-root}/_bmad/memory/tm/`:

```
_bmad/memory/tm/
├── wiki/
│   ├── index.md
│   ├── log.md
│   ├── overview.md
│   ├── regimes/
│   ├── strategies/
│   ├── sectors/
│   ├── causal-factors/
│   ├── tickers/
│   └── post-mortems/
├── raw/
│   ├── trade-logs/
│   ├── macro-events/
│   ├── earnings/
│   └── regime-snapshots/
└── schema.md
```

Write initial files:

**`wiki/index.md`** — Empty catalog with section headers (Regimes, Strategies, Sectors, Causal Factors, Tickers, Post-Mortems). No entries yet.

**`wiki/log.md`** — Header only: `# The Money — Activity Log` with a note that entries are append-only and timestamped.

**`wiki/overview.md`** — Placeholder noting that the onboarding stage will populate this with the user's risk profile and trading goals.

**`schema.md`** — Copy from `assets/wiki-schema.md`. This defines the wiki conventions, page frontmatter format, causal factor taxonomy, and confidence levels.

If any wiki directories already exist, skip creation and report what was preserved.

## Quantitative Signal Database

Initialize the SQLite database for signal history and performance tracking.

Run: `python3 scripts/init_db.py {project-root}/_bmad/memory/tm/tm-signals.db`

If the database already exists, the script detects it and reports existing tables without modifying data. Run `python3 scripts/init_db.py --help` for details.

## Daemon Project Scaffold

Create the Python execution daemon project structure at `{project-root}/daemon/`:

```
daemon/
├── README.md
├── requirements.txt
├── config/
│   └── rules.yaml
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── config_loader.py
│   ├── order_router.py
│   ├── position_manager.py
│   ├── risk_monitor.py
│   └── state_machine.py
└── tests/
    └── __init__.py
```

**`README.md`** — Brief description: "The Money execution daemon. Reads rules from The Quant, executes via Alpaca. This is the 'constitution' layer — deterministic enforcement of AI-generated rules."

**`requirements.txt`** — `alpaca-py`, `pyyaml`, `sqlite3` (stdlib note).

**`config/rules.yaml`** — Empty rules template with commented structure showing where The Quant writes strategy rules.

**`src/main.py`** — Skeleton entry point with TODO comments marking where streaming, cron scheduling, and signal processing will be implemented.

**Other `src/` files** — Minimal stubs with docstrings describing their purpose. No implementation yet — these are scaffolds for future development.

If the daemon directory already exists, skip and report what was preserved.

## Completion

Report what was created/preserved. Proceed to Stage 2 (Configuration).

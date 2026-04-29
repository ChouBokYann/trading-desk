#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Initialize The Money quantitative signal database (SQLite).

Creates the tm-signals.db database with tables for trade history,
signal tracking, strategy performance, regime state, and source accuracy.
Safe to run on existing databases — detects and reports existing tables.
"""

import argparse
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = {
    "trades": """
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL,
            direction TEXT NOT NULL CHECK(direction IN ('long', 'short')),
            strategy TEXT NOT NULL,
            conviction_tier INTEGER NOT NULL CHECK(conviction_tier IN (1, 2, 3)),
            entry_date TEXT NOT NULL,
            entry_price REAL NOT NULL,
            position_size INTEGER NOT NULL,
            risk_per_share REAL NOT NULL,
            stop_price REAL NOT NULL,
            target_1 REAL,
            target_2 REAL,
            exit_date TEXT,
            exit_price REAL,
            exit_reason TEXT,
            r_multiple REAL,
            pnl_dollars REAL,
            pnl_percent REAL,
            hold_days INTEGER,
            causal_factors TEXT,
            thesis TEXT,
            notes TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """,
    "signals": """
        CREATE TABLE IF NOT EXISTS signals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL,
            source TEXT NOT NULL,
            direction TEXT NOT NULL CHECK(direction IN ('long', 'short', 'neutral')),
            conviction REAL NOT NULL CHECK(conviction BETWEEN 0 AND 1),
            signal_date TEXT NOT NULL,
            acted_on INTEGER NOT NULL DEFAULT 0,
            trade_id INTEGER REFERENCES trades(id),
            outcome TEXT,
            raw_signal TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """,
    "strategies": """
        CREATE TABLE IF NOT EXISTS strategies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            enabled INTEGER NOT NULL DEFAULT 1,
            trade_count INTEGER NOT NULL DEFAULT 0,
            win_count INTEGER NOT NULL DEFAULT 0,
            loss_count INTEGER NOT NULL DEFAULT 0,
            avg_win_r REAL,
            avg_loss_r REAL,
            expected_value REAL,
            sharpe_30d REAL,
            sharpe_60d REAL,
            sharpe_90d REAL,
            loss_ratio REAL,
            capital_allocation REAL NOT NULL DEFAULT 0,
            last_trade_date TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """,
    "regime_history": """
        CREATE TABLE IF NOT EXISTS regime_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            assessment_date TEXT NOT NULL,
            macro_regime TEXT NOT NULL CHECK(macro_regime IN ('bull', 'bear', 'sideways')),
            macro_confidence REAL,
            sector_data TEXT,
            distribution_days INTEGER,
            r0_data TEXT,
            vix REAL,
            yield_curve_spread REAL,
            breadth_score REAL,
            flag_level TEXT CHECK(flag_level IN ('green', 'yellow', 'red', 'black')),
            safety_car INTEGER NOT NULL DEFAULT 0,
            notes TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """,
    "source_accuracy": """
        CREATE TABLE IF NOT EXISTS source_accuracy (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_name TEXT NOT NULL,
            signal_count INTEGER NOT NULL DEFAULT 0,
            correct_count INTEGER NOT NULL DEFAULT 0,
            accuracy_30d REAL,
            accuracy_90d REAL,
            accuracy_all REAL,
            weight REAL NOT NULL DEFAULT 1.0,
            last_signal_date TEXT,
            updated_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """,
    "portfolio_snapshots": """
        CREATE TABLE IF NOT EXISTS portfolio_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            snapshot_date TEXT NOT NULL,
            total_value REAL NOT NULL,
            cash REAL NOT NULL,
            positions_value REAL NOT NULL,
            portfolio_heat REAL NOT NULL,
            open_positions INTEGER NOT NULL,
            daily_pnl REAL,
            total_pnl REAL,
            max_drawdown REAL,
            sector_exposure TEXT,
            correlation_matrix TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """,
}

INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_trades_ticker ON trades(ticker)",
    "CREATE INDEX IF NOT EXISTS idx_trades_strategy ON trades(strategy)",
    "CREATE INDEX IF NOT EXISTS idx_trades_entry_date ON trades(entry_date)",
    "CREATE INDEX IF NOT EXISTS idx_trades_exit_date ON trades(exit_date)",
    "CREATE INDEX IF NOT EXISTS idx_signals_ticker ON signals(ticker)",
    "CREATE INDEX IF NOT EXISTS idx_signals_source ON signals(source)",
    "CREATE INDEX IF NOT EXISTS idx_signals_date ON signals(signal_date)",
    "CREATE INDEX IF NOT EXISTS idx_regime_date ON regime_history(assessment_date)",
    "CREATE INDEX IF NOT EXISTS idx_snapshots_date ON portfolio_snapshots(snapshot_date)",
]


def init_database(db_path: Path, verbose: bool = False) -> dict:
    """Initialize the database and return a status report."""
    existed = db_path.exists()
    existing_tables = []

    if existed:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        existing_tables = [row[0] for row in cursor.fetchall()]
        conn.close()

    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    created_tables = []

    for table_name, ddl in SCHEMA.items():
        if table_name not in existing_tables:
            conn.execute(ddl)
            created_tables.append(table_name)
            if verbose:
                print(f"  Created table: {table_name}", file=sys.stderr)
        elif verbose:
            print(f"  Existing table preserved: {table_name}", file=sys.stderr)

    for idx_sql in INDEXES:
        conn.execute(idx_sql)

    conn.commit()
    conn.close()

    return {
        "script": "init_db",
        "version": "1.0.0",
        "db_path": str(db_path),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "pass",
        "existed": existed,
        "existing_tables": existing_tables,
        "created_tables": created_tables,
        "total_tables": list(SCHEMA.keys()),
        "findings": [],
        "summary": {
            "total_tables": len(SCHEMA),
            "created": len(created_tables),
            "preserved": len(existing_tables),
        },
    }


def main():
    parser = argparse.ArgumentParser(
        description="Initialize The Money SQLite database (tm-signals.db). "
        "Creates tables for trades, signals, strategies, regime history, "
        "source accuracy, and portfolio snapshots. Safe on existing databases.",
    )
    parser.add_argument(
        "db_path",
        help="Path to the SQLite database file",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Write JSON report to file instead of stdout",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print progress to stderr",
    )
    args = parser.parse_args()

    try:
        result = init_database(Path(args.db_path), verbose=args.verbose)
        output = json.dumps(result, indent=2)

        if args.output:
            Path(args.output).write_text(output)
        else:
            print(output)

        sys.exit(0)
    except Exception as e:
        error = {
            "script": "init_db",
            "version": "1.0.0",
            "status": "error",
            "error": str(e),
        }
        print(json.dumps(error, indent=2))
        sys.exit(2)


if __name__ == "__main__":
    main()

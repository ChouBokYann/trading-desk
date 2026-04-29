#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Compute per-strategy statistics from tm-signals.db trade history.

Reads closed trades from the SQLite database and computes: trade count, win rate,
avg win/loss R, expected value, Sharpe ratio, max drawdown, and current streak
per strategy (signal_source or setup type).
"""

import argparse
import json
import math
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path


def compute_stats(trades: list[dict]) -> dict:
    """Compute stats for a list of trade dicts with r_multiple field."""
    if not trades:
        return {
            "trade_count": 0, "win_rate": 0, "avg_win_r": 0, "avg_loss_r": 0,
            "expected_value": 0, "sharpe": 0, "max_drawdown_r": 0,
            "current_streak": 0, "streak_type": "none",
            "proof_progress": "0/100",
        }

    rs = [t["r_multiple"] for t in trades if t.get("r_multiple") is not None]
    if not rs:
        return {"trade_count": len(trades), "error": "no R-multiple data"}

    wins = [r for r in rs if r > 0]
    losses = [r for r in rs if r <= 0]
    win_rate = len(wins) / len(rs) * 100 if rs else 0
    avg_win = sum(wins) / len(wins) if wins else 0
    avg_loss = sum(losses) / len(losses) if losses else 0
    ev = sum(rs) / len(rs) if rs else 0

    # Sharpe: mean(R) / std(R)
    mean_r = sum(rs) / len(rs)
    if len(rs) > 1:
        variance = sum((r - mean_r) ** 2 for r in rs) / (len(rs) - 1)
        std_r = math.sqrt(variance)
        sharpe = mean_r / std_r if std_r > 0 else 0
    else:
        sharpe = 0

    # Max drawdown in R terms
    cumulative = 0
    peak = 0
    max_dd = 0
    for r in rs:
        cumulative += r
        if cumulative > peak:
            peak = cumulative
        dd = peak - cumulative
        if dd > max_dd:
            max_dd = dd

    # Current streak
    streak = 0
    if rs:
        last_sign = rs[-1] > 0
        for r in reversed(rs):
            if (r > 0) == last_sign:
                streak += 1
            else:
                break
    streak_type = "win" if rs and rs[-1] > 0 else "loss" if rs else "none"

    return {
        "trade_count": len(rs),
        "win_rate": round(win_rate, 1),
        "avg_win_r": round(avg_win, 2),
        "avg_loss_r": round(avg_loss, 2),
        "expected_value": round(ev, 3),
        "sharpe": round(sharpe, 2),
        "max_drawdown_r": round(max_dd, 2),
        "current_streak": streak,
        "streak_type": streak_type,
        "proof_progress": f"{len(rs)}/100",
    }


def query_trades(db_path: str, days: int | None = None) -> list[dict]:
    """Query closed trades from tm-signals.db."""
    if not Path(db_path).exists():
        return []

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Check if trades table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='trades'")
    if not cursor.fetchone():
        conn.close()
        return []

    query = "SELECT * FROM trades WHERE status = 'closed'"
    params = []
    if days:
        query += " AND exit_date >= date('now', ?)"
        params.append(f"-{days} days")
    query += " ORDER BY exit_date DESC"

    try:
        cursor.execute(query, params)
        trades = [dict(row) for row in cursor.fetchall()]
    except sqlite3.OperationalError:
        trades = []
    finally:
        conn.close()

    return trades


def group_by_strategy(trades: list[dict], group_field: str = "signal_source") -> dict[str, list[dict]]:
    """Group trades by strategy/source field."""
    groups: dict[str, list[dict]] = {}
    for t in trades:
        key = t.get(group_field, "unknown") or "unknown"
        groups.setdefault(key, []).append(t)
    return groups


def main():
    parser = argparse.ArgumentParser(
        description="Compute per-strategy stats from tm-signals.db"
    )
    parser.add_argument("db_path", help="Path to tm-signals.db")
    parser.add_argument("--days", type=int, default=None, help="Limit to trades closed within N days (default: all)")
    parser.add_argument("--group-by", default="signal_source", help="Field to group by (default: signal_source)")
    parser.add_argument("-o", dest="output_file", default=None, help="Output file (default: stdout)")
    parser.add_argument("--verbose", action="store_true", help="Print diagnostics to stderr")
    args = parser.parse_args()

    trades = query_trades(args.db_path, args.days)

    if args.verbose:
        print(f"Found {len(trades)} closed trades", file=sys.stderr)

    groups = group_by_strategy(trades, args.group_by)
    all_stats = compute_stats(trades)

    per_strategy = {}
    for name, group_trades in sorted(groups.items()):
        per_strategy[name] = compute_stats(group_trades)

    output = {
        "script": "strategy_stats",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "db_path": args.db_path,
        "days_filter": args.days,
        "group_by": args.group_by,
        "overall": all_stats,
        "per_strategy": per_strategy,
    }

    json_str = json.dumps(output, indent=2)

    if args.output_file:
        with open(args.output_file, "w") as f:
            f.write(json_str)
    else:
        print(json_str)


if __name__ == "__main__":
    main()

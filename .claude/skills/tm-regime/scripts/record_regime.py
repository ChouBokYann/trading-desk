#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Record a regime assessment to the quantitative signal database.

Inserts a regime_history row into tm-signals.db with the current
regime state for historical tracking and synthesis queries.
"""

import argparse
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path


def record_regime(db_path: Path, regime_data: dict) -> dict:
    """Insert a regime assessment into the database."""
    conn = sqlite3.connect(str(db_path))

    conn.execute(
        """INSERT INTO regime_history
           (assessment_date, macro_regime, macro_confidence, sector_data,
            distribution_days, r0_data, vix, yield_curve_spread,
            breadth_score, flag_level, safety_car, notes)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            regime_data.get("timestamp", datetime.now(timezone.utc).isoformat()),
            regime_data.get("macro", "sideways"),
            regime_data.get("macro_confidence", 0.5),
            json.dumps(regime_data.get("sectors", {})),
            regime_data.get("distribution_days", 0),
            json.dumps(regime_data.get("r0_leading_sectors", {})),
            regime_data.get("vix"),
            regime_data.get("yield_curve_spread"),
            regime_data.get("breadth_score"),
            regime_data.get("flag", "green"),
            1 if regime_data.get("safety_car", False) else 0,
            regime_data.get("notes", ""),
        ),
    )

    conn.commit()
    row_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    conn.close()

    return {
        "script": "record_regime",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "pass",
        "row_id": row_id,
        "db_path": str(db_path),
        "findings": [],
        "summary": {"recorded": True, "flag": regime_data.get("flag", "green")},
    }


def main():
    parser = argparse.ArgumentParser(
        description="Record regime assessment to tm-signals.db. "
        "Accepts regime state as JSON via --regime flag or stdin.",
    )
    parser.add_argument("db_path", help="Path to tm-signals.db")
    parser.add_argument(
        "--regime",
        help="Regime state as JSON string",
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
        if args.regime:
            regime_data = json.loads(args.regime)
        else:
            regime_data = json.load(sys.stdin)

        if args.verbose:
            print(
                f"  Recording regime: {regime_data.get('flag', 'unknown')}",
                file=sys.stderr,
            )

        result = record_regime(Path(args.db_path), regime_data)
        output = json.dumps(result, indent=2)

        if args.output:
            with open(args.output, "w") as f:
                f.write(output)
        else:
            print(output)

        sys.exit(0)

    except Exception as e:
        error = {
            "script": "record_regime",
            "version": "1.0.0",
            "status": "error",
            "error": str(e),
        }
        print(json.dumps(error, indent=2))
        sys.exit(2)


if __name__ == "__main__":
    main()

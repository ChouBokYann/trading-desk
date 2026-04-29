#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Count distribution days using the Investor's Business Daily method.

A distribution day occurs when a major index drops ≥0.2% on volume higher
than the previous session. Stalling days are also tracked: index closes in
upper half of range, gains <0.2%, on higher volume than prior day.

Accepts JSON price/volume data from stdin or file. Outputs distribution and
stalling day counts per index with flag level assessment.
"""

import argparse
import json
import sys
from datetime import datetime, timezone


def calculate_distribution_days(
    daily_data: list[dict], lookback: int = 25
) -> dict:
    """Calculate distribution and stalling days from OHLCV data.

    Args:
        daily_data: List of dicts with keys: date, open, high, low, close, volume.
                    Must be sorted by date ascending.
        lookback: Number of trading days to look back (default 25).

    Returns:
        Dict with distribution_days, stalling_days, details, and flag.
    """
    if len(daily_data) < 2:
        return {
            "distribution_days": 0,
            "stalling_days": 0,
            "details": [],
            "flag": "green",
            "error": "insufficient data",
        }

    window = daily_data[-lookback:] if len(daily_data) >= lookback else daily_data
    distribution_days = []
    stalling_days = []

    for i in range(1, len(window)):
        today = window[i]
        yesterday = window[i - 1]

        today_close = float(today["close"])
        yesterday_close = float(yesterday["close"])
        today_volume = float(today["volume"])
        yesterday_volume = float(yesterday["volume"])
        today_high = float(today["high"])
        today_low = float(today["low"])

        pct_change = (today_close - yesterday_close) / yesterday_close * 100
        volume_higher = today_volume > yesterday_volume

        if pct_change <= -0.2 and volume_higher:
            distribution_days.append(
                {
                    "date": today["date"],
                    "pct_change": round(pct_change, 3),
                    "volume_ratio": round(today_volume / yesterday_volume, 2),
                }
            )

        daily_range = today_high - today_low
        if daily_range > 0:
            close_position = (today_close - today_low) / daily_range
            if (
                close_position >= 0.5
                and 0 <= pct_change < 0.2
                and volume_higher
            ):
                stalling_days.append(
                    {
                        "date": today["date"],
                        "pct_change": round(pct_change, 3),
                        "close_position": round(close_position, 2),
                    }
                )

    d_count = len(distribution_days)
    if d_count >= 6:
        flag = "red"
    elif d_count >= 4:
        flag = "yellow"
    else:
        flag = "green"

    return {
        "distribution_days": d_count,
        "stalling_days": len(stalling_days),
        "lookback_days": len(window),
        "distribution_details": distribution_days,
        "stalling_details": stalling_days,
        "flag": flag,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Count distribution days (IBD method) from OHLCV price data. "
        "Reads JSON from stdin or file. Each index is a key mapping to an array "
        "of {date, open, high, low, close, volume} objects sorted by date ascending.",
    )
    parser.add_argument(
        "input_file",
        nargs="?",
        help="JSON file with price data (default: stdin)",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=25,
        help="Lookback window in trading days (default: 25)",
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
        if args.input_file:
            with open(args.input_file) as f:
                data = json.load(f)
        else:
            data = json.load(sys.stdin)

        results = {}
        overall_flag = "green"
        flag_priority = {"green": 0, "yellow": 1, "red": 2}

        for index_name, daily_data in data.items():
            if args.verbose:
                print(
                    f"  Processing {index_name}: {len(daily_data)} days",
                    file=sys.stderr,
                )
            result = calculate_distribution_days(daily_data, args.days)
            results[index_name] = result
            if flag_priority.get(result["flag"], 0) > flag_priority.get(
                overall_flag, 0
            ):
                overall_flag = result["flag"]

        report = {
            "script": "distribution_days",
            "version": "1.0.0",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "pass",
            "lookback_days": args.days,
            "overall_flag": overall_flag,
            "indexes": results,
            "findings": [],
            "summary": {
                "indexes_analyzed": len(results),
                "overall_flag": overall_flag,
            },
        }

        output = json.dumps(report, indent=2)
        if args.output:
            with open(args.output, "w") as f:
                f.write(output)
        else:
            print(output)

        sys.exit(0)

    except Exception as e:
        error = {
            "script": "distribution_days",
            "version": "1.0.0",
            "status": "error",
            "error": str(e),
        }
        print(json.dumps(error, indent=2))
        sys.exit(2)


if __name__ == "__main__":
    main()

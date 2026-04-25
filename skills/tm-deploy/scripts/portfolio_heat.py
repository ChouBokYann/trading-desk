#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Portfolio heat calculator -- total risk across open positions vs. configured limit.

Reads positions as JSON array from stdin. Each object needs:
ticker, entry_price, stop_price, shares, current_price
"""

import argparse
import json
import sys
from datetime import datetime, timezone


def calculate_heat(positions: list[dict], account_value: float, heat_limit: float) -> dict:
    if account_value <= 0:
        return {"status": "fail", "error": "Account value must be positive"}

    position_risks = []
    total_risk = 0.0

    for pos in positions:
        try:
            per_share_risk = abs(pos["entry_price"] - pos["stop_price"])
            dollar_risk = per_share_risk * pos["shares"]
            risk_pct = (dollar_risk / account_value) * 100
            current_pnl = (pos["current_price"] - pos["entry_price"]) * pos["shares"]
            current_pnl_pct = (current_pnl / account_value) * 100

            position_risks.append({
                "ticker": pos["ticker"],
                "shares": pos["shares"],
                "entry_price": pos["entry_price"],
                "stop_price": pos["stop_price"],
                "current_price": pos["current_price"],
                "per_share_risk": round(per_share_risk, 2),
                "dollar_risk": round(dollar_risk, 2),
                "risk_pct": round(risk_pct, 4),
                "current_pnl": round(current_pnl, 2),
                "current_pnl_pct": round(current_pnl_pct, 4),
            })
            total_risk += risk_pct
        except (KeyError, TypeError) as e:
            position_risks.append({"ticker": pos.get("ticker", "UNKNOWN"), "error": str(e)})

    total_risk = round(total_risk, 4)
    headroom = round(heat_limit - total_risk, 4)

    return {
        "status": "fail" if total_risk > heat_limit else "pass",
        "total_heat_pct": total_risk,
        "heat_limit_pct": heat_limit,
        "headroom_pct": headroom,
        "breached": total_risk > heat_limit,
        "position_count": len(positions),
        "positions": position_risks,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Portfolio heat: total risk across open positions vs. configured limit",
        epilog="Reads positions as JSON array from stdin. Each object needs: ticker, entry_price, stop_price, shares, current_price",
    )
    parser.add_argument("--account-value", type=float, required=True, help="Total account equity in dollars")
    parser.add_argument("--heat-limit", type=float, default=8.0, help="Maximum portfolio heat %% (default 8.0)")
    parser.add_argument("-o", dest="output_file", default=None, help="Output file (default: stdout)")
    parser.add_argument("--verbose", action="store_true", help="Print diagnostics to stderr")
    args = parser.parse_args()

    try:
        positions = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        output = {"script": "portfolio_heat", "version": "1.0.0", "timestamp": datetime.now(timezone.utc).isoformat(), "status": "fail", "error": f"Invalid JSON input: {e}"}
        print(json.dumps(output, indent=2))
        sys.exit(2)

    if args.verbose:
        print(f"Inputs: account={args.account_value}, limit={args.heat_limit}%, positions={len(positions)}", file=sys.stderr)

    result = calculate_heat(positions, args.account_value, args.heat_limit)
    output = {"script": "portfolio_heat", "version": "1.0.0", "timestamp": datetime.now(timezone.utc).isoformat(), **result}
    json_str = json.dumps(output, indent=2)

    if args.output_file:
        with open(args.output_file, "w") as f:
            f.write(json_str)
    else:
        print(json_str)

    sys.exit(0 if result["status"] == "pass" else 1)


if __name__ == "__main__":
    main()

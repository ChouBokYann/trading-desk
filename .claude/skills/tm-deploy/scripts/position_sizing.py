#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Position sizing: half-Kelly x conviction tier x regime adjustment x liquidity multiplier."""

import argparse
import json
import math
import sys
from datetime import datetime, timezone

RISK_TIERS = {1: 0.02, 2: 0.01, 3: 0.0025}
REGIME_MULTIPLIERS = {"green": 1.0, "yellow": 0.5, "red": 0.0, "black": 0.0}


def half_kelly_size(
    account_value: float,
    entry_price: float,
    stop_price: float,
    conviction_tier: int,
    regime_flag: str,
    spread_pct: float = 0.05,
    vix: float = 16.0,
) -> dict:
    base_risk_pct = RISK_TIERS.get(conviction_tier, 0.01)
    regime_mult = REGIME_MULTIPLIERS.get(regime_flag, 0.5)

    liquidity_mult = 1.0
    if spread_pct > 0.3:
        liquidity_mult *= 0.375
    elif spread_pct > 0.1:
        liquidity_mult *= 0.75
    if vix > 35:
        liquidity_mult *= 0.375
    elif vix > 25:
        liquidity_mult *= 0.75

    adjusted_risk_pct = base_risk_pct * regime_mult * liquidity_mult
    dollar_risk = account_value * adjusted_risk_pct

    per_share_risk = abs(entry_price - stop_price)
    if per_share_risk == 0:
        return {"status": "fail", "error": "Entry and stop prices are identical"}

    shares = math.floor(dollar_risk / per_share_risk)
    position_value = shares * entry_price
    position_pct = (position_value / account_value * 100) if account_value > 0 else 0
    actual_dollar_risk = shares * per_share_risk
    actual_risk_pct = (actual_dollar_risk / account_value * 100) if account_value > 0 else 0

    return {
        "status": "pass",
        "shares": shares,
        "entry_price": entry_price,
        "stop_price": stop_price,
        "per_share_risk": round(per_share_risk, 2),
        "position_value": round(position_value, 2),
        "position_pct": round(position_pct, 2),
        "dollar_risk": round(actual_dollar_risk, 2),
        "risk_pct": round(actual_risk_pct, 4),
        "sizing_breakdown": {
            "base_risk_pct": base_risk_pct,
            "conviction_tier": conviction_tier,
            "regime_flag": regime_flag,
            "regime_multiplier": regime_mult,
            "spread_pct": spread_pct,
            "vix": vix,
            "liquidity_multiplier": round(liquidity_mult, 4),
            "adjusted_risk_pct": round(adjusted_risk_pct, 6),
        },
    }


def main():
    parser = argparse.ArgumentParser(
        description="Position sizing: half-Kelly x conviction x regime x liquidity"
    )
    parser.add_argument("--account-value", type=float, required=True, help="Total account equity in dollars")
    parser.add_argument("--entry", type=float, required=True, help="Entry price")
    parser.add_argument("--stop", type=float, required=True, help="Stop loss price")
    parser.add_argument("--conviction", type=int, choices=[1, 2, 3], default=2, help="Conviction tier: 1=high (2%%), 2=mixed (1%%), 3=spec (0.25%%)")
    parser.add_argument("--regime", choices=["green", "yellow", "red", "black"], default="green", help="Current regime flag")
    parser.add_argument("--spread-pct", type=float, default=0.05, help="Bid-ask spread as %% of price (default 0.05)")
    parser.add_argument("--vix", type=float, default=16.0, help="Current VIX level (default 16.0)")
    parser.add_argument("-o", dest="output_file", default=None, help="Output file (default: stdout)")
    parser.add_argument("--verbose", action="store_true", help="Print diagnostics to stderr")
    args = parser.parse_args()

    if args.verbose:
        print(
            f"Inputs: account={args.account_value}, entry={args.entry}, stop={args.stop}, "
            f"conviction={args.conviction}, regime={args.regime}, spread={args.spread_pct}%, vix={args.vix}",
            file=sys.stderr,
        )

    result = half_kelly_size(
        account_value=args.account_value,
        entry_price=args.entry,
        stop_price=args.stop,
        conviction_tier=args.conviction,
        regime_flag=args.regime,
        spread_pct=args.spread_pct,
        vix=args.vix,
    )

    output = {"script": "position_sizing", "version": "1.0.0", "timestamp": datetime.now(timezone.utc).isoformat(), **result}
    json_str = json.dumps(output, indent=2)

    if args.output_file:
        with open(args.output_file, "w") as f:
            f.write(json_str)
    else:
        print(json_str)

    sys.exit(0 if result["status"] == "pass" else 1)


if __name__ == "__main__":
    main()

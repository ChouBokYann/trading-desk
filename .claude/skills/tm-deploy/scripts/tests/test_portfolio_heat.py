#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from portfolio_heat import calculate_heat


def test_empty_portfolio():
    """No positions -> 0% heat, pass."""
    result = calculate_heat([], 100000, 8.0)
    assert result["status"] == "pass"
    assert result["total_heat_pct"] == 0
    assert result["headroom_pct"] == 8.0


def test_single_position_within_limit():
    """One position, within limit."""
    positions = [{
        "ticker": "AAPL",
        "entry_price": 195.50,
        "stop_price": 187.20,
        "shares": 45,
        "current_price": 200.00,
    }]
    result = calculate_heat(positions, 100000, 8.0)
    assert result["status"] == "pass"
    # Risk: (195.50 - 187.20) * 45 = $373.50 = 0.3735%
    assert abs(result["total_heat_pct"] - 0.3735) < 0.01


def test_breached_limit():
    """Positions exceed heat limit -> fail."""
    positions = [
        {"ticker": "AAPL", "entry_price": 200.0, "stop_price": 180.0, "shares": 200, "current_price": 195.0},
        {"ticker": "MSFT", "entry_price": 400.0, "stop_price": 370.0, "shares": 100, "current_price": 395.0},
    ]
    # AAPL: 20 * 200 = $4000 = 4%, MSFT: 30 * 100 = $3000 = 3%, total 7%
    result = calculate_heat(positions, 100000, 6.0)
    assert result["status"] == "fail"
    assert result["breached"] is True
    assert result["total_heat_pct"] == 7.0


def test_pnl_calculated():
    """Current P&L is included per position."""
    positions = [{
        "ticker": "TSLA",
        "entry_price": 250.0,
        "stop_price": 240.0,
        "shares": 30,
        "current_price": 260.0,
    }]
    result = calculate_heat(positions, 100000, 8.0)
    pos = result["positions"][0]
    assert pos["current_pnl"] == 300.0  # (260 - 250) * 30
    assert pos["current_pnl_pct"] == 0.3


def test_multiple_positions_sum():
    """Heat is the sum across all positions."""
    positions = [
        {"ticker": "A", "entry_price": 100.0, "stop_price": 95.0, "shares": 100, "current_price": 102.0},
        {"ticker": "B", "entry_price": 50.0, "stop_price": 47.0, "shares": 200, "current_price": 51.0},
    ]
    # A: 5 * 100 = $500 = 0.5%, B: 3 * 200 = $600 = 0.6%, total 1.1%
    result = calculate_heat(positions, 100000, 8.0)
    assert abs(result["total_heat_pct"] - 1.1) < 0.01


def test_zero_account_value():
    """Zero account value -> fail."""
    result = calculate_heat([], 0, 8.0)
    assert result["status"] == "fail"


def test_headroom_calculation():
    """Headroom = limit - current heat."""
    positions = [
        {"ticker": "SPY", "entry_price": 500.0, "stop_price": 490.0, "shares": 50, "current_price": 505.0},
    ]
    # Risk: 10 * 50 = $500 = 0.5%
    result = calculate_heat(positions, 100000, 8.0)
    assert abs(result["headroom_pct"] - 7.5) < 0.01


if __name__ == "__main__":
    tests = [name for name in sorted(dir()) if name.startswith("test_")]
    passed = failed = 0
    for name in tests:
        try:
            globals()[name]()
            passed += 1
            print(f"  PASS  {name}")
        except AssertionError as e:
            failed += 1
            print(f"  FAIL  {name}: {e}")
        except Exception as e:
            failed += 1
            print(f"  FAIL  {name}: {type(e).__name__}: {e}")
    print(f"\n{passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)

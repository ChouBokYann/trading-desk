#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from strategy_stats import compute_stats, group_by_strategy


SAMPLE_TRADES = [
    {"r_multiple": 2.5, "signal_source": "analyze-pipeline"},
    {"r_multiple": -1.0, "signal_source": "analyze-pipeline"},
    {"r_multiple": 1.8, "signal_source": "analyze-pipeline"},
    {"r_multiple": 3.0, "signal_source": "alpha-chain"},
    {"r_multiple": -1.0, "signal_source": "alpha-chain"},
    {"r_multiple": -1.0, "signal_source": "manual"},
    {"r_multiple": 0.5, "signal_source": "manual"},
]


def test_empty_trades():
    """Empty list returns zeroed stats."""
    result = compute_stats([])
    assert result["trade_count"] == 0
    assert result["win_rate"] == 0
    assert result["expected_value"] == 0


def test_all_winners():
    """All winning trades -> 100% win rate, positive EV."""
    trades = [{"r_multiple": 2.0}, {"r_multiple": 1.5}, {"r_multiple": 3.0}]
    result = compute_stats(trades)
    assert result["win_rate"] == 100.0
    assert result["expected_value"] > 0
    assert result["max_drawdown_r"] == 0


def test_all_losers():
    """All losing trades -> 0% win rate, negative EV."""
    trades = [{"r_multiple": -1.0}, {"r_multiple": -0.5}, {"r_multiple": -1.0}]
    result = compute_stats(trades)
    assert result["win_rate"] == 0.0
    assert result["expected_value"] < 0


def test_mixed_trades():
    """Mixed trades compute correct win rate."""
    result = compute_stats(SAMPLE_TRADES)
    # 4 wins (2.5, 1.8, 3.0, 0.5) out of 7 = 57.1%
    assert result["trade_count"] == 7
    assert abs(result["win_rate"] - 57.1) < 0.2


def test_expected_value():
    """EV is mean of R-multiples."""
    trades = [{"r_multiple": 2.0}, {"r_multiple": -1.0}]
    result = compute_stats(trades)
    assert result["expected_value"] == 0.5  # (2.0 + -1.0) / 2


def test_max_drawdown():
    """Drawdown tracks peak-to-trough in cumulative R."""
    trades = [{"r_multiple": 3.0}, {"r_multiple": -1.0}, {"r_multiple": -1.0}, {"r_multiple": 2.0}]
    # Cumulative: 3, 2, 1, 3. Peak=3, trough=1, dd=2
    result = compute_stats(trades)
    assert result["max_drawdown_r"] == 2.0


def test_current_streak_win():
    """Detects winning streak at end."""
    trades = [{"r_multiple": -1.0}, {"r_multiple": 2.0}, {"r_multiple": 1.5}]
    result = compute_stats(trades)
    assert result["current_streak"] == 2
    assert result["streak_type"] == "win"


def test_current_streak_loss():
    """Detects losing streak at end."""
    trades = [{"r_multiple": 2.0}, {"r_multiple": -1.0}, {"r_multiple": -0.5}]
    result = compute_stats(trades)
    assert result["current_streak"] == 2
    assert result["streak_type"] == "loss"


def test_proof_progress():
    """Shows progress toward 100-trade proof."""
    trades = [{"r_multiple": 1.0}] * 42
    result = compute_stats(trades)
    assert result["proof_progress"] == "42/100"


def test_group_by_strategy():
    """Groups trades by signal source."""
    groups = group_by_strategy(SAMPLE_TRADES)
    assert len(groups) == 3
    assert len(groups["analyze-pipeline"]) == 3
    assert len(groups["alpha-chain"]) == 2
    assert len(groups["manual"]) == 2


def test_sharpe_positive():
    """Sharpe is positive for consistently profitable trades."""
    trades = [{"r_multiple": 2.0}, {"r_multiple": 1.5}, {"r_multiple": 2.5}, {"r_multiple": 1.0}]
    result = compute_stats(trades)
    assert result["sharpe"] > 0


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

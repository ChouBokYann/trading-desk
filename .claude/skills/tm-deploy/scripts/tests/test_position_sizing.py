#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from position_sizing import half_kelly_size


def test_tier1_green_full_size():
    """Tier 1 conviction, green regime, normal liquidity -> 2% risk."""
    result = half_kelly_size(100000, 100.0, 95.0, 1, "green")
    assert result["status"] == "pass"
    assert result["shares"] == 400  # 2000 / 5
    assert result["risk_pct"] <= 2.0


def test_tier2_green():
    """Tier 2 conviction -> 1% risk."""
    result = half_kelly_size(100000, 50.0, 47.0, 2, "green")
    assert result["status"] == "pass"
    assert result["shares"] == 333  # floor(1000 / 3)
    assert result["risk_pct"] <= 1.0


def test_tier3_speculative():
    """Tier 3 -> 0.25% risk."""
    result = half_kelly_size(100000, 200.0, 190.0, 3, "green")
    assert result["status"] == "pass"
    assert result["shares"] == 25  # floor(250 / 10)
    assert result["dollar_risk"] <= 250


def test_yellow_regime_halves():
    """Yellow regime cuts sizing to 50%."""
    green = half_kelly_size(100000, 100.0, 95.0, 1, "green")
    yellow = half_kelly_size(100000, 100.0, 95.0, 1, "yellow")
    assert yellow["shares"] == green["shares"] // 2


def test_red_regime_zero():
    """Red regime -> 0 shares."""
    result = half_kelly_size(100000, 100.0, 95.0, 1, "red")
    assert result["shares"] == 0


def test_high_vix_reduces():
    """VIX > 25 reduces liquidity multiplier."""
    normal = half_kelly_size(100000, 100.0, 95.0, 1, "green", vix=16.0)
    elevated = half_kelly_size(100000, 100.0, 95.0, 1, "green", vix=30.0)
    assert elevated["shares"] < normal["shares"]


def test_wide_spread_reduces():
    """Wide bid-ask spread reduces sizing."""
    tight = half_kelly_size(100000, 100.0, 95.0, 1, "green", spread_pct=0.03)
    wide = half_kelly_size(100000, 100.0, 95.0, 1, "green", spread_pct=0.2)
    assert wide["shares"] < tight["shares"]


def test_zero_risk_fails():
    """Same entry and stop -> error."""
    result = half_kelly_size(100000, 100.0, 100.0, 1, "green")
    assert result["status"] == "fail"


def test_short_position():
    """Short: stop above entry, same math."""
    result = half_kelly_size(100000, 100.0, 105.0, 1, "green")
    assert result["status"] == "pass"
    assert result["shares"] == 400  # 2000 / 5


def test_sizing_breakdown_included():
    """Output includes the full sizing breakdown."""
    result = half_kelly_size(100000, 100.0, 95.0, 2, "yellow", spread_pct=0.15, vix=28)
    breakdown = result["sizing_breakdown"]
    assert breakdown["conviction_tier"] == 2
    assert breakdown["regime_multiplier"] == 0.5
    assert breakdown["liquidity_multiplier"] < 1.0


def test_combined_spread_and_vix():
    """Wide spread + high VIX stack multiplicatively."""
    clean = half_kelly_size(100000, 100.0, 95.0, 1, "green", spread_pct=0.03, vix=16.0)
    dirty = half_kelly_size(100000, 100.0, 95.0, 1, "green", spread_pct=0.2, vix=30.0)
    # 0.75 (spread) * 0.75 (VIX) = 0.5625x
    assert dirty["shares"] < clean["shares"]
    assert dirty["sizing_breakdown"]["liquidity_multiplier"] == 0.5625


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

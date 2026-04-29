"""Deterministic condition evaluation — no AI, no randomness."""

import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

_OPS = {
    ">=": lambda a, b: a >= b,
    "<=": lambda a, b: a <= b,
    ">":  lambda a, b: a > b,
    "<":  lambda a, b: a < b,
    "==": lambda a, b: a == b,
    "!=": lambda a, b: a != b,
}


def evaluate(conditions: list[dict], metrics: dict) -> tuple[bool, list[str]]:
    """
    Evaluate all conditions against current market metrics.
    ALL conditions must pass (AND logic).

    Returns (passed: bool, failures: list[str])

    Condition schemas:
      Numeric:  { metric: "gap_pct",    op: ">=", value: 3.0 }
      Boolean:  { metric: "price_above_vwap", value: true }
      Time window: { metric: "time_in_window", start: "09:30", end: "11:00" }
    """
    failures = []

    for cond in conditions:
        metric = cond.get("metric")

        # Time window check (no metrics lookup needed)
        if metric == "time_in_window":
            if not _check_time_window(cond):
                failures.append(f"time_in_window: outside {cond.get('start')}-{cond.get('end')} ET")
            continue

        # All other conditions require live metric data
        if metric not in metrics or metrics[metric] is None:
            failures.append(f"{metric}: data unavailable")
            continue

        actual = metrics[metric]

        # Boolean condition
        if "op" not in cond:
            expected = cond.get("value")
            if isinstance(expected, bool):
                if actual != expected:
                    failures.append(f"{metric}: expected {expected}, got {actual}")
            continue

        # Numeric condition
        op_str = cond["op"]
        op_fn = _OPS.get(op_str)
        if op_fn is None:
            logger.warning(f"Unknown operator: {op_str}")
            failures.append(f"{metric}: unknown operator '{op_str}'")
            continue

        expected = cond["value"]
        if not op_fn(actual, expected):
            failures.append(f"{metric}: {actual:.3f} {op_str} {expected} FAILED")

    passed = len(failures) == 0
    return passed, failures


def _check_time_window(cond: dict) -> bool:
    """Check if current ET time is within the specified window."""
    now_utc = datetime.now(timezone.utc)
    month = now_utc.month
    et_offset = -4 if 3 <= month <= 11 else -5
    now_et_hour = (now_utc.hour + et_offset) % 24
    now_et_min = now_utc.minute
    now_minutes = now_et_hour * 60 + now_et_min

    def parse_hhmm(s: str) -> int:
        h, m = map(int, s.split(":"))
        return h * 60 + m

    start_min = parse_hhmm(cond.get("start", "09:30"))
    end_min = parse_hhmm(cond.get("end", "11:00"))

    return start_min <= now_minutes <= end_min

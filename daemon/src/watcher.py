"""
2-minute polling loop. Runs during market hours (9:30–11:00 AM ET).
Checks trigger conditions, fires orders when all conditions pass.
"""

import logging
import time
from datetime import datetime, timezone

from .condition_engine import evaluate
from .config_loader import ConfigLoader
from .market_data import MarketDataFetcher
from .risk_monitor import RiskMonitor
from .order_router import OrderRouter
from .state_machine import StateMachine, State
from .position_manager import PositionManager

logger = logging.getLogger(__name__)

POLL_INTERVAL_SECONDS = 120   # 2 minutes
MARKET_OPEN_ET  = (9,  30)
MARKET_CLOSE_ET = (11,  0)


def _et_now() -> tuple[int, int]:
    now_utc = datetime.now(timezone.utc)
    month = now_utc.month
    offset = 4 if 3 <= month <= 11 else 5
    et_hour = (now_utc.hour - offset) % 24
    return et_hour, now_utc.minute


def _in_market_window() -> bool:
    h, m = _et_now()
    now_min = h * 60 + m
    open_min  = MARKET_OPEN_ET[0]  * 60 + MARKET_OPEN_ET[1]
    close_min = MARKET_CLOSE_ET[0] * 60 + MARKET_CLOSE_ET[1]
    return open_min <= now_min <= close_min


class Watcher:
    def __init__(
        self,
        config: ConfigLoader,
        market_data: MarketDataFetcher,
        risk_monitor: RiskMonitor,
        order_router: OrderRouter,
        position_manager: PositionManager,
    ):
        self.config = config
        self.market_data = market_data
        self.risk_monitor = risk_monitor
        self.order_router = order_router
        self.position_manager = position_manager
        self.sm = StateMachine()
        self._trades_fired: list[dict] = []

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    def run(self):
        """Main loop — runs every 2 min during 9:30-11:00 AM ET."""
        logger.info("Watcher started. Waiting for market window (9:30–11:00 AM ET).")

        while True:
            if not _in_market_window():
                h, m = _et_now()
                logger.info(f"Outside market window (ET {h:02d}:{m:02d}). Sleeping 60s.")
                time.sleep(60)
                continue

            self._tick()
            logger.info(f"Poll complete. Sleeping {POLL_INTERVAL_SECONDS}s.")
            time.sleep(POLL_INTERVAL_SECONDS)

    def run_once(self):
        """Single poll — useful for testing."""
        return self._tick()

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _tick(self) -> list[dict]:
        """One full evaluation pass across all active triggers."""
        fired_this_tick = []
        triggers = self.config.load_daily_triggers()

        if not triggers:
            logger.info("No active triggers today.")
            return []

        logger.info(f"Checking {len(triggers)} triggers...")

        for trigger in triggers:
            ticker = trigger.get("ticker", "?")

            if not self.sm.is_watchable(ticker):
                continue

            metrics = self.market_data.get_metrics(ticker)
            if not metrics:
                logger.warning(f"{ticker}: no market data, skipping")
                continue

            # Store latest price for risk monitor
            trigger["_last_price"] = metrics["price"]

            passed, failures = evaluate(trigger.get("conditions", []), metrics)

            if passed:
                result = self._fire(trigger, metrics)
                if result:
                    fired_this_tick.append(result)
            else:
                logger.debug(
                    f"{ticker} ({trigger.get('strategy')}): "
                    f"waiting — {'; '.join(failures)}"
                )

        # Position management check every tick
        self._check_positions()

        return fired_this_tick

    def _fire(self, trigger: dict, metrics: dict) -> dict | None:
        """Risk check → execute → update state."""
        ticker = trigger["ticker"]
        strategy = trigger.get("strategy", "?")
        autonomy = self.config.get_autonomy()

        logger.info(f"*** TRIGGER HIT: {ticker} ({strategy}) @ ${metrics['price']:.2f} ***")

        # Autonomy C — advisory only, never auto-execute
        if autonomy == "C":
            logger.info(f"{ticker}: autonomy=C — advisory only. No order placed.")
            self.sm.transition(ticker, State.BLOCKED)
            return {"ticker": ticker, "action": "advisory", "metrics": metrics}

        # Risk gate
        approved, reason = self.risk_monitor.check(trigger)
        if not approved:
            logger.warning(f"{ticker}: BLOCKED by risk — {reason}")
            self.sm.transition(ticker, State.BLOCKED)
            return {"ticker": ticker, "action": "blocked", "reason": reason}

        # Autonomy B — confirm before executing
        if autonomy == "B":
            logger.info(
                f"{ticker}: autonomy=B — confirmation required. "
                f"Conditions: {[c.get('metric') for c in trigger.get('conditions', [])]}. "
                f"Metrics: gap={metrics.get('gap_pct'):.1f}% vol_ratio={metrics.get('volume_ratio'):.2f}"
            )
            # In B mode we log the opportunity but don't execute.
            # Future: push a notification to the user for manual approval.
            return {"ticker": ticker, "action": "awaiting_confirmation", "metrics": metrics}

        # Autonomy A — full auto
        order = self.order_router.execute(trigger, metrics)
        if order:
            self.sm.transition(ticker, State.FIRED)
            fired_at = datetime.now(timezone.utc).isoformat()
            self.config.mark_fired(trigger, fired_at)
            self._trades_fired.append(order)
            logger.info(
                f"{ticker} EXECUTED — {order.get('shares')}sh @ "
                f"${order.get('entry_price'):.2f} | "
                f"stop=${order.get('stop_price'):.2f} target=${order.get('target_price'):.2f}"
            )
            return order
        else:
            logger.error(f"{ticker}: order_router returned None — order failed")
            return None

    def _check_positions(self):
        actions = self.position_manager.check_open_positions()
        for a in actions:
            logger.info(
                f"Position alert [{a['action']}]: {a['symbol']} "
                f"P&L={a.get('unrealized_pnl_pct', 0):.1f}% — {a.get('note', '')}"
            )

    def summary(self) -> str:
        states = self.sm.all_states()
        lines = ["Watcher session summary:"]
        for ticker, state in states.items():
            lines.append(f"  {ticker}: {state.value}")
        lines.append(f"  Trades fired this session: {len(self._trades_fired)}")
        return "\n".join(lines)

"""Routes orders to Alpaca with fill confirmation and trade logging."""

import json
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce, OrderClass

logger = logging.getLogger(__name__)


class OrderRouter:
    def __init__(self, api_key: str, api_secret: str, project_root: Path, paper: bool = True):
        self.client = TradingClient(api_key, api_secret, paper=paper)
        self.project_root = project_root

    def execute(self, trigger: dict, metrics: dict) -> dict | None:
        """
        Execute a bracket order from a fired trigger.
        Returns the Alpaca order object as a dict, or None on failure.
        """
        trade = trigger["trade"]
        ticker = trigger["ticker"]
        price = metrics["price"]

        shares = self._calculate_shares(trade, price)
        if shares <= 0:
            logger.warning(f"OrderRouter: {ticker} — shares={shares}, skipping")
            return None

        stop_price = round(price * (1 - trade["stop_pct"] / 100), 2)
        risk_per_share = price - stop_price
        target_price = round(price + risk_per_share * trade["target_rr"], 2)

        direction = trade.get("direction", "long").lower()
        side = OrderSide.BUY if direction == "long" else OrderSide.SELL

        client_order_id = f"TM-{trigger['strategy']}-{ticker}-{uuid.uuid4().hex[:8]}"

        try:
            order_req = MarketOrderRequest(
                symbol=ticker,
                qty=shares,
                side=side,
                time_in_force=TimeInForce.DAY,
                order_class=OrderClass.BRACKET,
                stop_loss={"stop_price": stop_price},
                take_profit={"limit_price": target_price},
                client_order_id=client_order_id,
            )
            order = self.client.submit_order(order_req)
            logger.info(
                f"Order placed: {ticker} {direction.upper()} {shares}sh @ mkt | "
                f"stop=${stop_price} target=${target_price} | id={client_order_id}"
            )
            order_dict = self._order_to_dict(order, trigger, metrics, shares, stop_price, target_price)
            self._write_trade_log(ticker, order_dict)
            return order_dict

        except Exception as e:
            logger.error(f"OrderRouter.execute({ticker}) failed: {e}")
            return None

    def _calculate_shares(self, trade: dict, price: float) -> int:
        """Calculate share count from max_risk and stop_pct."""
        max_risk = float(trade.get("max_risk", 150))
        stop_pct = float(trade.get("stop_pct", 3.0))
        risk_per_share = price * stop_pct / 100
        if risk_per_share <= 0:
            return 0
        return max(1, int(max_risk / risk_per_share))

    def _order_to_dict(self, order, trigger, metrics, shares, stop_price, target_price) -> dict:
        return {
            "ticker": trigger["ticker"],
            "strategy": trigger["strategy"],
            "direction": trigger["trade"].get("direction", "long"),
            "shares": shares,
            "entry_price": metrics["price"],
            "stop_price": stop_price,
            "target_price": target_price,
            "max_risk": trigger["trade"]["max_risk"],
            "rr": trigger["trade"]["target_rr"],
            "qualitative_flag": trigger.get("qualitative_flag", "green"),
            "alpaca_order_id": str(getattr(order, "id", "")),
            "client_order_id": str(getattr(order, "client_order_id", "")),
            "order_status": str(getattr(order, "status", "")),
            "metrics_at_trigger": metrics,
            "thesis": trigger.get("thesis", ""),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def _write_trade_log(self, ticker: str, order_dict: dict):
        today = datetime.now(timezone.utc).date().isoformat()
        log_dir = self.project_root / "_bmad/memory/tm/raw/trade-logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_path = log_dir / f"{today}-{ticker}.json"
        with open(log_path, "w") as f:
            json.dump(order_dict, f, indent=2)
        logger.info(f"Trade log written: {log_path}")

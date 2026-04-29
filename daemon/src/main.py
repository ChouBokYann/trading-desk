"""Entry point for The Money execution daemon."""

import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from alpaca.trading.client import TradingClient

from .config_loader import ConfigLoader
from .market_data import MarketDataFetcher
from .risk_monitor import RiskMonitor
from .order_router import OrderRouter
from .position_manager import PositionManager
from .watcher import Watcher

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
    datefmt="%H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("the-money-daemon")

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def main():
    load_dotenv(PROJECT_ROOT / ".env")

    api_key = os.getenv("ALPACA_API_KEY") or os.getenv("APCA_API_KEY_ID")
    api_secret = os.getenv("ALPACA_SECRET_KEY") or os.getenv("APCA_API_SECRET_KEY")

    if not api_key or not api_secret:
        logger.error("Alpaca keys not found. Set ALPACA_API_KEY + ALPACA_SECRET_KEY in .env. Exiting.")
        sys.exit(1)

    config = ConfigLoader(PROJECT_ROOT)
    paper = config.is_paper()
    autonomy = config.get_autonomy()

    logger.info(f"The Money daemon starting — paper={paper} autonomy={autonomy}")
    logger.info(f"Trigger dir: {PROJECT_ROOT / '_bmad/memory/tm/raw/triggers'}")

    trading_client = TradingClient(api_key, api_secret, paper=paper)
    market_data    = MarketDataFetcher(api_key, api_secret)
    risk_monitor   = RiskMonitor(trading_client, config)
    order_router   = OrderRouter(api_key, api_secret, PROJECT_ROOT, paper=paper)
    pos_manager    = PositionManager(trading_client)

    watcher = Watcher(config, market_data, risk_monitor, order_router, pos_manager)

    try:
        watcher.run()
    except KeyboardInterrupt:
        logger.info("Interrupted. Shutting down.")
        print(watcher.summary())


if __name__ == "__main__":
    main()

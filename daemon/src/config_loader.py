"""Loads config, strategy rules, and daily trigger files."""

import yaml
import logging
from datetime import date
from pathlib import Path

logger = logging.getLogger(__name__)

STRATEGY_MAX_POSITIONS = {
    "ORB": 3,
    "ERP": 2,
    "TCEP": 3,
    "EDVP": 2,
    "MRF": 2,
    "SMR": 2,
}


class ConfigLoader:
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self._tm_config = None

    def tm_config(self) -> dict:
        if self._tm_config is None:
            cfg = {}
            for path in [
                self.project_root / "_bmad/config.yaml",
                self.project_root / "_bmad/config.user.yaml",
            ]:
                if path.exists():
                    with open(path) as f:
                        data = yaml.safe_load(f) or {}
                        cfg.update(data.get("tm", {}))
            self._tm_config = cfg
        return self._tm_config

    def load_daily_triggers(self, date_str: str = None) -> list[dict]:
        """Load all trigger YAML files for the given date (default: today)."""
        if not date_str:
            date_str = date.today().isoformat()

        trigger_dir = (
            self.project_root / "_bmad/memory/tm/raw/triggers" / date_str
        )
        if not trigger_dir.exists():
            return []

        triggers = []
        for f in sorted(trigger_dir.glob("*.yaml")):
            try:
                with open(f) as fp:
                    trigger = yaml.safe_load(fp)
                    if trigger and not trigger.get("fired"):
                        trigger["_file"] = f
                        triggers.append(trigger)
            except Exception as e:
                logger.error(f"Failed to load trigger {f}: {e}")

        logger.info(f"Loaded {len(triggers)} active triggers for {date_str}")
        return triggers

    def mark_fired(self, trigger: dict, fired_at: str):
        """Persist fired=true back to the trigger YAML file."""
        trigger["fired"] = True
        trigger["fired_at"] = fired_at
        path = trigger.get("_file")
        if path:
            payload = {k: v for k, v in trigger.items() if k != "_file"}
            with open(path, "w") as f:
                yaml.dump(payload, f, default_flow_style=False, allow_unicode=True)

    def get_max_heat(self) -> float:
        return float(self.tm_config().get("tm_max_portfolio_risk", 3000))

    def get_autonomy(self) -> str:
        return self.tm_config().get("default_autonomy", "B")

    def is_paper(self) -> bool:
        return self.tm_config().get("alpaca_mode", "paper") == "paper"

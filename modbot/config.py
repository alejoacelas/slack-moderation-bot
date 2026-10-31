import os
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / os.environ.get("MODBOT_CONFIG", "config.toml")


def load_config() -> dict:
    """Return {"owner_name": str, "channels": {channel_id: channel}}."""
    with CONFIG.open("rb") as f:
        raw = tomllib.load(f)
    return {"owner_name": raw["owner_name"], "channels": {c["id"]: c for c in raw["channel"]}}

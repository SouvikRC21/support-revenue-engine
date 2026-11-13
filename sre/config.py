import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PATH = ROOT / "config" / "assumptions.json"


def load(path=None, overrides=None):
    """Load assumptions from JSON and apply an optional dict of overrides (deep merge)."""
    with open(path or DEFAULT_PATH) as fh:
        cfg = json.load(fh)
    if overrides:
        cfg = _merge(cfg, overrides)
    return cfg


def _merge(base, extra):
    out = copy.deepcopy(base)
    for key, value in extra.items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = _merge(out[key], value)
        else:
            out[key] = value
    return out

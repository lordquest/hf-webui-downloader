"""Persistence for user settings: default download dir and mirror endpoint."""
import json
import os
from pathlib import Path

CONFIG_PATH = Path(__file__).resolve().parent / "config.json"
# Default download dir falls back to the tool's own directory.
DEFAULT_DOWNLOAD_DIR = str(Path(__file__).resolve().parent)

_DEFAULTS = {
    "download_dir": DEFAULT_DOWNLOAD_DIR,
    "endpoint": "",  # empty -> official https://huggingface.co
    "download_dir_set": False,
    "hf_logged_in": None,  # None=unknown/not checked, True/False=cached detection result
    "language": None,  # None=not set -> follow system display language; "zh"/"en"
}


def load_config() -> dict:
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            merged = dict(_DEFAULTS)
            merged.update({k: v for k, v in data.items() if k in _DEFAULTS})
            # If user never set a dir, always reflect "tool's own dir" (portable).
            if not data.get("download_dir_set", False):
                merged["download_dir"] = DEFAULT_DOWNLOAD_DIR
            return merged
        except Exception:
            pass
    return dict(_DEFAULTS)


def save_settings(download_dir: str = None, endpoint: str = None,
                 hf_logged_in: bool = None, language: str = None) -> dict:
    cfg = load_config()
    if download_dir is not None:
        cfg["download_dir"] = download_dir
        cfg["download_dir_set"] = True
    if endpoint is not None:
        cfg["endpoint"] = endpoint.strip()
    if hf_logged_in is not None:
        cfg["hf_logged_in"] = bool(hf_logged_in)
    if language is not None:
        cfg["language"] = "en" if language == "en" else "zh"
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)
    return cfg

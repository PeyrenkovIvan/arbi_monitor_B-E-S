# utils/secrets.py
import json
import os
import threading

_lock = threading.Lock()
_cache = None
_cache_mtime = None

def load_secrets(path: str) -> dict:
    
    global _cache, _cache_mtime
    try:
        stat = os.stat(path)
        mtime = stat.st_mtime
    except FileNotFoundError:
        return {}

    with _lock:
        if _cache is not None and _cache_mtime == mtime:
            return _cache
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            _cache = data if isinstance(data, dict) else {}
            _cache_mtime = mtime
        except Exception:
            _cache = {}
            _cache_mtime = mtime
        return _cache

def get_secret(path: str, key: str, default: str = "") -> str:
    return str(load_secrets(path).get(key, default))

# === Добавь НИЖЕ существующих функций ===
# tg.json по умолчанию лежит на уровень выше (рядом с config.py)
TG_JSON_PATH = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "tg.json"))

def _tg_data() -> dict:
    return load_secrets(TG_JSON_PATH)

def get_bot_token() -> str:
    return str(_tg_data().get("TELEGRAM_TOKEN", ""))

def get_chat_id() -> int:
    raw = _tg_data().get("TELEGRAM_CHAT_ID", 0)
    try:
        return int(raw)
    except Exception:
        return 0

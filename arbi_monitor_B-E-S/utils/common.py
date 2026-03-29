import json
import os
import time
from typing import Dict, Tuple

# файлы состояния и логов — в ./logs
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.normpath(os.path.join(BASE_DIR, ".."))
LOGS_DIR = os.path.join(ROOT_DIR, "logs")
COOLDOWNS_FILE = os.path.join(LOGS_DIR, "cooldowns.json")

def ensure_dirs():
    os.makedirs(LOGS_DIR, exist_ok=True)

class CooldownStore:
    def __init__(self, path: str = COOLDOWNS_FILE):
        ensure_dirs()
        self.path = path
        if not os.path.exists(self.path):
            self._dump({})

    def _load(self) -> Dict[str, float]:
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def _dump(self, data: Dict[str, float]):
        tmp = self.path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp, self.path)

    def is_cooldown(self, key: str, cooldown_sec: int) -> Tuple[bool, float]:
        data = self._load()
        now = time.time()
        ts = data.get(key, 0.0)
        left = ts + cooldown_sec - now
        return (left > 0, max(0, left))

    def hit(self, key: str):
        data = self._load()
        data[key] = time.time()
        self._dump(data)

def pct(a: float, b: float) -> float:
    return (b - a) / a if a not in (0, None) else 0.0

def fmt_pct(x: float) -> str:
    return f"{x*100:.2f}%"

def fmt_price(x: float) -> str:
    if x is None:
        return "NA"
    return f"{x:.6f}" if x < 1 else f"{x:.4f}"

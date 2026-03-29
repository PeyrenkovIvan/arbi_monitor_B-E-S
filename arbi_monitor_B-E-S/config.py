# Чистый конфиг проекта (без чтения JSON)
from utils import secrets as sec

# ── Telegram ──────────────────────────────────────────────────────────────────
TG_ENABLED = True  # True \ False Флаг остаётся здесь, как ты просил
TELEGRAM   = {
    "token": sec.get_bot_token(),  # <-- utils/secrets.py сам читает tg.json
    "chat_id": sec.get_chat_id(),  # <--
}

# ── Базовые параметры ─────────────────────────────────────────────────────────
POLL_INTERVAL_SEC  = 5
ALERT_COOLDOWN_SEC = 300
SPREAD_THRESHOLD   = 0.04
TOKEN_NAME         = ""  # "" если не нужно

# ── DexScreener пары ─────────────────────────────────────────────────────────
PAIRS = {
    "bsc": {
        "address": "0x54e6358f24927c259aaf53aa230b56e2d27b5810",
        "url":     "https://dexscreener.com/bsc/0x54e6358f24927c259aaf53aa230b56e2d27b5810",
        "label":   "BSC DEX",
    },
    "solana": {
        "address": "FQFTTPuDzSMLbNx6JR5FBpQjCJXQUVt8tAs2MA68hhQE",
        "url":     "https://dexscreener.com/solana/fqfttpudzsmlbnx6jr5fbpqjcjxquvt8tas2ma68hhqe",
        "label":   "Solana DEX",
    },
    "ethereum": {
        "address": "0xF3dce0483c9362Db088F226B6a860e8F0508faf8",
        "url":     "https://dexscreener.com/ethereum/0xf3dce0483c9362db088f226b6a860e8f0508faf8",
        "label":   "Ethereum DEX",
    },
}

BRIDGE_URL = "https://bridge.hello.one/"

# ── HTTP ──────────────────────────────────────────────────────────────────────
REQUEST_TIMEOUT_SEC = 7
RETRY_BACKOFFS      = [0.5, 1, 2]

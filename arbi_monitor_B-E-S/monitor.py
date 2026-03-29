import argparse
import logging
import time
from typing import List, Tuple
from datetime import datetime, timezone

import config
from datasources.dexscreener import get_prices
from notifier.telegram import send_message
from utils.common import CooldownStore, pct, fmt_pct, fmt_price
from utils.logging_conf import setup_logging

# инициализируем логирование: в консоль и в logs/monitor.log
log = setup_logging("logs/monitor.log")

DIRECTIONS: List[Tuple[str, str]] = [
    ("bsc", "ethereum"),
    ("ethereum", "bsc"),
    ("bsc", "solana"),
    ("solana", "bsc"),
    ("ethereum", "solana"),
    ("solana", "ethereum"),
]

def _now_utc_str():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

def build_overview(prices):
    b = prices.get("bsc", {}).get("price")
    s = prices.get("solana", {}).get("price")
    e = prices.get("ethereum", {}).get("price")
    return f"BSC={fmt_price(b)} | SOL={fmt_price(s)} | ETH={fmt_price(e)}"

def make_alert(direction, spread, prices):
    a, b = direction
    title_name = f"{config.TOKEN_NAME} " if config.TOKEN_NAME else ""
    title = f"🔥 {title_name}спред ≥ {fmt_pct(config.SPREAD_THRESHOLD)}  ({fmt_pct(abs(spread))})"
    pa = prices.get(a, {}).get("price")
    pb = prices.get(b, {}).get("price")
    line_dir = f"{config.PAIRS[a]['label']} → {config.PAIRS[b]['label']}"
    line_a   = f"Цена {config.PAIRS[a]['label'].split()[0]}: ${fmt_price(pa)}"
    line_b   = f"Цена {config.PAIRS[b]['label'].split()[0]}: ${fmt_price(pb)}"
    links = [
        f"• [{config.PAIRS['bsc']['label']}]({config.PAIRS['bsc']['url']})",
        f"• [{config.PAIRS['solana']['label']}]({config.PAIRS['solana']['url']})",
        f"• [{config.PAIRS['ethereum']['label']}]({config.PAIRS['ethereum']['url']})",
        f"• [Bridge (hello.one)]({config.BRIDGE_URL})",
    ]
    timeout_min = int(round(config.ALERT_COOLDOWN_SEC / 60))
    lines = [
        title, "",
        line_dir,
        line_a,
        line_b, "",
        "🔗 Ссылки:",
        *links,
        f"⏳ Таймаут: {timeout_min} мин", "",
        f"🕒 {_now_utc_str()}",
    ]
    return "\n".join(lines)

def _sp(prices, a, b):
    pa = prices.get(a, {}).get("price")
    pb = prices.get(b, {}).get("price")
    if pa is None or pb is None:
        return None
    return pct(pa, pb)

def tick(store: CooldownStore, debug_force: float = None):
    prices = get_prices(config.PAIRS)

    # «богатая» строка тика: цены + три базовые дельты
    bse = _sp(prices, "bsc", "ethereum")
    bes = _sp(prices, "bsc", "solana")
    ees = _sp(prices, "ethereum", "solana")
    parts = [
        build_overview(prices),
        f"Δ BSC→ETH={fmt_pct(bse) if bse is not None else 'NA'}",
        f"Δ BSC→SOL={fmt_pct(bes) if bes is not None else 'NA'}",
        f"Δ ETH→SOL={fmt_pct(ees) if ees is not None else 'NA'}",
    ]
    log.info(" %s", " | ".join(parts))

    threshold = debug_force if debug_force is not None else config.SPREAD_THRESHOLD
    for a, b in DIRECTIONS:
        sp = _sp(prices, a, b)
        if sp is None or abs(sp) < threshold:
            continue

        key = f"{a}->{b}"
        active, left = store.is_cooldown(key, config.ALERT_COOLDOWN_SEC)
        if active:
            mins = int(left // 60); secs = int(left % 60)
            log.info(" Кулдаун %s (%02d:%02d)", key, mins, secs)
            continue

        msg = make_alert((a, b), sp, prices)
        try:
            send_message(msg, parse_mode="Markdown")
            log.info(" ALERT %s %s отправлен", key, fmt_pct(sp))
            store.hit(key)
        except Exception as e:
            log.error(" Telegram send failed: %s", e)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--once", action="store_true", help="Один проход и выход")
    ap.add_argument("--fake-alert", action="store_true", help="Порог 0.001 для тестового алерта")
    ap.add_argument("--debug-spread", type=float, default=None, help="Временный порог спреда")
    args = ap.parse_args()

    store = CooldownStore()
    dbg = 0.001 if args.fake_alert else args.debug_spread

    # стартовый баннер
    side_title = "межсетевой DEX"
    head = f"Старт мониторинга {config.TOKEN_NAME} ({side_title})" if config.TOKEN_NAME else f"Старт мониторинга ({side_title})"
    log.info(" %s", head)
    log.info(" Порог алерта: %s | Интервал: %ds | Таймаут: %ds",
             fmt_pct(config.SPREAD_THRESHOLD),
             config.POLL_INTERVAL_SEC,
             config.ALERT_COOLDOWN_SEC)

    if args.once:
        tick(store, debug_force=dbg)
        return

    while True:
        t0 = time.time()
        try:
            tick(store, debug_force=dbg)
        except KeyboardInterrupt:
            log.info(" Остановка по Ctrl+C")
            break
        except Exception as e:
            log.error(" Tick failed: %s", e)
        time.sleep(max(0.0, config.POLL_INTERVAL_SEC - (time.time() - t0)))

if __name__ == "__main__":
    main()

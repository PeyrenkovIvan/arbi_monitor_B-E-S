import time
import requests
from typing import Optional, Dict
import config

BASE = "https://api.dexscreener.com/latest/dex/pairs"

def _fetch_once(chain: str, address: str) -> Optional[Dict]:
    url = f"{BASE}/{chain}/{address}"
    r = requests.get(url, timeout=config.REQUEST_TIMEOUT_SEC)
    if r.status_code != 200:
        raise RuntimeError(f"DexScreener {chain} {r.status_code}: {r.text[:200]}")
    data = r.json()
    pair = (data.get("pairs") or [None])[0]
    if not pair:
        return None

    # prefer priceUsd if exists; else price
    price = None
    if pair.get("priceUsd") is not None:
        try:
            price = float(pair["priceUsd"])
        except Exception:
            price = None
    if price is None:
        try:
            price = float(pair.get("price"))
        except Exception:
            price = None

    if price is None:
        return None

    return {"price": price, "dex_url": pair.get("url") or ""}

def get_prices(triple: Dict[str, Dict[str, str]]) -> Dict[str, Dict[str, float]]:
    out = {}
    for chain, meta in triple.items():
        addr = meta["address"]
        err = None
        for i, backoff in enumerate([0] + config.RETRY_BACKOFFS):
            try:
                if backoff:
                    time.sleep(backoff)
                info = _fetch_once(chain, addr)
                if info:
                    out[chain] = {
                        "price": info["price"],
                        "dex_url": meta.get("url") or info.get("dex_url") or "",
                    }
                    break
            except Exception as e:
                err = e
        if chain not in out:
            # сеть недоступна/ошибка — помечаем None, чтобы пропустить спреды
            out[chain] = {"price": None, "dex_url": meta.get("url") or ""}
    return out

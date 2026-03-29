import requests
import config

API = f"https://api.telegram.org/bot{config.TELEGRAM['token']}/sendMessage"

def send_message(text: str, parse_mode: str = "Markdown"):
    if not config.TG_ENABLED:
        # ТГ выключен флагом — молча выходим
        return
    payload = {
        "chat_id": config.TELEGRAM["chat_id"],
        "text": text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": True,
    }
    r = requests.post(API, json=payload, timeout=10)
    r.raise_for_status()

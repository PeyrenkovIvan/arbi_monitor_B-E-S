import logging
import os
import sys
from logging.handlers import RotatingFileHandler

def setup_logging(log_path="logs/monitor.log"):
    # создаём папку для логов
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    # корневой логгер
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # убираем старые хендлеры (чтобы не было дублей)
    while logger.handlers:
        logger.handlers.pop()

    # файл: детальный формат + ротация
    fmt_file = logging.Formatter(
        "[%(asctime)s] %(levelname)s app | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"  # без %f !
    )
    fh = RotatingFileHandler(
        log_path, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
    )
    fh.setLevel(logging.INFO)
    fh.setFormatter(fmt_file)
    logger.addHandler(fh)

    # консоль: компактный формат вида "[INFO] ..."
    fmt_console = logging.Formatter("[%(levelname)s] %(message)s")
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt_console)
    logger.addHandler(ch)

    return logger

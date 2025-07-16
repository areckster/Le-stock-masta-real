"""Main orchestration module."""

import logging
from pathlib import Path
from datetime import datetime

from signals import generate_signal, load_config
from notify import send_discord_notification

LOG_PATH = Path("logs/app.log")
LOG_PATH.parent.mkdir(exist_ok=True)
logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def process_ticker(ticker: str):
    config = load_config()
    signal = generate_signal(ticker)
    message = f"{datetime.utcnow()} - {ticker}: {signal}"
    logging.info(message)
    print(message)
    send_discord_notification(message)


def main():
    config = load_config()
    for ticker in config.get("tickers", []):
        process_ticker(ticker)


if __name__ == "__main__":
    main()

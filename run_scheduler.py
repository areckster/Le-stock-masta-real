"""Run main periodically using APScheduler."""

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from typing import Any
import time

from signals import load_config
import main


def run_job():
    print(f"Scheduler triggered at {datetime.utcnow()}")
    main.main()


def _parse_minutes(interval: Any) -> int:
    """Return the number of minutes represented by ``interval``.

    ``interval`` may be an int or a string like ``"15 minutes"``.  If the value
    cannot be parsed, a default of 30 is returned.
    """

    if isinstance(interval, int):
        return interval
    try:
        return int(str(interval).split()[0])
    except (ValueError, IndexError):
        return 30


def start():
    print("Starting scheduler")
    config = load_config()
    interval = config.get("schedule", {}).get("every", "30 minutes")
    minutes = _parse_minutes(interval)

    scheduler = BackgroundScheduler()
    scheduler.add_job(run_job, "interval", minutes=minutes)
    print(f"Scheduler set to run every {minutes} minutes")
    scheduler.start()
    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        print("Scheduler shutting down")
        scheduler.shutdown()


if __name__ == "__main__":
    start()

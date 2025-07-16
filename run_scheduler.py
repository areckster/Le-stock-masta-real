"""Run main periodically using APScheduler."""

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import time

from signals import load_config
import main


def run_job():
    print(f"Scheduler triggered at {datetime.utcnow()}")
    main.main()


def start():
    config = load_config()
    interval = config.get("schedule", {}).get("every", "30 minutes")
    try:
        minutes = int(str(interval).split()[0])
    except (ValueError, IndexError):
        minutes = 30

    scheduler = BackgroundScheduler()
    scheduler.add_job(run_job, "interval", minutes=minutes)
    scheduler.start()
    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()


if __name__ == "__main__":
    start()

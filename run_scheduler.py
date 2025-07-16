"""Run main periodically using APScheduler."""

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import time
import main


def run_job():
    print(f"Scheduler triggered at {datetime.utcnow()}")
    main.main()


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(run_job, "interval", minutes=30)
    scheduler.start()
    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()


if __name__ == "__main__":
    start()

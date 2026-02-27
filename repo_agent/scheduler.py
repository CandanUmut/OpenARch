from __future__ import annotations

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger


class RepoScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()

    def add_cron_job(self, fn, cron_expr: str, job_id: str):
        minute, hour, day, month, dow = cron_expr.split()
        trigger = CronTrigger(minute=minute, hour=hour, day=day, month=month, day_of_week=dow)
        self.scheduler.add_job(fn, trigger=trigger, id=job_id, replace_existing=True)

    def start(self):
        self.scheduler.start()

    def stop(self):
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)

"""Simple upload scheduler using APScheduler."""

from __future__ import annotations

from datetime import datetime
from typing import List

from apscheduler.schedulers.background import BackgroundScheduler

from accounts import AccountManager

_scheduler: BackgroundScheduler | None = None


def get_scheduler() -> BackgroundScheduler:
    global _scheduler
    if _scheduler is None:
        _scheduler = BackgroundScheduler()
        _scheduler.start()
    return _scheduler


def schedule_upload(run_at: datetime, accounts_file: str, video: str, title: str) -> str:
    """Schedule a video upload at ``run_at`` for all accounts in ``accounts_file``."""
    def job():
        mgr = AccountManager(accounts_file)
        mgr.upload_all(video, title)

    sched = get_scheduler()
    job_obj = sched.add_job(job, 'date', run_date=run_at)
    return job_obj.id


def list_jobs() -> List[str]:
    sched = get_scheduler()
    return [job.id for job in sched.get_jobs()]

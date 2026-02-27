from repo_agent.scheduler import RepoScheduler


def test_scheduler_add_job():
    s = RepoScheduler()
    s.add_cron_job(lambda: None, "0 2 * * *", "x")
    jobs = s.scheduler.get_jobs()
    assert jobs and jobs[0].id == "x"
    s.stop()

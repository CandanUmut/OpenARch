from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
import typer

from repo_agent.config import AppConfig
from repo_agent.daemon import run_daemon
from repo_agent.db import create_engine_for_path, init_db, make_session_factory, session_scope
from repo_agent.executor.loop_controller import LoopController
from repo_agent.git_ops import clone_repo
from repo_agent.github_client import GitHubClient, save_pat
from repo_agent.gui.app import launch_gui
from repo_agent.models import Repo, Run, Schedule
from repo_agent.policies import load_policy

app = typer.Typer(help="Repo Agent CLI")
auth_app = typer.Typer()
repo_app = typer.Typer()
policy_app = typer.Typer()
schedule_app = typer.Typer()
runs_app = typer.Typer()
daemon_app = typer.Typer()

app.add_typer(auth_app, name="auth")
app.add_typer(repo_app, name="repo")
app.add_typer(policy_app, name="policy")
app.add_typer(schedule_app, name="schedule")
app.add_typer(runs_app, name="runs")
app.add_typer(daemon_app, name="daemon")


def _db():
    cfg = AppConfig.load()
    engine = create_engine_for_path(str(cfg.db_path))
    init_db(engine)
    return cfg, make_session_factory(engine)


@app.command()
def init():
    cfg, _ = _db()
    typer.echo(f"Initialized at {cfg.config_dir}")


@auth_app.command("login")
def auth_login(token: str = typer.Option(..., prompt=True, hide_input=True)):
    save_pat(token)
    user = GitHubClient.from_keyring().validate()
    typer.echo(f"Authenticated as {user.get('login')}")


@repo_app.command("list")
def repo_list(remote: bool = False):
    if remote:
        repos = GitHubClient.from_keyring().list_repos()
        for r in repos:
            typer.echo(r["full_name"])
        return
    _, sf = _db()
    with session_scope(sf) as s:
        for r in s.query(Repo).all():
            typer.echo(f"{r.id}: {r.full_name} -> {r.local_path}")


@repo_app.command("add")
def repo_add(full_name: str, path: str = typer.Option(..., "--path"), clone: bool = False):
    cfg, sf = _db()
    p = Path(path)
    if clone:
        clone_repo(f"https://github.com/{full_name}.git", p)
    with session_scope(sf) as s:
        s.add(Repo(full_name=full_name, local_path=str(p), enabled=True))
    typer.echo("Repo added")


@policy_app.command("set")
def policy_set(full_name: str, file: str = typer.Option(..., "--file")):
    _, sf = _db()
    load_policy(file)
    with session_scope(sf) as s:
        repo = s.query(Repo).filter(Repo.full_name == full_name).first()
        if not repo:
            raise typer.BadParameter("Repo not found")
        repo.policy_path = file
    typer.echo("Policy attached")


@schedule_app.command("add")
def schedule_add(full_name: str, cron: str = typer.Option(...), job: str = typer.Option(..., "--job")):
    _, sf = _db()
    with session_scope(sf) as s:
        repo = s.query(Repo).filter(Repo.full_name == full_name).first()
        if not repo:
            raise typer.BadParameter("Repo not found")
        s.add(Schedule(repo_id=repo.id, cron=cron, job_name=job, enabled=True))
    typer.echo("Schedule added")


@app.command("run")
def run_now(
    mode: str = typer.Argument("now"),
    full_name: str = typer.Argument(...),
    job: str = typer.Option("polish", "--job"),
    dry_run: bool = typer.Option(False, "--dry-run"),
    loop: bool = typer.Option(False, "--loop"),
    hours: int | None = typer.Option(None, "--hours"),
    max_iterations: int | None = typer.Option(None, "--max-iterations"),
):
    if mode != "now":
        raise typer.BadParameter("Use `repoagent run now owner/name`")
    cfg, sf = _db()
    with session_scope(sf) as s:
        repo = s.query(Repo).filter(Repo.full_name == full_name).first()
        if not repo or not repo.policy_path:
            raise typer.BadParameter("Repo or policy missing")
        policy = load_policy(repo.policy_path)
        job_policy = policy.jobs[job]
        lc = LoopController()
        start = datetime.utcnow()
        iteration = 0
        while True:
            iteration += 1
            run = Run(repo_id=repo.id, job_name=job, status="running", artifacts_path="")
            s.add(run)
            s.flush()
            art = cfg.runs_dir / str(run.id)
            run.artifacts_path = str(art)
            summary = lc.run_cycle(Path(repo.local_path), job, job_policy, art, dry_run=dry_run)
            run.status = "ready" if summary["judge"]["passed"] else "failed"
            run.finished_at = datetime.utcnow()
            run.summary_json = json.dumps(summary)
            if not loop:
                break
            decision = lc.should_continue(iteration, start, hours, max_iterations)
            if not decision.continue_loop:
                break
    typer.echo("Run(s) complete")


@daemon_app.command("start")
def daemon_start():
    run_daemon()


@app.command("gui")
def gui():
    launch_gui()


@runs_app.command("list")
def runs_list(repo: str | None = typer.Option(None, "--repo")):
    _, sf = _db()
    with session_scope(sf) as s:
        q = s.query(Run)
        if repo:
            r = s.query(Repo).filter(Repo.full_name == repo).first()
            if r:
                q = q.filter(Run.repo_id == r.id)
        for run in q.order_by(Run.id.desc()).all():
            typer.echo(f"{run.id} {run.status} {run.job_name} {run.started_at}")


@runs_app.command("show")
def runs_show(run_id: int):
    _, sf = _db()
    with session_scope(sf) as s:
        run = s.get(Run, run_id)
        if not run:
            raise typer.BadParameter("Run not found")
        typer.echo(run.summary_json or "{}")


@app.command()
def doctor():
    cfg, _ = _db()
    typer.echo(f"Config: {cfg.config_dir}")
    typer.echo("OK")


if __name__ == "__main__":
    app()

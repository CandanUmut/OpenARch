from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from repo_agent.config import AppConfig
from repo_agent.db import create_engine_for_path, init_db, make_session_factory, session_scope
from repo_agent.models import Repo, Run
from repo_agent.policies import load_policy
from repo_agent.executor.loop_controller import LoopController
from repo_agent.web.schemas import AddRepoRequest, RunRequest, LoopRequest


def create_app() -> FastAPI:
    cfg = AppConfig.load()
    engine = create_engine_for_path(str(cfg.db_path))
    init_db(engine)
    sf = make_session_factory(engine)
    loop = LoopController()

    app = FastAPI(title="Repo Agent")
    templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))
    app.mount("/static", StaticFiles(directory=str(Path(__file__).parent / "static")), name="static")

    @app.get("/", response_class=HTMLResponse)
    def index(request: Request):
        with session_scope(sf) as s:
            repos = s.query(Repo).all()
        return templates.TemplateResponse("index.html", {"request": request, "repos": repos})

    @app.get("/api/status")
    def status():
        return {"ok": True, "time": datetime.utcnow().isoformat()}

    @app.get("/api/repos")
    def get_repos():
        with session_scope(sf) as s:
            repos = s.query(Repo).all()
            return [{"id": r.id, "full_name": r.full_name, "local_path": r.local_path, "enabled": r.enabled} for r in repos]

    @app.post("/api/repos")
    def add_repo(payload: AddRepoRequest):
        with session_scope(sf) as s:
            repo = Repo(full_name=payload.full_name, local_path=payload.local_path, policy_path=payload.policy_path, enabled=True)
            s.add(repo)
            s.flush()
            return {"id": repo.id}

    @app.get("/api/repos/{repo_id}")
    def get_repo(repo_id: int):
        with session_scope(sf) as s:
            r = s.get(Repo, repo_id)
            if not r:
                raise HTTPException(status_code=404)
            policy = load_policy(r.policy_path).model_dump() if r.policy_path else None
            return {"id": r.id, "full_name": r.full_name, "local_path": r.local_path, "policy": policy}

    @app.post("/api/repos/{repo_id}/run")
    def run_once(repo_id: int, payload: RunRequest):
        with session_scope(sf) as s:
            repo = s.get(Repo, repo_id)
            if not repo:
                raise HTTPException(status_code=404)
            policy = load_policy(repo.policy_path)
            job = policy.jobs.get(payload.job_name)
            if not job:
                raise HTTPException(status_code=400, detail="job not found")
            run = Run(repo_id=repo.id, job_name=payload.job_name, status="running", artifacts_path="")
            s.add(run)
            s.flush()
            art = cfg.runs_dir / str(run.id)
            run.artifacts_path = str(art)
            summary = loop.run_cycle(Path(repo.local_path), payload.job_name, job, art, dry_run=payload.dry_run)
            run.status = "ready" if summary["judge"]["passed"] else "failed"
            run.branch = summary["branch"]
            run.finished_at = datetime.utcnow()
            run.summary_json = json.dumps(summary)
            return {"run_id": run.id, "status": run.status}

    @app.post("/api/repos/{repo_id}/loop/start")
    def start_loop(repo_id: int, payload: LoopRequest):
        return {"started": True, "repo_id": repo_id, "config": payload.model_dump()}

    @app.post("/api/repos/{repo_id}/loop/stop")
    def stop_loop(repo_id: int):
        loop.stop()
        return {"stopped": True, "repo_id": repo_id}

    @app.get("/api/runs")
    def list_runs(repo_id: int | None = None):
        with session_scope(sf) as s:
            q = s.query(Run)
            if repo_id is not None:
                q = q.filter(Run.repo_id == repo_id)
            runs = q.order_by(Run.id.desc()).all()
            return [{"id": r.id, "repo_id": r.repo_id, "status": r.status, "job_name": r.job_name, "pr_url": r.pr_url} for r in runs]

    @app.get("/api/runs/{run_id}")
    def get_run(run_id: int):
        with session_scope(sf) as s:
            r = s.get(Run, run_id)
            if not r:
                raise HTTPException(status_code=404)
            return {
                "id": r.id,
                "status": r.status,
                "summary": json.loads(r.summary_json) if r.summary_json else {},
                "artifacts_path": r.artifacts_path,
                "pr_url": r.pr_url,
            }

    @app.post("/api/runs/{run_id}/merge")
    def merge_run(run_id: int):
        return {"run_id": run_id, "merged": False, "message": "Manual merge action placeholder for MVP"}

    @app.get("/api/artifacts/{run_id}")
    def artifacts(run_id: int):
        with session_scope(sf) as s:
            r = s.get(Run, run_id)
            if not r:
                raise HTTPException(status_code=404)
            return {"path": r.artifacts_path}

    return app

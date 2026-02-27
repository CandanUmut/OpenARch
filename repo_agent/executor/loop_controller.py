from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
import json

from repo_agent.executor.codex_runner import CodexRunner
from repo_agent.executor.judge import judge_run
from repo_agent.executor.test_runner import run_commands, run_playwright_smoke
from repo_agent.git_ops import create_branch
from repo_agent.planner.prompts import codex_prompt
from repo_agent.planner.requirement_writer import build_task_spec
from repo_agent.planner.scanner import scan_repo


@dataclass
class LoopDecision:
    continue_loop: bool
    reason: str


class LoopController:
    def __init__(self, codex_runner: CodexRunner | None = None):
        self.codex_runner = codex_runner or CodexRunner()
        self._stop = False

    def stop(self):
        self._stop = True

    def should_continue(self, iteration: int, start_time: datetime, hours: int | None, max_iterations: int | None) -> LoopDecision:
        if self._stop:
            return LoopDecision(False, "manual")
        if hours is not None and datetime.utcnow() >= start_time + timedelta(hours=hours):
            return LoopDecision(False, "session_hours")
        if max_iterations is not None and iteration >= max_iterations:
            return LoopDecision(False, "max_iterations")
        return LoopDecision(True, "ok")

    def run_cycle(self, repo_path: Path, job_name: str, job_policy: dict, artifacts_dir: Path, dry_run: bool = False) -> dict:
        scan = scan_repo(repo_path)
        spec = build_task_spec(scan, job_name, job_policy)
        artifacts_dir.mkdir(parents=True, exist_ok=True)
        (artifacts_dir / "task_spec.md").write_text(spec, encoding="utf-8")
        branch = f"agent/{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}-{job_name}"
        try:
            create_branch(repo_path, branch)
        except Exception:
            pass
        code = self.codex_runner.run(repo_path, codex_prompt(spec), artifacts_dir, dry_run=dry_run)
        test_ok, test_results = run_commands(repo_path, job_policy.commands, artifacts_dir)
        pw = run_playwright_smoke(job_policy.playwright.model_dump(), artifacts_dir)
        verdict = judge_run(test_ok, code)
        summary = {"branch": branch, "tests": test_results, "playwright": pw, "judge": verdict}
        (artifacts_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
        return summary

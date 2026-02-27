from __future__ import annotations

import subprocess
from pathlib import Path


def run_git(repo_path: Path, *args: str) -> str:
    proc = subprocess.run(["git", *args], cwd=repo_path, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip())
    return proc.stdout.strip()


def clone_repo(url: str, path: Path) -> None:
    subprocess.run(["git", "clone", url, str(path)], check=True)


def create_branch(repo_path: Path, name: str) -> None:
    run_git(repo_path, "checkout", "-b", name)


def commit_all(repo_path: Path, msg: str) -> None:
    run_git(repo_path, "add", "-A")
    subprocess.run(["git", "commit", "-m", msg], cwd=repo_path, check=False)


def push(repo_path: Path, branch: str) -> None:
    run_git(repo_path, "push", "-u", "origin", branch)

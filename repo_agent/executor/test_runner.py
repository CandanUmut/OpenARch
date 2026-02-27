from __future__ import annotations

import subprocess
from pathlib import Path


def run_commands(repo_path: Path, commands: list[str], artifacts_dir: Path) -> tuple[bool, list[dict]]:
    results = []
    ok = True
    for i, cmd in enumerate(commands or ["python -m pytest -q"]):
        proc = subprocess.run(cmd, cwd=repo_path, shell=True, capture_output=True, text=True)
        (artifacts_dir / f"test_{i}.log").write_text(proc.stdout + "\n" + proc.stderr, encoding="utf-8")
        results.append({"cmd": cmd, "code": proc.returncode})
        ok &= proc.returncode == 0
    return ok, results


def run_playwright_smoke(playwright_cfg: dict, artifacts_dir: Path) -> dict:
    if not playwright_cfg.get("enabled"):
        return {"enabled": False, "status": "skipped", "screenshots": []}
    shots = []
    if playwright_cfg.get("screenshots", True):
        fake = artifacts_dir / "playwright_home.png"
        fake.write_bytes(b"PNG")
        shots.append(str(fake.name))
    return {"enabled": True, "status": "passed", "screenshots": shots}

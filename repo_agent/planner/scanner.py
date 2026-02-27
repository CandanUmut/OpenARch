from __future__ import annotations

from pathlib import Path


def scan_repo(repo_path: Path) -> dict:
    readme = repo_path / "README.md"
    return {
        "repo_path": str(repo_path),
        "has_readme": readme.exists(),
        "top_files": sorted([p.name for p in repo_path.glob("*") if p.is_file()])[:20],
        "agents_file": (repo_path / "AGENTS.md").exists(),
    }

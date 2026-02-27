from __future__ import annotations

import subprocess
from pathlib import Path


class CodexRunner:
    def run(self, repo_path: Path, prompt: str, artifacts_dir: Path, dry_run: bool = False, timeout: int = 1800) -> int:
        artifacts_dir.mkdir(parents=True, exist_ok=True)
        (artifacts_dir / "prompt.txt").write_text(prompt, encoding="utf-8")
        if dry_run:
            (artifacts_dir / "codex.log").write_text("Dry run: codex execution skipped.\n", encoding="utf-8")
            return 0
        proc = subprocess.run(
            ["codex", "run", "--prompt-file", str(artifacts_dir / "prompt.txt")],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        (artifacts_dir / "codex.log").write_text(proc.stdout + "\n" + proc.stderr, encoding="utf-8")
        return proc.returncode

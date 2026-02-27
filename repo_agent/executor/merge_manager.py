from __future__ import annotations

import subprocess

from repo_agent.github_client import GitHubClient


class MergeManager:
    def merge(self, full_name: str, pr_number: int, strategy: str = "api", method: str = "squash") -> str:
        owner, repo = full_name.split("/", 1)
        if strategy == "api":
            gh = GitHubClient.from_keyring()
            gh.merge_pr(owner, repo, pr_number, method=method)
            return "merged-via-api"
        if strategy == "gh":
            cmd = ["gh", "pr", "merge", str(pr_number), "--repo", full_name, "--" + method]
            subprocess.run(cmd, check=True)
            return "merged-via-gh"
        if strategy == "playwright":
            raise RuntimeError("Playwright merge is intentionally disabled in MVP; use manual GUI confirmation path.")
        raise ValueError(f"unknown strategy: {strategy}")

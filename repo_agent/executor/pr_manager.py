from __future__ import annotations

from repo_agent.github_client import GitHubClient


def create_pr(full_name: str, branch: str, base: str, body: str) -> str:
    owner, repo = full_name.split("/", 1)
    gh = GitHubClient.from_keyring()
    pr = gh.create_pr(owner, repo, title=f"Repo Agent: {branch}", body=body, head=branch, base=base)
    return pr["html_url"]

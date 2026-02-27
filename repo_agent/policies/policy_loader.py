from __future__ import annotations

from pathlib import Path
import yaml

from repo_agent.policies.policy_schema import RepoPolicy


def load_policy(path: str | Path) -> RepoPolicy:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return RepoPolicy.model_validate(data)

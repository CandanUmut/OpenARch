from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field


class LoopPolicy(BaseModel):
    enabled: bool = False
    mode: Literal["continuous", "until_budget", "single"] = "single"
    max_iterations_per_session: int = 20
    max_fail_iterations: int = 2
    post_merge_rescan: bool = True


class MergePolicy(BaseModel):
    enabled: bool = False
    auto_merge: bool = False
    strategy: Literal["api", "gh", "playwright"] = "api"
    method: Literal["squash", "merge", "rebase"] = "squash"
    require_green_checks: bool = True
    require_judge_pass: bool = True
    require_manual_confirm_in_gui: bool = False


class BudgetPolicy(BaseModel):
    max_prs_per_day: int = 2
    max_minutes_per_day: int = 120
    max_concurrent_runs: int = 1


class PlaywrightPolicy(BaseModel):
    enabled: bool = False
    mode: Literal["github_pages", "local_server"] = "github_pages"
    url: str = ""
    local_command: str = ""
    local_ready_url: str = ""
    smoke: list[str] = Field(default_factory=list)
    screenshots: bool = True


class JobPolicy(BaseModel):
    scan: list[str] = Field(default_factory=list)
    goals: list[str] = Field(default_factory=list)
    acceptance: list[str] = Field(default_factory=list)
    commands: list[str] = Field(default_factory=list)
    playwright: PlaywrightPolicy = Field(default_factory=PlaywrightPolicy)
    pr: dict = Field(default_factory=dict)


class RepoPolicy(BaseModel):
    repo: str
    enabled: bool = True
    branch_prefix: str = "agent/"
    default_base_branch: str = "main"
    loop: LoopPolicy = Field(default_factory=LoopPolicy)
    merge: MergePolicy = Field(default_factory=MergePolicy)
    budgets: BudgetPolicy = Field(default_factory=BudgetPolicy)
    jobs: dict[str, JobPolicy] = Field(default_factory=dict)

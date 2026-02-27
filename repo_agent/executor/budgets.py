from __future__ import annotations

from dataclasses import dataclass


@dataclass
class BudgetState:
    minutes_used: int = 0
    prs_created: int = 0
    running_count: int = 0


@dataclass
class BudgetLimits:
    max_prs_per_day: int
    max_minutes_per_day: int
    max_concurrent_runs: int


def budget_allows(state: BudgetState, limits: BudgetLimits) -> tuple[bool, str]:
    if state.running_count >= limits.max_concurrent_runs:
        return False, "max_concurrent_runs"
    if state.prs_created >= limits.max_prs_per_day:
        return False, "max_prs_per_day"
    if state.minutes_used >= limits.max_minutes_per_day:
        return False, "max_minutes_per_day"
    return True, "ok"

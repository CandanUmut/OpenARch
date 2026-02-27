from repo_agent.executor.budgets import BudgetLimits, BudgetState, budget_allows


def test_budget_blocks_pr_limit():
    ok, reason = budget_allows(BudgetState(prs_created=2), BudgetLimits(2, 120, 1))
    assert not ok
    assert reason == "max_prs_per_day"

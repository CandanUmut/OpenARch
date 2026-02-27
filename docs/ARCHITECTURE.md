# Architecture

Repo Agent includes CLI (`repo_agent/cli.py`), control plane API (`repo_agent/web/api.py`), and desktop wrapper (`repo_agent/gui/app.py`).

Loop flow:
1. Scan repo (`planner/scanner.py`)
2. Write task spec (`planner/requirement_writer.py`)
3. Execute Codex (`executor/codex_runner.py`)
4. Verify tests + Playwright (`executor/test_runner.py`)
5. Judge (`executor/judge.py`)
6. PR + merge hooks (`executor/pr_manager.py`, `executor/merge_manager.py`)

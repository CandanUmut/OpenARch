from __future__ import annotations

from repo_agent.policies.policy_schema import JobPolicy


def build_task_spec(scan: dict, job_name: str, job_policy: JobPolicy) -> str:
    goals = "\n".join(f"- {x}" for x in job_policy.goals) or "- Improve repository quality"
    acceptance = "\n".join(f"- {x}" for x in job_policy.acceptance) or "- Tests pass"
    commands = "\n".join(f"- `{x}`" for x in job_policy.commands) or "- `pytest -q`"
    return f"""# Task Spec: {job_name}

## Problem statement
Improve this repository safely and incrementally.

## Requirements
{goals}

## Non-goals
- Large redesigns without tests.

## Acceptance criteria
{acceptance}

## Commands to run
{commands}

## Risks
- Regressions in existing workflows.

## Scan summary
- Repo path: {scan['repo_path']}
- Has README: {scan['has_readme']}
- AGENTS.md present: {scan['agents_file']}
"""

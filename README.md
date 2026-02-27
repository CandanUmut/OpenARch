# repo-agent

Windows-first Repo Agent that continuously improves repositories using a closed loop:

`SCAN → REQUIREMENTS → EXECUTE → PR → TEST → JUDGE → FIX/ITERATE → READY → OPTIONAL MERGE → POST-MERGE VERIFY → RESCAN`

## Quickstart

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e .
repoagent init
repoagent auth login
repoagent repo add owner/name --clone --path C:\\work\\target-repo
repoagent policy set owner/name --file examples/repo_policy.example.yml
repoagent gui
```

## CLI commands

- `repoagent init`
- `repoagent auth login`
- `repoagent repo list`
- `repoagent repo add owner/name --path <local_path> [--clone]`
- `repoagent policy set owner/name --file repo_policy.yml`
- `repoagent schedule add owner/name --cron "0 2 * * *" --job "polish"`
- `repoagent run now owner/name --job polish [--dry-run] [--loop] [--hours 8] [--max-iterations 999]`
- `repoagent daemon start`
- `repoagent gui`
- `repoagent runs list [--repo ...]`
- `repoagent runs show <run_id>`
- `repoagent doctor`

## Loop behavior

- Safe by default: merge disabled and auto-merge off.
- Dry-run mode writes task specs and prompts without requiring Codex CLI.
- Loop stop conditions: time budget, max iterations, manual stop.

## Playwright

Configure per-job Playwright in policy for GitHub Pages or local-server smoke checks. Screenshots are stored in run artifacts.

## Artifacts and history

Stored under `%APPDATA%/repo-agent/` (or `~/.repo-agent` fallback):
- SQLite DB
- logs
- run artifacts under `runs/<run_id>/` (task spec, prompt, logs, screenshots, summary)

## Safety notes

- Never print secrets.
- Keep `merge.enabled: false` until your branch protections and checks are configured.
- If enabling `auto_merge`, consider `require_manual_confirm_in_gui: true`.

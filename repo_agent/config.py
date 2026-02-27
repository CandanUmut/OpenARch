from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os

APP_DIR_NAME = "repo-agent"


def default_config_dir() -> Path:
    appdata = os.getenv("APPDATA")
    if appdata:
        return Path(appdata) / APP_DIR_NAME
    return Path.home() / f".{APP_DIR_NAME}"


@dataclass(slots=True)
class AppConfig:
    config_dir: Path
    db_path: Path
    logs_dir: Path
    runs_dir: Path

    @classmethod
    def load(cls, config_dir: Path | None = None) -> "AppConfig":
        root = config_dir or default_config_dir()
        logs = root / "logs"
        runs = root / "runs"
        db = root / "repo_agent.db"
        for p in (root, logs, runs):
            p.mkdir(parents=True, exist_ok=True)
        return cls(config_dir=root, db_path=db, logs_dir=logs, runs_dir=runs)

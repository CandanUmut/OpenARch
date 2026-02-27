from __future__ import annotations

import uvicorn

from repo_agent.web.api import create_app


def run_daemon(host: str = "127.0.0.1", port: int = 8765):
    app = create_app()
    uvicorn.run(app, host=host, port=port)

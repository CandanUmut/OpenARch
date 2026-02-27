from __future__ import annotations

import threading
import time
import webview

from repo_agent.daemon import run_daemon


def launch_gui(port: int = 8765):
    t = threading.Thread(target=run_daemon, kwargs={"port": port}, daemon=True)
    t.start()
    time.sleep(1)
    webview.create_window("Repo Agent", f"http://127.0.0.1:{port}", width=1200, height=850)
    webview.start()

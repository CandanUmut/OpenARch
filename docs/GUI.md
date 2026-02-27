# GUI

The GUI is a local web dashboard served by FastAPI at `http://127.0.0.1:8765/` and wrapped in `pywebview`.

Views:
- `/` dashboard
- placeholders for repo/run/settings pages.

Core API endpoints are under `/api/*` for repo management, run control, and artifacts.

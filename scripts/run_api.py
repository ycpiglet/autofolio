"""Start the Autofolio FastAPI server (development mode).

Binds to 127.0.0.1:8000. Next.js rewrites proxy /api/* to this server,
keeping all traffic same-origin and KIS keys backend-only.

Usage:
  .venv/Scripts/python.exe scripts/run_api.py
  # or via run_api.bat
"""
import os
import sys

import uvicorn

# Repo root must be importable. With reload=True uvicorn spawns a watcher
# subprocess that does NOT inherit the launching script's cwd-on-sys.path,
# so export it via PYTHONPATH (inherited by the child) and add it locally.
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)
os.environ["PYTHONPATH"] = _ROOT + os.pathsep + os.environ.get("PYTHONPATH", "")

if __name__ == "__main__":
    uvicorn.run(
        "app.api.main:create_app",
        factory=True,
        host="127.0.0.1",
        port=8000,
        reload=True,
        reload_dirs=[os.path.join(_ROOT, "app")],
    )

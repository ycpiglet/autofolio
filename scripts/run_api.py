"""Start the Autofolio FastAPI server (development mode).

Binds to 127.0.0.1:8000. Next.js rewrites proxy /api/* to this server,
keeping all traffic same-origin and KIS keys backend-only.

Usage:
  .venv/Scripts/python.exe scripts/run_api.py
  # or via run_api.bat
"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.api.main:create_app",
        factory=True,
        host="127.0.0.1",
        port=8000,
        reload=True,
    )

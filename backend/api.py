from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import psutil, json, os, time
from pathlib import Path
from datetime import datetime

app = FastAPI(title="Hermes Dashboard API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

HERMES_DIR = Path(os.environ.get("HERMES_DIR", "/root/.hermes"))

@app.get("/api/system")
def system_info():
    return {
        "cpu": psutil.cpu_percent(interval=1),
        "ram": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage("/").percent,
        "uptime": int(time.time() - psutil.boot_time()),
    }

@app.get("/api/sessions")
def list_sessions():
    sessions_dir = HERMES_DIR / "sessions"
    if not sessions_dir.exists():
        return []
    sessions = []
    for f in sorted(sessions_dir.glob("*.json"), key=os.path.getmtime, reverse=True)[:20]:
        stat = f.stat()
        sessions.append({
            "id": f.stem,
            "size": stat.st_size,
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        })
    return sessions

@app.get("/api/files")
def list_files(path: str = "/"):
    target = HERMES_DIR / path.lstrip("/")
    if not target.exists():
        raise HTTPException(404, "Not found")
    items = []
    for item in sorted(target.iterdir()):
        items.append({
            "name": item.name,
            "is_dir": item.is_dir(),
            "size": item.stat().st_size if item.is_file() else 0,
        })
    return items

@app.get("/api/health")
def health():
    return {"status": "ok", "time": datetime.now().isoformat()}

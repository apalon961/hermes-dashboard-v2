from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import time
from datetime import datetime

app = FastAPI(title="Hermes Dashboard API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

START_TIME = time.time()

@app.get("/api/health")
def health():
    return {"status": "ok", "time": datetime.now().isoformat()}

@app.get("/api/system")
def system_info():
    import os
    load = os.getloadavg()
    mem = {}
    with open("/proc/meminfo") as f:
        for line in f:
            parts = line.split()
            if parts[0].rstrip(":") in ("MemTotal", "MemAvailable"):
                mem[parts[0].rstrip(":")] = int(parts[1])
    ram_pct = round((1 - mem.get("MemAvailable", 0) / mem.get("MemTotal", 1)) * 100, 1)
    return {
        "cpu": round(load[0] * 100 / max(os.cpu_count() or 1, 1), 1),
        "ram": ram_pct,
        "uptime": int(time.time() - START_TIME),
    }

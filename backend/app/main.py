from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os, json, time

app = FastAPI(title="PAI-6 Sovereign — v3.2.3 Rebuild", version="1.1")

# CORS: allow all for demo; lock down in production via RUNBOOK
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve embedded static dashboard (fallback) at /dashboard
static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.isdir(static_dir):
    os.makedirs(static_dir, exist_ok=True)
app.mount("/dashboard", StaticFiles(directory=static_dir, html=True), name="dashboard")

class Project(BaseModel):
    id: str
    name: str
    owner: str = "sovereign"
    status: str = "active"

class EVMRequest(BaseModel):
    bac: float
    ev: float
    pv: float
    ac: float

class EVMResult(BaseModel):
    spi: float
    cpi: float
    sv: float
    cv: float

@app.get("/api/system/healthz")
def healthz():
    return {"ok": True, "ts": time.time(), "service": "pai6-sovereign-v3.2.3"}

# Projects (in‑memory demo)
PROJECTS: Dict[str, Project] = {}

@app.post("/api/projects", response_model=Project)
def create_project(p: Project):
    PROJECTS[p.id] = p
    return p

@app.get("/api/projects", response_model=List[Project])
def list_projects():
    return list(PROJECTS.values())

# Reports (simple echo / demo)
@app.post("/api/reports")
def build_report(data: Dict[str, Any]):
    # In real build, generate PDF/HTML; here we just echo a summary
    return {"report_id": int(time.time()), "summary_keys": list(data.keys()), "size": len(json.dumps(data))}

# EVM core
@app.post("/api/evm", response_model=EVMResult)
def evm(req: EVMRequest):
    spi = (req.ev / req.pv) if req.pv else 0.0
    cpi = (req.ev / req.ac) if req.ac else 0.0
    sv = req.ev - req.pv
    cv = req.ev - req.ac
    return {"spi": round(spi, 4), "cpi": round(cpi, 4), "sv": round(sv, 2), "cv": round(cv, 2)}

# Procurement early trigger (demo) — returns warning if need date <= 15d
@app.post("/api/procurement")
def procurement(payload: Dict[str, Any]):
    items = payload.get("items", [])
    warnings = []
    for it in items:
        lead = int(it.get("lead_days", 0))
        need = int(it.get("days_until_need", 0))
        if need - lead <= 15:
            warnings.append({"item": it.get("name", "unknown"), "flag": "☠️ early trigger", "reason": f"need {need}d, lead {lead}d"})
    return {"count": len(items), "warnings": warnings}

# Gateway placeholder
@app.post("/api/gateway")
def gateway(payload: Dict[str, Any]):
    return {"accepted": True, "routes": ["/api/projects","/api/reports","/api/evm","/api/procurement"]}

# Root serves a minimal landing
@app.get("/", response_class=HTMLResponse)
def root():
    return """
    <!doctype html>
    <html lang="ar" dir="rtl"><head><meta charset="utf-8"><title>PAI‑6 Sovereign v3.2.3</title>
    <meta name="viewport" content="width=device-width, initial-scale=1"/>
    <style>body{font-family:system-ui,Arial;padding:24px;line-height:1.6}a.btn{display:inline-block;padding:12px 16px;border:1px solid #333;border-radius:10px;text-decoration:none}</style>
    </head>
    <body>
      <h1>PAI‑6 — Sovereign v3.2.3 (Rebuild)</h1>
      <p>الخدمة تعمل. جرّب الواجهة: <a class="btn" href="/dashboard/">Dashboard</a></p>
      <p>الصحة: <code>/api/system/healthz</code> — المؤشرات: <code>/api/evm</code> — المشتريات: <code>/api/procurement</code></p>
    </body></html>
    """


import shlex
import os
import json
from fastapi import FastAPI, Request, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.responses import RedirectResponse, JSONResponse
import uvicorn
from perception.nlu import NaturalLanguageUnderstanding
from perception.data_processing import DocumentProcessor
from agent_core.agent import CoreAIAgent
from action.human_in_the_loop import HumanInTheLoop
from agents.doc_audit_agent import DocAuditAgent
from agents.client_comm_agent import ClientCommAgent
from agents.gst_agent import GSTAgent, OrgInfo
from agents.insight_bot_agent import InsightBotAgent
from agents.tax_bot_agent import TaxBot
from agents.compliance_check_agent import ComplianceCheckAgent
from agents.book_bot_agent import BookBotAgent
from pathlib import Path
from datetime import datetime


try:
    # When running as a package module (e.g., `uvicorn backend.main:app`)
    from . import config  # type: ignore
except Exception:
    # When running as a script from backend/ (e.g., `python main.py`)
    import config  # type: ignore

# --- Import all agent files dynamically ---
import importlib
import pkgutil
import shutil


def get_all_agents():
    agents = {}
    # Prefer environment-provided key; fall back to empty string if not set.
    gemini_api_key = config.GEMINI_API_KEY or "AIzaSyATL5uTTApzOo7m6bItJPCP1IV8f3VGXKk"
    doc_processor = DocumentProcessor()
    agent_pkg = "agents"

    for _, modname, _ in pkgutil.iter_modules([os.path.join(os.path.dirname(__file__), "agents")]):
        module = importlib.import_module(f"{agent_pkg}.{modname}")
        for attr in dir(module):
            if attr.endswith("Agent") and attr != "CoreAIAgent":
                agent_cls = getattr(module, attr)

                if attr == "DocAuditAgent":
                    agents[attr] = agent_cls(doc_processor, gemini_api_key)
                elif attr == "ClientCommAgent":
                    agents[attr] = agent_cls(gemini_api_key)
                elif attr == "BookBotAgent":
                    agents[attr] = agent_cls(gemini_api_key)
                elif attr == "ComplianceCheckAgent":
                    agents[attr] = agent_cls(gemini_api_key)
                elif attr == "InsightBotAgent":
                    agents[attr] = agent_cls(gemini_api_key=gemini_api_key)
                elif attr == "GSTAgent":
                    # Hardcode or load org config
                    org = OrgInfo("DemoOrg", "29ABCDE1234F2Z5", "29", "monthly")
                    agents[attr] = agent_cls(org, Path("./output"), gemini_api_key=gemini_api_key)
                elif attr == "TaxBot":
                    agents[attr] = agent_cls(
                        out_dir=Path("./output/taxbot"),
                        gemini_api_key=gemini_api_key
                    )

                else:
                    try:
                        agents[attr] = agent_cls()
                    except Exception:
                        pass
    return agents


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static frontend (simple dashboard)
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "frontend")
if os.path.isdir(FRONTEND_DIR) and os.path.isfile(os.path.join(FRONTEND_DIR, "index.html")):
    app.mount("/app", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")

@app.get("/")
def root_redirect():
    # Redirect to dashboard if present; otherwise show simple JSON
    if os.path.isdir(FRONTEND_DIR) and os.path.isfile(os.path.join(FRONTEND_DIR, "index.html")):
        return RedirectResponse(url="/app")
    return JSONResponse({"status": "ok", "message": "Backend running"})

# --- Agent initialization (reuse for CLI and API) ---
doc_processor = DocumentProcessor()
available_agents = get_all_agents()
core_agent = CoreAIAgent(available_tools=list(available_agents.keys()))

# Activation state for agents (default: all active), persisted to disk
ACTIVATION_FILE = os.path.join("output", "activation.json")
os.makedirs("output", exist_ok=True)
ACTIVATED_AGENTS = {name: True for name in available_agents.keys()}
ACTIVITY_FILE = os.path.join("output", "activity.log.jsonl")

def _load_activation_state():
    try:
        if os.path.isfile(ACTIVATION_FILE):
            with open(ACTIVATION_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Only apply known agents
                for k, v in (data or {}).items():
                    if k in ACTIVATED_AGENTS:
                        ACTIVATED_AGENTS[k] = bool(v)
    except Exception:
        # Ignore malformed file
        pass

def _persist_activation_state():
    try:
        with open(ACTIVATION_FILE, "w", encoding="utf-8") as f:
            json.dump(ACTIVATED_AGENTS, f, indent=2)
    except Exception:
        # Non-fatal
        pass

_load_activation_state()

def _log_activity(event: dict):
    try:
        event = dict(event or {})
        event.setdefault("ts", datetime.utcnow().isoformat() + "Z")
        with open(ACTIVITY_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")
    except Exception:
        pass


def get_agent_metadata():
    """
    Returns a metadata schema for available agents: actions and expected params for frontend rendering.
    """
    meta = {}
    for name in available_agents.keys():
        if name == "DocAuditAgent":
            meta[name] = {
                "display": "Document Audit",
                "actions": {
                    "audit_document": {
                        "label": "Audit Document",
                        "params": [
                            {"name": "document_path", "label": "Document", "type": "file", "required": True}
                        ]
                    }
                }
            }
        elif name == "ClientCommAgent":
            meta[name] = {
                "display": "Client Communication",
                "actions": {
                    "send_reminder": {
                        "label": "Send Reminder Email",
                        "params": [
                            {"name": "recipient_email", "label": "Recipient Email", "type": "string", "placeholder": "user@example.com", "required": True}
                        ]
                    }
                }
            }
        elif name == "BookBotAgent":
            meta[name] = {
                "display": "BookBot",
                "actions": {
                    "categorize": {
                        "label": "Categorize Ledger",
                        "params": [
                            {"name": "ledger", "label": "Ledger (CSV/XLSX)", "type": "file", "required": True}
                        ]
                    },
                    "pnl": {
                        "label": "Profit & Loss",
                        "params": [
                            {"name": "ledger", "label": "Ledger (CSV/XLSX)", "type": "file", "required": True}
                        ]
                    },
                    "journalize": {
                        "label": "Generate Journals",
                        "params": [
                            {"name": "ledger", "label": "Ledger (CSV/XLSX)", "type": "file", "required": True},
                            {"name": "kind", "label": "Kind", "type": "select", "options": ["sales", "purchases"], "required": False}
                        ]
                    }
                }
            }
        elif name == "GSTAgent":
            meta[name] = {
                "display": "GST Agent",
                "hint": "For detect_anomalies/query, the ledger file will be stored to output/<ledger_key>.csv",
                "actions": {
                    "detect_anomalies": {
                        "label": "Detect Anomalies",
                        "params": [
                            {"name": "ledger_key", "label": "Ledger Key", "type": "select", "options": ["sales", "purchases"], "required": True},
                            {"name": "file", "label": "Ledger File (CSV)", "type": "file", "required": True}
                        ]
                    },
                    "query": {
                        "label": "Query Ledger (AI)",
                        "params": [
                            {"name": "ledger_key", "label": "Ledger Key", "type": "select", "options": ["sales", "purchases"], "required": True},
                            {"name": "file", "label": "Ledger File (CSV)", "type": "file", "required": True},
                            {"name": "query", "label": "Natural Language Query", "type": "text", "required": True}
                        ]
                    },
                    "summarize": {
                        "label": "Summarize Data (AI)",
                        "params": [
                            {"name": "context", "label": "Context", "type": "text", "required": True},
                            {"name": "data", "label": "JSON Data", "type": "json", "required": False}
                        ]
                    }
                }
            }
        elif name == "ComplianceCheckAgent":
            meta[name] = {
                "display": "Compliance Checks",
                "actions": {
                    "run_checks": {
                        "label": "Run Checks",
                        "params": [
                            {"name": "sales", "label": "Sales Ledger (CSV/XLSX)", "type": "file", "required": True},
                            {"name": "purchases", "label": "Purchases Ledger (CSV/XLSX)", "type": "file", "required": True},
                            {"name": "period", "label": "Period (YYYY-MM)", "type": "string", "placeholder": "2025-07", "required": False}
                        ]
                    }
                }
            }
        elif name == "InsightBotAgent":
            meta[name] = {
                "display": "Insights",
                "actions": {
                    "summarize_period": {
                        "label": "Summarize Period",
                        "params": [
                            {"name": "sales", "label": "Sales Ledger (CSV/XLSX)", "type": "file", "required": True},
                            {"name": "purchases", "label": "Purchases Ledger (CSV/XLSX)", "type": "file", "required": True}
                        ]
                    },
                    "top_customers": {
                        "label": "Top Customers",
                        "params": [
                            {"name": "sales", "label": "Sales Ledger (CSV/XLSX)", "type": "file", "required": True},
                            {"name": "top_n", "label": "Top N", "type": "number", "required": False}
                        ]
                    },
                    "anomaly_scan": {
                        "label": "Anomaly Scan",
                        "params": [
                            {"name": "sales", "label": "Sales Ledger (CSV/XLSX)", "type": "file", "required": True}
                        ]
                    },
                    "ai_summary": {
                        "label": "AI KPI Summary",
                        "params": [
                            {"name": "sales", "label": "Sales Ledger (CSV/XLSX)", "type": "file", "required": True},
                            {"name": "purchases", "label": "Purchases Ledger (CSV/XLSX)", "type": "file", "required": True}
                        ]
                    },
                    "ai_explain_anomalies": {
                        "label": "AI Explain Anomalies",
                        "params": [
                            {"name": "sales", "label": "Sales Ledger (CSV/XLSX)", "type": "file", "required": True}
                        ]
                    },
                    "ai_forecast": {
                        "label": "AI Forecast",
                        "params": [
                            {"name": "sales", "label": "Sales Ledger (CSV/XLSX)", "type": "file", "required": True},
                            {"name": "purchases", "label": "Purchases Ledger (CSV/XLSX)", "type": "file", "required": True}
                        ]
                    },
                    "ai_query": {
                        "label": "AI Query",
                        "params": [
                            {"name": "sales", "label": "Sales Ledger (CSV/XLSX)", "type": "file", "required": True},
                            {"name": "query", "label": "Query", "type": "text", "required": True}
                        ]
                    }
                }
            }
        elif name == "TaxBot":
            meta[name] = {
                "display": "TaxBot",
                "actions": {
                    "extract": {
                        "label": "Extract from Files",
                        "params": [
                            {"name": "files", "label": "Files (PDF/IMG/CSV/XLSX)", "type": "files", "required": True}
                        ]
                    },
                    "calculate": {
                        "label": "Calculate Tax",
                        "params": [
                            {"name": "incomes", "label": "Incomes JSON", "type": "file", "required": True},
                            {"name": "deductions", "label": "Deductions JSON", "type": "file", "required": False},
                            {"name": "rebate", "label": "Rebate", "type": "number", "required": False}
                        ]
                    },
                    "ai-summarize": {
                        "label": "AI Summarize Doc",
                        "params": [
                            {"name": "file", "label": "File (PDF/TXT/JSON)", "type": "file", "required": True}
                        ]
                    },
                    "ai-categorize": {
                        "label": "AI Categorize Incomes",
                        "params": [
                            {"name": "file", "label": "File (PDF/TXT)", "type": "file", "required": True}
                        ]
                    }
                }
            }
        else:
            # Fallback: no metadata, still list as basic agent with no actions
            meta[name] = {"display": name, "actions": {}}
    # Attach activation flags
    for name in meta:
        meta[name]["active"] = ACTIVATED_AGENTS.get(name, True)
    return meta

def _safe_float(x, default=0.0):
    try:
        return float(x)
    except Exception:
        return default

def _read_csv_rows(csv_path: str):
    rows = []
    if not os.path.isfile(csv_path):
        return rows
    try:
        import csv
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for r in reader:
                rows.append(r)
    except Exception:
        pass
    return rows

@app.get("/overview")
def get_overview():
    """High-level overview: counts, active/inactive, sample health info."""
    agents_meta = get_agent_metadata()
    total = len(agents_meta)
    active = sum(1 for a in agents_meta.values() if a.get("active"))
    inactive = total - active
    health = {"backend": "ok", "time": datetime.utcnow().isoformat() + "Z"}
    return {"total_agents": total, "active_agents": active, "inactive_agents": inactive, "health": health}

@app.get("/activity")
def get_activity(limit: int = 50):
    """Return the most recent activity events (JSONL file)."""
    events = []
    try:
        if os.path.isfile(ACTIVITY_FILE):
            with open(ACTIVITY_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        events.append(json.loads(line))
                    except Exception:
                        pass
        events = events[-limit:]
    except Exception:
        events = []
    return {"events": events[::-1]}

@app.get("/agents/metrics")
def get_agents_metrics():
    """Aggregate per-agent metrics from activity log and current activation state."""
    agents_meta = get_agent_metadata()
    agg = {name: {"name": name, "active": bool(meta.get("active")), "executions": 0, "errors": 0, "last_ts": None} for name, meta in agents_meta.items()}
    try:
        if os.path.isfile(ACTIVITY_FILE):
            with open(ACTIVITY_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        ev = json.loads(line)
                    except Exception:
                        continue
                    if ev.get("type") == "agent_execute":
                        nm = ev.get("agent")
                        if nm in agg:
                            if ev.get("status") == "success":
                                agg[nm]["executions"] += 1
                            if ev.get("status") == "error":
                                agg[nm]["errors"] += 1
                            agg[nm]["last_ts"] = ev.get("ts") or agg[nm]["last_ts"]
    except Exception:
        pass
    return {"metrics": list(agg.values())}

@app.get("/data/sales")
def data_sales(path: str | None = Query(default=None)):
    csv_path = path if (path and os.path.isfile(path)) else "sales.csv"
    rows = _read_csv_rows(csv_path)
    # Aggregate by date (sum invoice_value) and GST rate counts
    by_date = {}
    gst_rates = {}
    total_value = 0.0
    for r in rows:
        date = (r.get("invoice_date") or "").strip()
        val = _safe_float(r.get("invoice_value"))
        total_value += val
        by_date[date] = by_date.get(date, 0.0) + val
        rate = (r.get("gst_rate") or "unknown")
        gst_rates[rate] = gst_rates.get(rate, 0) + 1
    trend = sorted([{"date": k, "value": v} for k, v in by_date.items()], key=lambda x: x["date"])
    rate_dist = sorted([{"rate": str(k), "count": v} for k, v in gst_rates.items()], key=lambda x: x["rate"])
    return {"total": total_value, "trend": trend, "rate_dist": rate_dist, "rows": rows[:200]}

@app.get("/data/purchases")
def data_purchases(path: str | None = Query(default=None)):
    csv_path = path if (path and os.path.isfile(path)) else "purchases.csv"
    rows = _read_csv_rows(csv_path)
    by_date = {}
    gst_rates = {}
    total_value = 0.0
    for r in rows:
        date = (r.get("invoice_date") or "").strip()
        val = _safe_float(r.get("invoice_value"))
        total_value += val
        by_date[date] = by_date.get(date, 0.0) + val
        rate = (r.get("gst_rate") or "unknown")
        gst_rates[rate] = gst_rates.get(rate, 0) + 1
    trend = sorted([{"date": k, "value": v} for k, v in by_date.items()], key=lambda x: x["date"])
    rate_dist = sorted([{"rate": str(k), "count": v} for k, v in gst_rates.items()], key=lambda x: x["rate"])
    return {"total": total_value, "trend": trend, "rate_dist": rate_dist, "rows": rows[:200]}


def process_command(user_input: str):
    command_parts = shlex.split(user_input)
    plan = core_agent.process_request(user_input)
    if not plan:
        return {"error": "Could not determine an action plan for your command."}

    results = []
    for step in plan:
        tool_name = step.get("tool")
        agent = available_agents.get(tool_name)
        if not agent:
            results.append({"error": f"Agent '{tool_name}' is not available."})
            continue

        params = {}
        if tool_name == "DocAuditAgent" and len(command_parts) > 2:
            params['document_path'] = command_parts[2]
        elif tool_name == "ClientCommAgent" and len(command_parts) > 2:
            params['recipient_email'] = command_parts[2]
        elif tool_name == "BookBotAgent" and len(command_parts) > 2:
            params['ledger'] = command_parts[2]
            if len(command_parts) > 3 and command_parts[3].startswith("kind="):
                params['kind'] = command_parts[3].split("=")[1]
        elif tool_name == "GSTAgent" and len(command_parts) > 2:
            if step.get("action") == "detect_anomalies":
                params["ledger"] = command_parts[2]
            elif step.get("action") == "query":
                params["ledger"] = command_parts[2]
                params["query"] = " ".join(command_parts[3:])
            elif step.get("action") == "summarize":
                params["context"] = command_parts[2]
                params["data"] = json.loads(command_parts[3]) if len(command_parts) > 3 else {}
        elif tool_name == "ComplianceCheckAgent":
            for arg in command_parts[2:]:
                if arg.startswith("sales="):
                    params["sales"] = arg.split("=", 1)[1]
                elif arg.startswith("purchases="):
                    params["purchases"] = arg.split("=", 1)[1]
                elif arg.startswith("period="):
                    params["period"] = arg.split("=", 1)[1]
        elif tool_name == "TaxBot":
            if step.get("action") == "extract":
                params["files"] = command_parts[2:]
            elif step.get("action") == "calculate":
                params["incomes"] = command_parts[2]
                if "--deductions" in command_parts:
                    idx = command_parts.index("--deductions")
                    params["deductions"] = command_parts[idx + 1]
                if "--rebate" in command_parts:
                    idx = command_parts.index("--rebate")
                    params["rebate"] = float(command_parts[idx + 1])
            elif step.get("action") == "autofill":
                params["template"] = command_parts[2]
                params["person"] = command_parts[4]
                params["incomes"] = command_parts[6]
                if "--deductions" in command_parts:
                    idx = command_parts.index("--deductions")
                    params["deductions"] = command_parts[idx + 1]
                params["out"] = command_parts[-1]
            elif step.get("action") == "remind":
                params["date"] = command_parts[2]
                params["message"] = " ".join(command_parts[3:])
            elif step.get("action") in ["ai-summarize", "ai-categorize"]:
                params["text"] = Path(command_parts[2]).read_text(encoding="utf-8")
            elif step.get("action") == "ai-check-deductions":
                params["incomes"] = json.loads(Path(command_parts[2]).read_text(encoding="utf-8")).get(
                    "incomes", [])
                params["deductions"] = json.loads(Path(command_parts[3]).read_text(encoding="utf-8")).get(
                    "deductions", [])
        elif tool_name == "InsightBotAgent":
            if step.get("action") in ["summarize_period", "ai_summary", "ai_forecast"]:
                params["sales"] = command_parts[2]
                params["purchases"] = command_parts[4] if len(command_parts) > 4 else None
            elif step.get("action") in ["top_customers"]:
                params["sales"] = command_parts[2]
                params["top_n"] = int(command_parts[4]) if len(command_parts) > 4 else 10
            elif step.get("action") in ["anomaly_scan", "ai_explain_anomalies"]:
                params["sales"] = command_parts[2]
            elif step.get("action") == "ai_query":
                params["sales"] = command_parts[2]
                params["query"] = " ".join(command_parts[3:])

        task = {"action": step.get("action"), "params": params}
        try:
            result = agent.execute(task)
            results.append(result)
        except Exception as e:
            results.append({"error": str(e)})
    return {"plan": plan, "results": results}


# --- New structured API for dashboard ---
@app.get("/agents")
def list_agents():
    return get_agent_metadata()


@app.post("/agents/{name}/activate")
async def set_agent_activation(name: str, request: Request, active: bool | None = Query(default=None)):
    if name not in available_agents:
        raise HTTPException(status_code=404, detail="Agent not found")
    # Try to read JSON body, but tolerate missing/invalid
    body = {}
    try:
        body = await request.json()
    except Exception:
        body = {}
    # Determine desired state: query param > body.active > toggle
    if active is None:
        if isinstance(body, dict) and "active" in body:
            try:
                active = bool(body.get("active"))
            except Exception:
                active = True
        else:
            active = not ACTIVATED_AGENTS.get(name, True)
    ACTIVATED_AGENTS[name] = bool(active)
    _persist_activation_state()
    _log_activity({"type": "agent_activation", "agent": name, "active": ACTIVATED_AGENTS[name]})
    return {"name": name, "active": ACTIVATED_AGENTS[name]}

@app.get("/agents/{name}/status")
def get_agent_status(name: str):
    if name not in available_agents:
        raise HTTPException(status_code=404, detail="Agent not found")
    return {"name": name, "active": ACTIVATED_AGENTS.get(name, True)}


def _prepare_params_for_execution(agent_name: str, action: str, params: dict) -> dict:
    """Adjust params from UI to match agent expectations (file paths, special cases)."""
    p = dict(params or {})
    # Normalize files inputs: UI may send arrays of uploaded paths under 'files'
    if agent_name == "GSTAgent":
        # Copy uploaded 'file' to output/<ledger_key>.csv and set 'ledger'
        if action in ("detect_anomalies", "query"):
            ledger_key = p.get("ledger_key")
            up = p.get("file")
            if ledger_key and up:
                os.makedirs("output", exist_ok=True)
                dest = os.path.join("output", f"{ledger_key}.csv")
                try:
                    shutil.copyfile(up, dest)
                except Exception:
                    # If copy fails, try reading and writing
                    with open(up, "rb") as rf, open(dest, "wb") as wf:
                        wf.write(rf.read())
                p["ledger"] = ledger_key
                p.pop("ledger_key", None)
                p.pop("file", None)
    if agent_name == "TaxBot":
        if action == "extract":
            # Ensure 'files' is a list of paths
            files = p.get("files")
            if isinstance(files, str):
                p["files"] = [files]
        elif action in ("ai-summarize", "ai-categorize"):
            # If UI sends a file path, read to text
            fpath = p.get("file")
            if fpath and os.path.exists(fpath):
                try:
                    from pathlib import Path as _Path
                    ext = _Path(fpath).suffix.lower()
                    text = ""
                    if ext == ".json":
                        text = json.dumps(json.loads(open(fpath, "r", encoding="utf-8").read()), indent=2)
                    elif ext in (".pdf",):
                        # let agent handle PDF via its own extract if needed; read raw text as fallback
                        text = open(fpath, "rb").read().decode(errors="ignore")
                    else:
                        text = open(fpath, "r", encoding="utf-8", errors="ignore").read()
                    p["text"] = text
                except Exception:
                    pass
                p.pop("file", None)
    return p


@app.post("/agents/execute")
async def execute_agent(request: Request):
    data = await request.json()
    agent_name = data.get("agent")
    action = data.get("action")
    params = data.get("params", {})

    if agent_name not in available_agents:
        raise HTTPException(status_code=404, detail="Agent not found")
    if not ACTIVATED_AGENTS.get(agent_name, True):
        raise HTTPException(status_code=400, detail="Agent is deactivated")
    agent = available_agents[agent_name]

    # Adjust params for agent-specific expectations
    params = _prepare_params_for_execution(agent_name, action, params)

    task = {"action": action, "params": params}
    _log_activity({"type": "agent_execute", "agent": agent_name, "action": action, "status": "started"})
    try:
        result = agent.execute(task)
        _log_activity({"type": "agent_execute", "agent": agent_name, "action": action, "status": "success"})
        return result
    except Exception as e:
        _log_activity({"type": "agent_execute", "agent": agent_name, "action": action, "status": "error", "error": str(e)})
        return {"status": "error", "message": str(e)}


@app.post("/agent")
async def agent_endpoint(request: Request):
    data = await request.json()
    user_input = data.get("command", "")
    response = process_command(user_input)
    return response


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    upload_dir = "uploaded_files"
    os.makedirs(upload_dir, exist_ok=True)
    if not file.filename:
        return {"error": "No filename provided"}
    file_location = os.path.join(upload_dir, file.filename)
    with open(file_location, "wb") as f:
        f.write(await file.read())
    # Return relative path for backend usage
    return {"path": file_location}


def main():
    """
    Main function to run the AI Agent (Phase 1 MVP).
    """
    print("Initializing AI Agent components...")
    doc_processor = DocumentProcessor()

    available_agents = get_all_agents()
    core_agent = CoreAIAgent(available_tools=list(available_agents.keys()))

    print("\n--- AI Agent for CA Firm ---")
    print("Available Agents: " + ", ".join(available_agents.keys()))
    print("Example Commands:")
    if "DocAuditAgent" in available_agents:
        print("  audit document \"/path/to/your/invoice.pdf\"")
    if "ClientCommAgent" in available_agents:
        print("  send reminder client_abc@example.com")
    if "BookBotAgent" in available_agents:
        print("  bookbotagent categorize ./path/to/ledger.csv")
        print("  bookbotagent pnl ./path/to/ledger.csv")
        print("  bookbotagent journalize ./path/to/ledger.csv kind=sales")
    if "ComplianceCheckAgent" in available_agents:
        print("  compliance run_checks sales=./sales.csv purchases=./purchases.csv period=2025-07")
    if "GSTAgent" in available_agents:
        print("  gstagent anomalies --ledger ./path/to/sales")
        print("  gstagent query ./path/to/sales 'high value invoices above 5L'")
        print("  gstagent summarize --context 'Monthly filing' --data '{...}'")
    if "InsightBotAgent" in available_agents:
        print("  insight summarize_period --sales ./sales.csv --purchases ./purchases.csv")
        print("  insight top_customers --sales ./sales.csv --top_n 5")
        print("  insight anomaly_scan --sales ./sales.csv")
        print("  insight ai_summary --sales ./sales.csv --purchases ./purchases.csv")
        print("  insight ai_explain_anomalies --sales ./sales.csv")
        print("  insight ai_forecast --sales ./sales.csv --purchases ./purchases.csv")
        print("  insight ai_query --sales ./sales.csv 'show invoices above 5 lakh'")
    if "TaxBot" in available_agents:
        print("  taxbot extract --files ./salary.pdf ./interest.pdf")
        print(
            "  taxbot calculate --incomes ./taxbot_output/extracted.json --deductions ./deductions.json --rebate 12500")
        print(
            "  taxbot autofill --template ./template.json --person ./person.json --incomes ./incomes.json --deductions ./deductions.json --out ./filled.json")
        print("  taxbot remind --date 2025-07-31 --message 'File your returns!'")
        print("  taxbot ai-summarize --file ./salary.pdf")
        print("  taxbot ai-categorize --file ./salary.pdf")
        print("  taxbot ai-check-deductions --incomes ./incomes.json --deductions ./deductions.json")

    # for agent_name in available_agents:
    #     if agent_name not in ["DocAuditAgent", "ClientCommAgent", "BookBotAgent"]:
    #         print(f"  {agent_name.lower()} <your_parameters_here>")
    # print("Enter your command (or 'exit' to quit):")

    while True:
        try:
            user_input = input("> ")
            if user_input.lower() in ['exit', 'quit']:
                print("Exiting agent. Goodbye!")
                break
            if not user_input.strip():
                continue
            response = process_command(user_input)
            print(f"Generated Plan: {response.get('plan')}")
            if "error" in response:
                print(f"Error: {response['error']}")
                continue
            for result in response.get("results", []):
                print("\n--- Execution Result ---")
                if isinstance(result, dict):
                    for key, value in result.items():
                        print(f"{key.replace('_', ' ').capitalize()}: {value}")
                else:
                    print(result)
                print("------------------------\n")
        except (KeyboardInterrupt, EOFError):
            print("\nExiting agent. Goodbye!")
            break
        except Exception as e:
            print(f"\nAn unexpected error occurred: {e}\nPlease try again.\n")


if __name__ == "__main__":
    for dir_name in ["perception", "agent_core", "action", "agents"]:
        os.makedirs(dir_name, exist_ok=True)
        with open(os.path.join(dir_name, "__init__.py"), "w") as f:
            pass
    # Run FastAPI server
    # Use config-driven host/port if provided
    uvicorn.run(app, host=config.UVICORN_HOST, port=config.UVICORN_PORT)
    # Optionally, keep CLI for local testing
    # main()

# To run the backend, use the following command in your terminal:
# (Make sure you are in the backend folder and have all dependencies installed.)

# If you have Python and uvicorn installed:
# > uvicorn main:app --host 0.0.0.0 --port 8000

# Or, simply run:
# > python main.py

# This will start the FastAPI server on http://localhost:8000
# Make sure your backend is running before using the frontend.
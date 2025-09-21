# CAAI — CA AI Agents (FastAPI + Next.js)

CAAI is a full-stack app with a FastAPI backend of accounting/CA-focused AI agents and a Next.js (TypeScript) dashboard to control them.

## Prerequisites

- Git
- Python 3.11+ (3.12 recommended)
- Node.js 18 or 20 LTS and npm
- Windows PowerShell (these commands use PowerShell syntax)

## 1) Clone the repository

```powershell
# Clone and enter the project
git clone https://github.com/omkarmakar/CAAI.git
cd CAAI
```

## 2) Backend setup (FastAPI)

```powershell
# Create and activate a virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Run the backend (from the backend/ folder)
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000
# Backend will be at http://localhost:8000
```

Notes:
- If the activation script is blocked, you may need (once):
  - Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
- Optional config: create a `.env` in `backend/` if you want to override defaults:
  - GEMINI_API_KEY=your_api_key
  - UVICORN_HOST=0.0.0.0
  - UVICORN_PORT=8000

## 3) Frontend setup (Next.js + TypeScript)

Open a new PowerShell window (keep the backend running), then:

```powershell
cd CAAI\frontend-next

# Install Node dependencies
npm install

# Configure the backend origin used by the UI
# Create .env.local with the backend URL (default shown)
"NEXT_PUBLIC_BACKEND_URL=http://localhost:8000" | Out-File -FilePath .env.local -Encoding UTF8

# Start the dev server
npm run dev
# Frontend will be at http://localhost:3000
```

For production builds:

```powershell
npm run build
npm start
```

## 4) Using the app

1. Open http://localhost:3000
2. You’ll see agent cards. Use the toggle to activate/deactivate an agent.
3. Click "Open" to view an agent’s actions and fill in parameters.
4. Upload files when required (they’re stored under `backend/uploaded_files/`).
5. Click "Run" to execute; results render as tables, KPI cards, or JSON.

Backend health check: opening http://localhost:8000 returns a small JSON if the backend is running.

## API overview (for reference)

- GET /agents → List agents with actions and `active` state
- POST /agents/{name}/activate?active=true|false → Toggle activation (also accepts JSON body `{ "active": true|false }`)
- POST /agents/execute → Execute an action
  - Body: `{ "agent": "AgentName", "action": "action_name", "params": { ... } }`
- POST /upload → Upload a file (returns `{ path: "backend/uploaded_files/<filename>" }`)

## Repo structure

- `backend/` FastAPI app and agents
  - `main.py` API and agent routing
  - `agents/` agent implementations
  - `uploaded_files/` uploaded files (generated)
  - `output/` generated outputs (activation state, etc.)
- `frontend-next/` Next.js dashboard

## Troubleshooting

- Frontend can’t reach backend: ensure `NEXT_PUBLIC_BACKEND_URL` matches where FastAPI is running.
- Toggle doesn’t change: check the Network tab (POST /agents/{name}/activate should be 200) and verify `GET /agents` shows `active: true/false`.
- Virtualenv activation blocked: run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once in PowerShell (as your user).

## Development notes

- Activation state is persisted in `backend/output/activation.json`.
- `.gitignore` excludes virtualenvs, node_modules, build artifacts, uploads, and generated outputs.
- You can run the backend with `python main.py` as well, but `uvicorn` is recommended during development.

Enjoy building with CAAI! 👩‍💻👨‍💻

## AI agents included

Below is a quick overview of the built-in agents, their purpose, and the actions you can run from the dashboard (or via the API). The frontend automatically renders forms based on the metadata served by the backend (GET /agents).

1) Document Audit — `DocAuditAgent`
- Purpose: Audit a single document (invoice/receipt) for compliance or irregularities.
- Action:
  - `audit_document`
    - Params: `document_path` (string; path returned by /upload)
    - Output: `{ findings: string[] }`

2) Client Communication — `ClientCommAgent`
- Purpose: Draft and send reminder emails to clients (e.g., filing reminders).
- Action:
  - `send_reminder`
    - Params: `recipient_email` (string)
    - Output: `{ status: 'ok'|'error', details?: any }`

3) BookBot — `BookBotAgent`
- Purpose: Analyze ledgers (CSV/XLSX) for categorization, P&L, and journal entries.
- Actions:
  - `categorize` (Params: `ledger`) → `{ top_categories: {category, rows}[], preview: any[] }`
  - `pnl` (Params: `ledger`) → `{ pnl_by_category: any[], net_profit: number }`
  - `journalize` (Params: `ledger`, `kind?`='sales'|'purchases') → `{ journals: { invoice_no, entry: {account, dr, cr}[] }[] }`

4) Compliance Checks — `ComplianceCheckAgent`
- Purpose: Check sales/purchases ledgers for compliance issues and anomalies.
- Action:
  - `run_checks`
    - Params: `sales` (file), `purchases` (file), `period?` ('YYYY-MM')
    - Output: `{ findings: { severity: 'HIGH'|'MEDIUM'|'LOW', ledger, invoice_no, issue, hint? }[] }`

5) GST Agent — `GSTAgent`
- Purpose: GST-related anomaly detection, AI querying, and summarization.
- Actions:
  - `detect_anomalies` (Params: `ledger_key` ('sales'|'purchases'), `file` (CSV)) → copies to `output/<ledger_key>.csv` and runs checks.
  - `query` (Params: `ledger_key`, `file`, `query` (text)) → `{ results: any[], expression?: string }`
  - `summarize` (Params: `context` (text), `data?` (JSON)) → AI summary object

6) Insights — `InsightBotAgent`
- Purpose: High-level business insights from sales/purchases ledgers.
- Actions:
  - `summarize_period` (Params: `sales`, `purchases`) → `{ kpis: { sales, purchases, net_tax_liability_proxy } }`
  - `top_customers` (Params: `sales`, `top_n?`) → `{ top_customers: any[] }`
  - `anomaly_scan` (Params: `sales`) → `{ anomalies: any[], population_mean, population_stdev }`
  - `ai_summary` / `ai_explain_anomalies` / `ai_forecast` (various ledger params) → AI-generated content
  - `ai_query` (Params: `sales`, `query` (text)) → `{ rows: any[], query: string }`

7) TaxBot — `TaxBot`
- Purpose: Extract data from documents and calculate personal tax, plus AI helpers.
- Actions:
  - `extract` (Params: `files` (string[] of uploaded paths)) → `{ person: any, incomes: any[] }`
  - `calculate` (Params: `incomes` (JSON file), `deductions?` (JSON file), `rebate?` (number)) → `{ summary: { gross_income, total_deductions, taxable_income, ... } }`
  - `ai-summarize` (Params: `file`) → `{ ...AI summary... }`
  - `ai-categorize` (Params: `file`) → `{ ...AI categorization... }`

Notes
- File uploads use POST `/upload` and are saved under `backend/uploaded_files/`; the API returns a `path` string which you pass back to actions.
- Agent activation states are toggleable in the UI and persisted to `backend/output/activation.json`.

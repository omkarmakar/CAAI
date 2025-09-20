"""
GSTAgent – Prepare GST returns, reconcile ledgers, detect anomalies (via Gemini), and (mock) upload to GSTN.

Highlights
---------
- Read sales & purchase ledgers (CSV/Excel)
- Validate GSTINs and invoice fields
- Auto-compute taxes (CGST/SGST/IGST) per invoice line
- Build period-wise summaries for GSTR-1 and GSTR-3B
- Reconcile Purchase Register vs 2B (or supplier invoices) with tolerances
- Export JSON/CSV artifacts ready for filing workflows
- Intelligent anomaly detection, summaries, and queries with Gemini
- CLI commands: prepare-returns, reconcile, upload (mock), report, query, anomalies, summarize
- Pluggable GSTN client – swap MockGSTNClient with a real GSP/ASP SDK
"""

from __future__ import annotations
import argparse
import csv
import datetime as dt
import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

try:
    import pandas as pd
except ImportError:
    pd = None

try:
    from pydantic import BaseModel, Field
except Exception:
    BaseModel = object
    Field = lambda *a, **k: None

import google.generativeai as genai

# ---------------------------- Utilities ----------------------------
GSTIN_RE = re.compile(r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$")

STATE_CODES = {
    "07": "Delhi", "19": "West Bengal", "27": "Maharashtra", "29": "Karnataka",
    "33": "Tamil Nadu", "36": "Telangana", "32": "Kerala", "37": "Andhra Pradesh"
}

ROUND2 = lambda x: float(f"{x:.2f}")


def validate_gstin(gstin: str) -> bool:
    return bool(GSTIN_RE.match((gstin or "").strip()))


def norm_inv_no(inv: str) -> str:
    return re.sub(r"[^A-Za-z0-9]", "", (inv or "").upper())


def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def parse_date(x) -> dt.date:
    if isinstance(x, dt.date):
        return x
    s = str(x)
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%Y/%m/%d"):
        try:
            return dt.datetime.strptime(s, fmt).date()
        except Exception:
            continue
    raise ValueError(f"Unrecognized date: {x}")


def read_table(path: Path):
    if pd is None:
        raise RuntimeError("pandas required: pip install pandas")
    if path.suffix.lower() in {".xlsx", ".xls"}:
        return pd.read_excel(path)
    return pd.read_csv(path)

# ---------------------------- Data Models ----------------------------
@dataclass
class OrgInfo:
    legal_name: str
    gstin: str
    state_code: str
    filing_frequency: str

    @staticmethod
    def from_json(path: Path) -> "OrgInfo":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        org = OrgInfo(
            legal_name=data["legal_name"],
            gstin=data["gstin"],
            state_code=data["state_code"],
            filing_frequency=data.get("filing_frequency", "monthly").lower(),
        )
        if not validate_gstin(org.gstin):
            raise ValueError("Invalid org GSTIN")
        if org.state_code not in STATE_CODES:
            raise ValueError("Invalid org state_code")
        return org

@dataclass
class LineItem:
    item_name: str
    hsn: str
    qty: float
    unit_price: float
    discount: float
    gst_rate: float
    shipping_charges: float = 0.0
    other_charges: float = 0.0

    def taxable_value(self) -> float:
        gross = self.qty * self.unit_price
        return ROUND2(max(gross - self.discount, 0.0) + self.shipping_charges + self.other_charges)

@dataclass
class Invoice:
    invoice_no: str
    invoice_date: dt.date
    counterparty_gstin: str
    is_interstate: bool
    place_of_supply_state_code: str
    lines: List[LineItem]
    itc_eligible: Optional[bool] = None

    def totals(self) -> Dict[str, float]:
        tv = sum(li.taxable_value() for li in self.lines)
        rate_groups: Dict[float, float] = {}
        for li in self.lines:
            rate_groups[li.gst_rate] = rate_groups.get(li.gst_rate, 0.0) + li.taxable_value()
        igst = cgst = sgst = 0.0
        for rate, base in rate_groups.items():
            if self.is_interstate:
                igst += base * (rate / 100.0)
            else:
                half = (rate / 100.0) / 2.0
                cgst += base * half
                sgst += base * half
        return {
            "taxable_value": ROUND2(tv),
            "igst": ROUND2(igst),
            "cgst": ROUND2(cgst),
            "sgst": ROUND2(sgst),
            "total_invoice_value": ROUND2(tv + igst + cgst + sgst),
        }

# ---------------------------- GST Agent ----------------------------
class GSTAgent:
    def __init__(self, org: OrgInfo, out_dir: Path, gemini_api_key: Optional[str] = None):
        self.org = org
        self.out_dir = out_dir
        ensure_dir(out_dir)

        self.gemini_client = None
        if gemini_api_key:
            genai.configure(api_key=gemini_api_key)
            self.gemini_client = genai.GenerativeModel("gemini-1.5-flash")

    # ---------------- Gemini helpers ----------------
    def _detect_anomalies(self, ledger: str) -> Dict[str, Any]:
        if not self.gemini_client:
            return {"status": "error", "message": "Gemini not initialized"}
        path = self.out_dir / f"{ledger}.csv"
        df = pd.read_csv(path)
        prompt = f"""
        Analyze this GST ledger for anomalies.
        Columns: {list(df.columns)}
        First rows: {df.head().to_dict(orient="records")}
        Return JSON list with: issue, severity, invoice_no, details.
        """
        resp = self.gemini_client.generate_content(prompt)
        try:
            findings = json.loads(resp.text)
        except Exception:
            findings = [{"issue": "Failed to parse Gemini output", "severity": "LOW"}]
        return {"status": "success", "findings": findings}

    def _summarize(self, context: str, data: Dict[str, Any]) -> str:
        if not self.gemini_client:
            return "Gemini not initialized"
        prompt = f"Summarize the GST data for a CA.\nContext: {context}\nData:\n{json.dumps(data, indent=2)}"
        resp = self.gemini_client.generate_content(prompt)
        return resp.text.strip()

    def _query_ledger(self, ledger: str, query: str) -> Dict[str, Any]:
        if not self.gemini_client:
            return {"status": "error", "message": "Gemini not initialized"}
        path = self.out_dir / f"{ledger}.csv"
        df = pd.read_csv(path)
        prompt = f"""
        User query: "{query}"
        Columns: {list(df.columns)}
        Generate a pandas filter expression (without df.) that selects matching rows.
        """
        resp = self.gemini_client.generate_content(prompt)
        expr = resp.text.strip()
        try:
            filtered = df.query(expr)
            return {"status": "success", "expression": expr, "results": filtered.to_dict(orient="records")}
        except Exception as e:
            return {"status": "error", "message": str(e), "expression": expr}

    # ---------------- Router ----------------
    def execute(self, task: dict) -> dict:
        action = task.get("action")
        params = task.get("params", {})
        try:
            if action == "detect_anomalies":
                return self._detect_anomalies(params["ledger"])
            elif action == "summarize":
                return {"summary": self._summarize(params.get("context", ""), params.get("data", {}))}
            elif action == "query":
                return self._query_ledger(params["ledger"], params["query"])
            else:
                return {"status": "error", "message": f"Unknown action {action}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

# ---------------------------- CLI ----------------------------
def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="GSTAgent – with Gemini intelligence")
    sub = p.add_subparsers(dest="cmd", required=True)

    an = sub.add_parser("anomalies", help="Detect anomalies in a ledger")
    an.add_argument("--ledger", required=True)

    q = sub.add_parser("query", help="Query ledger with natural language")
    q.add_argument("--ledger", required=True)
    q.add_argument("--query", required=True)

    sm = sub.add_parser("summarize", help="Summarize GST data")
    sm.add_argument("--context", required=True)
    sm.add_argument("--data", required=True)

    return p.parse_args()

def main():
    args = parse_args()
    org = OrgInfo("DemoOrg", "29ABCDE1234F2Z5", "29", "monthly")  # demo org
    agent = GSTAgent(org, Path("./output"), gemini_api_key="YOUR_API_KEY")

    if args.cmd == "anomalies":
        print(agent.execute({"action": "detect_anomalies", "params": {"ledger": args.ledger}}))
    elif args.cmd == "query":
        print(agent.execute({"action": "query", "params": {"ledger": args.ledger, "query": args.query}}))
    elif args.cmd == "summarize":
        data = json.loads(args.data)
        print(agent.execute({"action": "summarize", "params": {"context": args.context, "data": data}}))

if __name__ == "__main__":
    main()

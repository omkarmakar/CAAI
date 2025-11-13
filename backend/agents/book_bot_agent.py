from __future__ import annotations
from typing import Dict, Any, List
from pathlib import Path
import re
from dataclasses import dataclass
import pandas as pd

from .base_agent import BaseAgent

@dataclass
class Rule:
    pattern: str           # regex on item_name / details
    category: str          # e.g., 'Sales', 'COGS', 'Rent', 'Utilities', 'Travel'
    side: str              # 'income' or 'expense'

DEFAULT_RULES = [
    Rule(r"salary|payroll|wages", "Payroll", "expense"),
    Rule(r"freight|courier|shipping", "Freight & Shipping", "expense"),
    Rule(r"rent|lease", "Rent", "expense"),
    Rule(r"electric|power|utility|internet|wifi|broadband", "Utilities", "expense"),
    Rule(r"consult|service|fee", "Professional Fees", "expense"),
    Rule(r"repair|maintenance", "Repairs & Maintenance", "expense"),
    Rule(r"advert|marketing|ads", "Advertising & Marketing", "expense"),
    Rule(r"software|saas|subscription|license", "Software Subscriptions", "expense"),
    Rule(r"interest|bank charge|fee", "Finance Charges", "expense"),
    Rule(r"sale|invoice|billed", "Sales", "income"),
]

class BookBotAgent(BaseAgent):
    """
    Lightweight bookkeeping helper with optional Gemini support.
    Actions:
      - categorize: tag each ledger row to a P&L category using regex + Gemini fallback
      - pnl: produce P&L summary (Income - Expenses) from categorized rows
      - journalize: emit simple double-entry journals for sales/purchases
    """
    def __init__(self, rules: List[Rule] | None = None, gemini_api_key: str | None = None):
        super().__init__("BookBotAgent")
        self.rules = rules or DEFAULT_RULES
        self.gemini_api_key = gemini_api_key
        self.gemini = None

        if self.gemini_api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.gemini_api_key)
                self.gemini = genai.GenerativeModel("gemini-2.0-flash")
            except ImportError:
                print("⚠️ google-generativeai not installed, BookBotAgent will work without Gemini.")

    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        action = task.get("action")
        p = task.get("params", {}) or {}
        if action == "categorize":
            return self._categorize(Path(p["ledger"]))
        if action == "pnl":
            return self._pnl(Path(p["ledger"]))
        if action == "journalize":
            kind = p.get("kind", "sales")  # 'sales' or 'purchases'
            return self._journalize(Path(p["ledger"]), kind=kind)
        return {"status": "error", "message": f"Unknown action '{action}' for BookBotAgent"}

    # --------------- core ops ---------------
    def _categorize(self, path: Path) -> Dict[str, Any]:
        self._require_pandas()
        df = self._load(path)
        df["category"] = df.apply(self._categorize_row, axis=1)
        out = df[["invoice_no","invoice_date","item_name","category"]].fillna("")
        # return top categories
        top = out["category"].value_counts().head(15)
        summary = [{"category": k, "rows": int(v)} for k, v in top.items()]
        return {"status": "success", "preview": out.head(25).to_dict(orient="records"), "top_categories": summary}

    def _pnl(self, path: Path) -> Dict[str, Any]:
        self._require_pandas()
        df = self._load(path)
        if "category" not in df.columns:
            df["category"] = df.apply(self._categorize_row, axis=1)
        # reconstruct taxable value per line
        for col in ["shipping_charges","other_charges","discount"]:
            if col not in df.columns:
                df[col] = 0.0
        df["taxable_value"] = (df["qty"] * df["unit_price"] - df["discount"] + df["shipping_charges"] + df["other_charges"]).clip(lower=0)
        # positive income for 'Sales', expenses for others (very simplified)
        df["amount"] = df.apply(lambda r: r["taxable_value"] if r["category"] == "Sales" else -abs(r["taxable_value"]), axis=1)
        pnl = df.groupby("category")["amount"].sum().sort_values(ascending=False)
        return {
            "status": "success",
            "pnl_by_category": [{"category": k, "amount": float(f"{v:.2f}")} for k, v in pnl.items()],
            "net_profit": float(f"{pnl.sum():.2f}")
        }

    def _journalize(self, path: Path, kind: str = "sales") -> Dict[str, Any]:
        """
        Very simple double-entry generator for demonstration:
          - sales: Dr. Debtors / Bank, Cr. Sales, Cr. Output GST
          - purchases: Dr. Purchases/Expense, Dr. Input GST, Cr. Creditors / Bank
        """
        self._require_pandas()
        df = self._load(path)
        for col in ["shipping_charges","other_charges","discount"]:
            if col not in df.columns:
                df[col] = 0.0
        df["taxable_value"] = (df["qty"] * df["unit_price"] - df["discount"] + df["shipping_charges"] + df["other_charges"]).clip(lower=0)
        # tax split
        def split(r):
            rate = float(r["gst_rate"]) / 100.0
            if bool(r["is_interstate"]):
                return r["taxable_value"]*rate, 0.0, 0.0
            h = rate/2.0
            return 0.0, r["taxable_value"]*h, r["taxable_value"]*h
        igst, cgst, sgst = zip(*df.apply(split, axis=1))
        df["igst"], df["cgst"], df["sgst"] = igst, cgst, sgst

        journals = []
        for _, r in df.iterrows():
            inv = str(r["invoice_no"])
            tx = float(r["taxable_value"]); i = float(r["igst"]); c = float(r["cgst"]); s = float(r["sgst"])
            if kind == "sales":
                journals.append({
                    "invoice_no": inv, "entry": [
                        {"account": "Debtors/Bank", "dr": round(tx + i + c + s, 2), "cr": 0.0},
                        {"account": "Sales", "dr": 0.0, "cr": round(tx, 2)},
                        {"account": "Output IGST", "dr": 0.0, "cr": round(i, 2)} if i else None,
                        {"account": "Output CGST", "dr": 0.0, "cr": round(c, 2)} if c else None,
                        {"account": "Output SGST", "dr": 0.0, "cr": round(s, 2)} if s else None,
                    ]
                })
            else:  # purchases
                journals.append({
                    "invoice_no": inv, "entry": [
                        {"account": "Purchases/Expense", "dr": round(tx, 2), "cr": 0.0},
                        {"account": "Input IGST", "dr": round(i, 2), "cr": 0.0} if i else None,
                        {"account": "Input CGST", "dr": round(c, 2), "cr": 0.0} if c else None,
                        {"account": "Input SGST", "dr": round(s, 2), "cr": 0.0} if s else None,
                        {"account": "Creditors/Bank", "dr": 0.0, "cr": round(tx + i + c + s, 2)},
                    ]
                })
        # remove None lines
        for j in journals:
            j["entry"] = [line for line in j["entry"] if line]

        return {"status": "success", "journals": journals[:200]}  # cap for payload size

    # --------------- utils ---------------
    def _require_pandas(self):
        if pd is None:
            raise RuntimeError("pandas required: pip install pandas")

    def _load(self, path: Path):
        return pd.read_excel(path) if path.suffix.lower() in (".xlsx",".xls") else pd.read_csv(path)

    def _categorize_row(self, r) -> str:
        name = f"{str(r.get('item_name',''))} {str(r.get('details',''))}".lower()

        # Try regex rules
        for rule in self.rules:
            if re.search(rule.pattern, name):
                return rule.category

        # Gemini fallback if available
        if self.gemini:
            prompt = f"Categorize this ledger item into an accounting category: '{name}'"
            try:
                resp = self.gemini.generate_content(prompt)
                return resp.text.strip().split()[0] if resp and resp.text else "Other"
            except Exception:
                return "Other"

        return "Other"

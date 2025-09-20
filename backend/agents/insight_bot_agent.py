from __future__ import annotations
from typing import Dict, Any, List
from pathlib import Path
import math
import statistics as stats
import pandas as pd
import json

from .base_agent import BaseAgent

# Gemini import
import google.generativeai as genai

SAFE_ROUND = lambda x: float(f"{x:.2f}") if isinstance(x, (int, float)) and not math.isnan(x) else 0.0


class InsightBotAgent(BaseAgent):
    """
    Insights & anomaly sweeps for CA use-cases over sales/purchase ledgers.

    Actions
    -------
    - summarize_period: KPIs from sales & purchases
    - top_customers: Top-N customers by billed value
    - anomaly_scan: Z-score outlier scan on invoice totals
    - ai_summary: Gemini-generated plain English summary of KPIs
    - ai_explain_anomalies: Gemini explanation of anomalies
    - ai_forecast: Project next period's liability
    - ai_query: Natural language query → dataframe filter
    """
    def __init__(self, gemini_api_key: str = None):
        super().__init__("InsightBotAgent")
        if gemini_api_key:
            genai.configure(api_key=gemini_api_key)
            self.gemini_client = genai.GenerativeModel("gemini-1.5-flash")
        else:
            self.gemini_client = None

    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        action = task.get("action")
        p = task.get("params", {}) or {}

        if action == "summarize_period":
            return self._summarize_period(Path(p["sales"]), Path(p["purchases"]))
        if action == "top_customers":
            n = int(p.get("top_n", 10))
            return self._top_customers(Path(p["sales"]), top_n=n)
        if action == "anomaly_scan":
            return self._anomaly_scan(Path(p["sales"]))
        if action == "ai_summary":
            kpis = self._summarize_period(Path(p["sales"]), Path(p["purchases"]))
            return {"status": "success", "summary": self._summarize_with_ai(kpis)}
        if action == "ai_explain_anomalies":
            anomalies = self._anomaly_scan(Path(p["sales"]))
            return {"status": "success", "explanation": self._explain_anomalies_with_ai(anomalies)}
        if action == "ai_forecast":
            kpis = self._summarize_period(Path(p["sales"]), Path(p["purchases"]))
            return {"status": "success", "forecast": self._forecast_with_ai(kpis)}
        if action == "ai_query":
            query = p.get("query")
            return self._nl_query(Path(p["sales"]), query)

        return {"status": "error", "message": f"Unknown action '{action}' for InsightBotAgent"}

    # ---------------- internal helpers ----------------
    def _summarize_period(self, sales_path: Path, purchases_path: Path) -> Dict[str, Any]:
        self._require_pandas()
        sales = self._load_sales(sales_path)
        purch = self._load_purchases(purchases_path)

        s_tot = self._totals(sales)
        p_tot = self._totals(purch)

        kpis = {
            "sales": {
                "invoices": int(s_tot["invoice_no"].nunique()),
                "taxable_value": SAFE_ROUND(s_tot["taxable_value"].sum()),
                "igst": SAFE_ROUND(s_tot["igst"].sum()),
                "cgst": SAFE_ROUND(s_tot["cgst"].sum()),
                "sgst": SAFE_ROUND(s_tot["sgst"].sum()),
                "gross": SAFE_ROUND(s_tot["gross"].sum()),
                "avg_invoice": SAFE_ROUND(s_tot["gross"].mean() or 0),
            },
            "purchases": {
                "invoices": int(p_tot["invoice_no"].nunique()),
                "taxable_value": SAFE_ROUND(p_tot["taxable_value"].sum()),
                "igst": SAFE_ROUND(p_tot["igst"].sum()),
                "cgst": SAFE_ROUND(p_tot["cgst"].sum()),
                "sgst": SAFE_ROUND(p_tot["sgst"].sum()),
                "gross": SAFE_ROUND(p_tot["gross"].sum()),
                "avg_invoice": SAFE_ROUND(p_tot["gross"].mean() or 0),
            },
            "net_tax_liability_proxy": {
                "igst": SAFE_ROUND(s_tot["igst"].sum() - p_tot["igst"].sum()),
                "cgst": SAFE_ROUND(s_tot["cgst"].sum() - p_tot["cgst"].sum()),
                "sgst": SAFE_ROUND(s_tot["sgst"].sum() - p_tot["sgst"].sum()),
            }
        }
        return {"status": "success", "kpis": kpis}

    def _top_customers(self, sales_path: Path, top_n: int = 10) -> Dict[str, Any]:
        self._require_pandas()
        df = self._load_sales(sales_path)
        df["line_total"] = df["qty"] * df["unit_price"] - df["discount"] + df["shipping_charges"] + df["other_charges"]
        grp = df.groupby("buyer_gstin", dropna=False)["line_total"].sum().sort_values(ascending=False).head(top_n)
        rows = [{"buyer_gstin": str(k) if k == k else "UNREGISTERED", "amount": SAFE_ROUND(v)} for k, v in grp.items()]
        return {"status": "success", "top_customers": rows}

    def _anomaly_scan(self, sales_path: Path) -> Dict[str, Any]:
        self._require_pandas()
        df = self._load_sales(sales_path)
        inv = (df.assign(line_total=df["qty"]*df["unit_price"]-df["discount"]+df["shipping_charges"]+df["other_charges"])
                 .groupby(["invoice_no","invoice_date"], as_index=False)["line_total"].sum())
        vals = inv["line_total"].tolist()
        if len(vals) < 5:
            return {"status": "success", "anomalies": [], "note": "Insufficient data for z-score (need >=5 invoices)"}
        mu, sigma = stats.mean(vals), stats.pstdev(vals) or 1.0
        inv["z_score"] = (inv["line_total"] - mu) / sigma
        out = inv[inv["z_score"].abs() >= 2.5].sort_values("z_score", ascending=False)

        anomalies = [{
            "invoice_no": r["invoice_no"],
            "invoice_date": str(r["invoice_date"]),
            "amount": SAFE_ROUND(r["line_total"]),
            "z_score": SAFE_ROUND(r["z_score"])
        } for _, r in out.iterrows()]
        return {"status": "success", "anomalies": anomalies, "population_mean": SAFE_ROUND(mu), "population_stdev": SAFE_ROUND(sigma)}

    # ---------------- Gemini helpers ----------------
    def _summarize_with_ai(self, kpis: Dict[str, Any]) -> str:
        if not self.gemini_client:
            return "Gemini not initialized"
        prompt = f"Summarize this GST KPI data for a Chartered Accountant in plain English:\n{json.dumps(kpis, indent=2)}"
        resp = self.gemini_client.generate_content(prompt)
        return resp.text.strip()

    def _explain_anomalies_with_ai(self, anomalies: Dict[str, Any]) -> str:
        if not self.gemini_client:
            return "Gemini not initialized"
        prompt = f"Explain in plain English why these anomalies may be unusual:\n{json.dumps(anomalies, indent=2)}"
        resp = self.gemini_client.generate_content(prompt)
        return resp.text.strip()

    def _forecast_with_ai(self, kpis: Dict[str, Any]) -> str:
        if not self.gemini_client:
            return "Gemini not initialized"
        prompt = f"Based on these KPIs, forecast the likely GST liability for the next month:\n{json.dumps(kpis, indent=2)}"
        resp = self.gemini_client.generate_content(prompt)
        return resp.text.strip()

    def _nl_query(self, sales_path: Path, query: str) -> Dict[str, Any]:
        self._require_pandas()
        df = self._load_sales(sales_path)
        if not self.gemini_client:
            return {"status": "error", "message": "Gemini not initialized"}
        prompt = f"""
        Convert this natural language query into a pandas query string that works on the dataframe columns:
        {list(df.columns)}.
        Query: {query}
        """
        resp = self.gemini_client.generate_content(prompt)
        try:
            q = resp.text.strip().strip("`")
            result = df.query(q)
            return {"status": "success", "query": q, "rows": result.to_dict(orient="records")}
        except Exception as e:
            return {"status": "error", "message": f"Query failed: {e}", "raw_ai_output": resp.text}

    # ---------------- IO helpers ----------------
    def _require_pandas(self):
        if pd is None:
            raise RuntimeError("pandas required: pip install pandas")

    def _load_sales(self, path: Path) -> "pd.DataFrame":
        df = pd.read_excel(path) if path.suffix.lower() in (".xlsx",".xls") else pd.read_csv(path)
        for col in ["shipping_charges","other_charges","discount"]:
            if col not in df.columns:
                df[col] = 0.0
        return df

    def _load_purchases(self, path: Path) -> "pd.DataFrame":
        df = pd.read_excel(path) if path.suffix.lower() in (".xlsx",".xls") else pd.read_csv(path)
        for col in ["shipping_charges","other_charges","discount"]:
            if col not in df.columns:
                df[col] = 0.0
        return df

    def _totals(self, df: "pd.DataFrame") -> "pd.DataFrame":
        def taxable(row):
            gross = float(row["qty"]) * float(row["unit_price"])
            return SAFE_ROUND(max(gross - float(row["discount"]), 0.0) + float(row["shipping_charges"]) + float(row["other_charges"]))
        tmp = df.copy()
        tmp["tx"] = tmp.apply(taxable, axis=1)
        by_inv = tmp.groupby(["invoice_no"], as_index=False).agg({
            "tx": "sum",
            "is_interstate": "max",
            "gst_rate": "mean"
        })
        def split(row):
            rate = float(row["gst_rate"]) / 100.0
            if bool(row["is_interstate"]):
                igst = row["tx"] * rate
                return SAFE_ROUND(igst), 0.0, 0.0
            half = rate / 2.0
            return 0.0, SAFE_ROUND(row["tx"] * half), SAFE_ROUND(row["tx"] * half)
        igst, cgst, sgst = zip(*by_inv.apply(split, axis=1))
        by_inv["taxable_value"] = by_inv["tx"].map(SAFE_ROUND)
        by_inv["igst"], by_inv["cgst"], by_inv["sgst"] = igst, cgst, sgst
        by_inv["gross"] = by_inv["taxable_value"] + by_inv["igst"] + by_inv["cgst"] + by_inv["sgst"]
        return by_inv[["invoice_no","taxable_value","igst","cgst","sgst","gross"]]

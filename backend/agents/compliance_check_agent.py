from __future__ import annotations
from typing import Dict, Any, List, Tuple
from pathlib import Path
import datetime as dt
import re
import google.generativeai as genai
import pandas as pd
# try:
#     import pandas as pd
# except ImportError:
#     pd = None

from .base_agent import BaseAgent
# Reuse canonical helpers & state codes from your GST agent for consistency :contentReference[oaicite:3]{index=3}
from .gst_agent import validate_gstin, STATE_CODES  # type: ignore

DATE_FMT_TRIES = ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%Y/%m/%d")
NUMERIC_RATE_SET = {0, 5, 12, 18, 28}  # extend if needed


def parse_date_any(x):
    s = str(x)
    for f in DATE_FMT_TRIES:
        try:
            return dt.datetime.strptime(s, f).date()
        except Exception:
            continue
    return None


class ComplianceCheckAgent(BaseAgent):
    """
    Rule-based compliance checks on ledgers.
    Actions:
      - run_checks: run all checks and return findings + severities
    """
    def __init__(self, gemini_api_key: str):
        super().__init__("ComplianceCheckAgent")
        genai.configure(api_key=gemini_api_key)
        self.llm = genai.GenerativeModel("gemini-2.0-flash")

    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        action = task.get("action")
        p = task.get("params", {}) or {}
        if action == "run_checks":
            return self._run_checks(Path(p["sales"]), Path(p["purchases"]), period=p.get("period"))
        return {"status": "error", "message": f"Unknown action '{action}' for ComplianceCheckAgent"}

    # ---------------- checks ----------------
    # def _run_checks(self, sales_path: Path, purchases_path: Path, period: str | None) -> Dict[str, Any]:
    #     self._require_pandas()
    #     s = self._load(sales_path)
    #     p = self._load(purchases_path)
    #
    #     findings: List[Dict[str, Any]] = []
    #     findings += self._check_gstin_format(s, "buyer_gstin", ledger="sales")
    #     findings += self._check_gstin_format(p, "supplier_gstin", ledger="purchases")
    #     findings += self._check_state_codes(s, "place_of_supply_state_code", ledger="sales")
    #     findings += self._check_state_codes(p, "place_of_supply_state_code", ledger="purchases")
    #     findings += self._check_rate_values(s, ledger="sales")
    #     findings += self._check_rate_values(p, ledger="purchases")
    #     findings += self._check_invoice_duplicates(s, "sales")
    #     findings += self._check_invoice_duplicates(p, "purchases")
    #     if period:
    #         findings += self._check_period_dates(s, period, "sales")
    #         findings += self._check_period_dates(p, period, "purchases")
    #     findings += self._check_hsn_present(s, "sales")
    #     findings += self._check_hsn_present(p, "purchases")
    #     findings += self._check_interstate_consistency(s, "buyer_gstin", "sales")
    #     findings += self._check_interstate_consistency(p, "supplier_gstin", "purchases")
    #
    #     # Severity scoring
    #     severity_order = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}
    #     findings.sort(key=lambda x: severity_order.get(x["severity"], 1), reverse=True)
    #
    #     return {"status": "success", "findings": findings}
    def _run_checks(self, sales_path: Path, purchases_path: Path, period: str | None) -> Dict[str, Any]:
        self._require_pandas()
        s = self._load(sales_path)
        p = self._load(purchases_path)

        findings: List[Dict[str, Any]] = []

        # --- Run your existing rule-based checks ---
        findings += self._check_gstin_format(s, "buyer_gstin", ledger="sales")
        findings += self._check_gstin_format(p, "supplier_gstin", ledger="purchases")
        findings += self._check_state_codes(s, "place_of_supply_state_code", ledger="sales")
        findings += self._check_state_codes(p, "place_of_supply_state_code", ledger="purchases")
        findings += self._check_rate_values(s, ledger="sales")
        findings += self._check_rate_values(p, ledger="purchases")
        findings += self._check_invoice_duplicates(s, "sales")
        findings += self._check_invoice_duplicates(p, "purchases")

        if period:
            findings += self._check_period_dates(s, period, "sales")
            findings += self._check_period_dates(p, period, "purchases")

        findings += self._check_hsn_present(s, "sales")
        findings += self._check_hsn_present(p, "purchases")
        findings += self._check_interstate_consistency(s, "buyer_gstin", "sales")
        findings += self._check_interstate_consistency(p, "supplier_gstin", "purchases")

        # --- NEW: LLM-based compliance reasoning ---
        llm_feedback = self._llm_compliance_review(s, p, period)
        findings.extend(llm_feedback)

        # Severity scoring
        severity_order = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}
        findings.sort(key=lambda x: severity_order.get(x["severity"], 1), reverse=True)

        return {"status": "success", "findings": findings}

    def _llm_compliance_review(self, sales_df: pd.DataFrame, purchases_df: pd.DataFrame, period: str | None):
        sample_sales = sales_df.head(10).to_dict(orient="records")
        sample_purch = purchases_df.head(10).to_dict(orient="records")

        prompt = f"""
        You are a GST compliance auditor.
        Review the following SALES and PURCHASE ledger samples for hidden risks or anomalies 
        beyond simple format/rate checks.

        Consider:
        - Suspicious invoice sequencing
        - Unrealistic invoice amounts
        - GSTIN mismatches across ledgers
        - Cross-check sales vs purchases consistency
        - Any signs of tax evasion or reporting red flags

        Period under review: {period}

        SALES sample:
        {sample_sales}

        PURCHASE sample:
        {sample_purch}

        Return a JSON array of issues with keys:
        [ledger, invoice_no, issue, severity, hint].
        """

        try:
            resp = self.llm.generate_content(prompt)
            text = resp.text.strip()

            # Defensive parsing: expect JSON array, fallback to empty
            import json
            issues = json.loads(text) if text.startswith("[") else []
            return issues
        except Exception as e:
            return [{
                "ledger": "system",
                "invoice_no": None,
                "issue": f"LLM compliance check failed: {e}",
                "severity": "LOW"
            }]

    # --------------- individual rules ---------------
    def _check_gstin_format(self, df, col: str, ledger: str):
        rows = []
        for i, r in df.iterrows():
            g = str(r.get(col, "") or "")
            if g and not validate_gstin(g):
                rows.append(self._finding(
                    ledger, r, "Invalid GSTIN format", "HIGH",
                    hint="Check transposed characters or missing Z at pos 14 (…Z…)"
                ))
        return rows

    def _check_state_codes(self, df, col: str, ledger: str):
        rows = []
        for _, r in df.iterrows():
            code = str(r.get(col, "") or "").zfill(2)
            if code not in STATE_CODES:
                rows.append(self._finding(ledger, r, f"Invalid Place of Supply state code '{code}'", "HIGH"))
        return rows

    def _check_rate_values(self, df, ledger: str):
        rows = []
        for _, r in df.iterrows():
            rate = float(r.get("gst_rate", 0) or 0)
            if rate not in NUMERIC_RATE_SET:
                rows.append(self._finding(ledger, r, f"Non-standard GST rate {rate}%", "MEDIUM",
                                          hint=f"Allowed set: {sorted(NUMERIC_RATE_SET)}"))
        return rows

    def _check_invoice_duplicates(self, df, ledger: str):
        rows = []
        dup = df.groupby(["invoice_no", "invoice_date"]).size()
        for (inv, dtv), count in dup.items():
            if count > 1:
                rows.append({
                    "ledger": ledger,
                    "invoice_no": inv, "invoice_date": str(dtv),
                    "issue": f"Duplicate invoice lines detected (count={count})",
                    "severity": "LOW",
                    "hint": "Verify line consolidation or consider collapsing rows by HSN/rate."
                })
        return rows

    def _check_period_dates(self, df, period: str, ledger: str):
        rows = []
        y, m = period.split("-")
        start = dt.date(int(y), int(m), 1)
        if m == "12":
            end = dt.date(int(y)+1, 1, 1) - dt.timedelta(days=1)
        else:
            end = dt.date(int(y), int(m)+1, 1) - dt.timedelta(days=1)
        for _, r in df.iterrows():
            d = parse_date_any(r.get("invoice_date"))
            if not d or not (start <= d <= end):
                rows.append(self._finding(ledger, r, f"Invoice date {r.get('invoice_date')} outside period {period}", "MEDIUM"))
        return rows

    def _check_hsn_present(self, df, ledger: str):
        rows = []
        for _, r in df.iterrows():
            hsn = str(r.get("hsn", "") or "").strip()
            if not hsn:
                rows.append(self._finding(ledger, r, "Missing HSN code", "MEDIUM"))
        return rows

    def _check_interstate_consistency(self, df, party_col: str, ledger: str):
        """
        Heuristic: if party GSTIN's first 2 digits == PoS code, invoice should be intra-state (is_interstate=False)
        This is a soft rule; mismatches are flagged as LOW severity.
        """
        rows = []
        for _, r in df.iterrows():
            gstin = str(r.get(party_col, "") or "")
            pos = str(r.get("place_of_supply_state_code", "") or "").zfill(2)
            interstate = bool(r.get("is_interstate", False))
            if validate_gstin(gstin):
                party_state = gstin[:2]
                expected_inter = (party_state != pos)
                if expected_inter != interstate:
                    rows.append(self._finding(
                        ledger, r, "Interstate flag inconsistent with PoS vs GSTIN state", "LOW",
                        hint=f"Party state={party_state}, PoS={pos}, is_interstate={interstate}"
                    ))
        return rows

    # ---------------- utilities ----------------
    def _require_pandas(self):
        if pd is None:
            raise RuntimeError("pandas required: pip install pandas")

    def _load(self, path: Path):
        return pd.read_excel(path) if path.suffix.lower() in (".xlsx",".xls") else pd.read_csv(path)

    def _finding(self, ledger: str, row, issue: str, severity: str, hint: str | None = None) -> Dict[str, Any]:
        out = {
            "ledger": ledger,
            "invoice_no": row.get("invoice_no"),
            "invoice_date": str(row.get("invoice_date")),
            "issue": issue,
            "severity": severity,
        }
        if hint:
            out["hint"] = hint
        return out

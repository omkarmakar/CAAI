from .base_agent import BaseAgent
from typing import Dict, Any, List, Tuple, Optional
import csv
import os
import json
from datetime import datetime
from rapidfuzz import fuzz
import itertools

# Gemini import
try:
    import google.generativeai as genai
except ImportError:
    genai = None


class ReconAgent(BaseAgent):
    """
    AI-enhanced accounts reconciliation agent for Chartered Accountants:
    - Uses fuzzy matching (RapidFuzz) on invoice numbers and details
    - Computes a combined confidence score (invoice_no, details, amount proximity)
    - Proposes ranked candidate matches and supports combined-invoice heuristics
    - AI-powered insights on discrepancies and reconciliation patterns
    """

    def __init__(self, gemini_api_key: Optional[str] = None):
        super().__init__("ReconAgent")
        self.gemini_api_key = gemini_api_key
        self.gemini_client = None
        
        if self.gemini_api_key and genai:
            try:
                genai.configure(api_key=self.gemini_api_key)
                self.gemini_client = genai.GenerativeModel("gemini-2.0-flash")
            except Exception as e:
                print(f"⚠️ Failed to initialize Gemini for ReconAgent: {e}")

    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        action = task.get("action")
        params = task.get("params", {})

        if action == "match_payments":
            return self._match_payments(params)
        elif action == "summarize_discrepancies":
            return self._summarize_discrepancies(params)
        elif action == "explain_discrepancies":
            return self._explain_discrepancies(params)
        elif action == "reconciliation_insights":
            return self._reconciliation_insights(params)
        else:
            return {"status": "error", "message": f"Unknown action '{action}' for ReconAgent"}

    def _read_ledger(self, ledger_path: str) -> List[Dict[str, Any]]:
        invoices: List[Dict[str, Any]] = []
        if not os.path.isfile(ledger_path):
            return invoices
        with open(ledger_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for r in reader:
                try:
                    qty = float(r.get("qty") or 1)
                except Exception:
                    qty = 1.0
                try:
                    unit = float(r.get("unit_price") or r.get("invoice_value") or 0)
                except Exception:
                    unit = 0.0
                total = round(qty * unit, 2)
                inv = {
                    "invoice_no": (r.get("invoice_no") or r.get("inv_no") or "").strip() or None,
                    "date": r.get("invoice_date") or r.get("date") or None,
                    "details": (r.get("details") or r.get("item_name") or "").strip(),
                    "total": total,
                    "raw": r,
                }
                invoices.append(inv)
        return invoices

    def _read_payments(self, payments: Any, payments_file: str) -> List[Dict[str, Any]]:
        payment_rows: List[Dict[str, Any]] = []
        if payments_file and os.path.isfile(payments_file):
            with open(payments_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for r in reader:
                    try:
                        amt = float(r.get("amount") or r.get("amt") or 0)
                    except Exception:
                        amt = 0.0
                    payment_rows.append({"amount": amt, "date": r.get("date"), "reference": r.get("reference") or r.get("details") or ""})
        elif isinstance(payments, list):
            for p in payments:
                try:
                    amt = float(p.get("amount") or p.get("amt") or 0)
                except Exception:
                    amt = 0.0
                payment_rows.append({"amount": amt, "date": p.get("date"), "reference": p.get("reference") or p.get("details") or ""})
        return payment_rows

    def _amount_score(self, inv_amount: float, pay_amount: float) -> float:
        # Higher when amounts are close. Range approx 0..1
        if inv_amount <= 0 and pay_amount <= 0:
            return 0.0
        diff = abs(inv_amount - pay_amount)
        denom = max(inv_amount, pay_amount, 1.0)
        score = max(0.0, 1.0 - (diff / denom))
        return score

    def _make_candidate(self, payment: Dict[str, Any], invoice: Dict[str, Any]) -> Dict[str, Any]:
        ref = payment.get("reference") or ""
        inv_no = invoice.get("invoice_no") or ""
        details = invoice.get("details") or ""
        # invoice_no exact substring match
        invoice_no_match = 1.0 if inv_no and inv_no in ref else 0.0
        details_sim = (fuzz.token_sort_ratio(ref, details) / 100.0) if ref and details else 0.0
        amount_sim = self._amount_score(invoice.get("total", 0.0), payment.get("amount", 0.0))

        # weights (tuneable)
        w_no = 0.45
        w_amt = 0.40
        w_det = 0.15

        combined = invoice_no_match * w_no + amount_sim * w_amt + details_sim * w_det

        reasons = {
            "invoice_no_match": invoice_no_match,
            "amount_score": round(amount_sim, 3),
            "details_score": round(details_sim, 3),
        }

        return {
            "invoice": invoice,
            "score": round(combined, 3),
            "reasons": reasons,
        }

    def _find_combination_match(self, payment_amount: float, candidates: List[Dict[str, Any]], max_comb=3) -> Tuple[List[Dict[str, Any]], float]:
        """
        Try to find a small combination of invoices whose sums match the payment_amount within a tolerance.
        Returns (allocations_list, combined_score) or ([], 0.0)
        """
        # Limit search size
        pool = [c for c in candidates]
        if not pool:
            return [], 0.0
        tol = max(1.0, 0.01 * payment_amount)
        best = ([], 0.0)
        n = min(len(pool), 10)  # keep combinatorics bounded
        pool = pool[:n]
        for r in range(2, min(max_comb, len(pool)) + 1):
            for combo in itertools.combinations(pool, r):
                s = sum([c["invoice"]["total"] for c in combo])
                if abs(s - payment_amount) <= tol:
                    # compute combined score as mean of candidate scores + amount closeness factor
                    mean_score = sum(c["score"] for c in combo) / len(combo)
                    return ([{"invoice": c["invoice"], "allocated": c["invoice"]["total"]} for c in combo], round(mean_score, 3))
                # keep best approximate if closer
                closeness = 1.0 - (abs(s - payment_amount) / max(payment_amount, s, 1.0))
                combined_score = (sum(c["score"] for c in combo) / len(combo)) * 0.7 + closeness * 0.3
                if combined_score > best[1]:
                    best = ([{"invoice": c["invoice"], "allocated": c["invoice"]["total"]} for c in combo], round(combined_score, 3))
        return best

    def _match_payments(self, params: Dict[str, Any]) -> Dict[str, Any]:
        ledger_path = params.get("ledger") or os.path.join(os.path.dirname(__file__), "..", "ledger.csv")
        payments = params.get("payments")
        payments_file = params.get("payments_file")

        invoices = self._read_ledger(ledger_path)
        payment_rows = self._read_payments(payments, payments_file)

        if not payment_rows:
            return {"status": "success", "invoices_count": len(invoices), "invoices": invoices}

        proposals = []
        unmatched = []
        invoices_used = set()  # will store invoice indexes

        # Build candidate list for quick scoring
        for p in payment_rows:
            candidates = []
            for idx, inv in enumerate(invoices):
                if idx in invoices_used:
                    continue
                cand = self._make_candidate(p, inv)
                cand["_idx"] = idx
                candidates.append(cand)

            # sort candidates by score desc
            candidates.sort(key=lambda x: x["score"], reverse=True)

            # quick accept if top candidate has very high score
            if candidates and candidates[0]["score"] >= 0.78:
                top = candidates[0]
                proposals.append({"payment": p, "match_type": "single", "invoice": top["invoice"], "score": top["score"], "reasons": top["reasons"]})
                invoices_used.add(top["_idx"])
                continue

            # try exact invoice_no substring match
            ref = p.get("reference") or ""
            inv_no_match = None
            for cand in candidates:
                if cand["invoice"].get("invoice_no") and cand["invoice"]["invoice_no"] in ref:
                    inv_no_match = cand
                    break
            if inv_no_match and inv_no_match["score"] >= 0.5:
                proposals.append({"payment": p, "match_type": "single", "invoice": inv_no_match["invoice"], "score": inv_no_match["score"], "reasons": inv_no_match["reasons"]})
                invoices_used.add(inv_no_match["_idx"])
                continue

            # try combined-match heuristics (pairs/triples)
            combo_alloc, combo_score = self._find_combination_match(p["amount"], candidates, max_comb=3)
            if combo_alloc and combo_score >= 0.65:
                proposals.append({"payment": p, "match_type": "combined", "allocations": combo_alloc, "score": combo_score})
                for a in combo_alloc:
                    # allocations come from candidates with invoice dicts; find their index and add
                    # try to find index by matching invoice_no + total
                    for idx, inv in enumerate(invoices):
                        if inv.get("invoice_no") == a["invoice"].get("invoice_no") and inv.get("total") == a["invoice"].get("total"):
                            invoices_used.add(idx)
                            break
                continue

            # else return top-K candidates as proposals for human review
            topk = candidates[:5]
            # remove internal _idx when returning candidates
            for c in topk:
                c.pop("_idx", None)
            proposals.append({"payment": p, "match_type": "candidates", "candidates": topk})

        # collect unmatched (those proposals that are candidate lists with empty top matching)
        for pr in proposals:
            if pr["match_type"] == "candidates":
                unmatched.append(pr["payment"])

        return {"status": "success", "proposals": proposals, "unmatched_payments": unmatched}

    def _summarize_discrepancies(self, params: Dict[str, Any]) -> Dict[str, Any]:
        issues = params.get("issues", [])
        return {"status": "success", "discrepancies": len(issues), "items": issues}

    def _explain_discrepancies(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        AI-powered explanation of reconciliation discrepancies
        """
        discrepancies = params.get("discrepancies", [])
        context = params.get("context", "")
        
        if not self.gemini_client:
            return {
                "status": "error",
                "message": "Gemini AI required for discrepancy explanation"
            }
        
        try:
            prompt = f"""As a Chartered Accountant analyzing reconciliation discrepancies:

Context: {context}
Discrepancies: {json.dumps(discrepancies, indent=2)}

Provide professional analysis:
1. Discrepancy Classification:
   - Timing differences (in-transit items, post-dated)
   - Errors (data entry, transposition)
   - Missing entries
   - Duplicate entries
   - Amount mismatches
2. Root Cause Analysis for each discrepancy type
3. Materiality Assessment:
   - Significant items requiring immediate attention
   - Minor items that can be batch processed
4. Pattern Recognition:
   - Recurring issues
   - Systemic problems
   - One-time anomalies
5. Financial Impact:
   - Effect on reported balances
   - Cash flow implications
6. Recommended Actions:
   - Immediate steps
   - Long-term process improvements
   - Control enhancements
7. Documentation Requirements
8. Sign-off checklist

Format as professional reconciliation discrepancy report."""

            response = self.gemini_client.generate_content(prompt)
            
            return {
                "status": "success",
                "explanation": response.text.strip(),
                "discrepancies_count": len(discrepancies),
                "explained_at": self._get_timestamp()
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Discrepancy explanation failed: {str(e)}"
            }

    def _reconciliation_insights(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        AI-powered insights on reconciliation patterns and improvements
        """
        recon_history = params.get("recon_history", [])
        current_results = params.get("current_results", {})
        
        if not self.gemini_client:
            return {
                "status": "error",
                "message": "Gemini AI required for reconciliation insights"
            }
        
        try:
            prompt = f"""As a process improvement CA consultant, analyze reconciliation patterns:

Historical Reconciliation Data: {json.dumps(recon_history, indent=2)}
Current Reconciliation: {json.dumps(current_results, indent=2)}

Provide strategic insights:
1. Performance Metrics:
   - Match rate trends
   - Manual intervention rate
   - Time to reconcile trends
   - Error rate patterns
2. Quality Indicators:
   - Accuracy improvement/deterioration
   - Confidence score trends
   - Exception rate analysis
3. Process Efficiency:
   - Bottlenecks identified
   - Automation opportunities
   - Resource utilization
4. Control Environment:
   - Control weaknesses
   - Risk areas
   - Segregation of duties
5. Technology Recommendations:
   - System integrations needed
   - Automation scope
   - Data quality improvements
6. Training Needs:
   - Skill gaps
   - Common error patterns
7. Best Practices:
   - Industry benchmarking
   - Leading practice adoption
8. Action Plan:
   - Priority improvements
   - Quick wins
   - Long-term roadmap

Format as professional reconciliation process improvement report."""

            response = self.gemini_client.generate_content(prompt)
            
            return {
                "status": "success",
                "insights": response.text.strip(),
                "history_periods": len(recon_history),
                "generated_at": self._get_timestamp()
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Insights generation failed: {str(e)}"
            }

    def _get_timestamp(self) -> str:
        """Return current timestamp in ISO format"""
        return datetime.utcnow().isoformat() + "Z"

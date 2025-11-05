import tempfile
import csv
from agents.recon_agent import ReconAgent


def _write_temp_ledger(rows):
    tf = tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".csv", newline='', encoding='utf-8')
    fieldnames = list(rows[0].keys())
    writer = csv.DictWriter(tf, fieldnames=fieldnames)
    writer.writeheader()
    for r in rows:
        writer.writerow(r)
    tf.flush()
    tf.close()
    return tf.name


def test_match_payments_simple():
    agent = ReconAgent()
    # create a small ledger file with two invoices
    ledger_rows = [
        {"invoice_no": "1004", "invoice_date": "2025-01-01", "details": "Consulting services", "qty": "1", "unit_price": "20000"},
        {"invoice_no": "1006", "invoice_date": "2025-01-05", "details": "Development work", "qty": "1", "unit_price": "7000"},
    ]
    ledger_path = _write_temp_ledger(ledger_rows)

    payments = [
        {"amount": 20000, "date": "2025-01-11", "reference": "Invoice #1004 bank transfer"},
        {"amount": 7000, "date": "2025-01-16", "reference": "Payment for invoice 1006"},
    ]
    res = agent._match_payments({"payments": payments, "ledger": ledger_path})
    assert res.get("status") == "success"
    assert isinstance(res.get("proposals"), list)
    # Expect proposals for both payments
    assert len(res.get("proposals")) == 2
    # top proposals should include score or candidate lists
    for p in res.get("proposals"):
        assert "payment" in p
        assert p["match_type"] in ("single", "combined", "candidates")
        if p["match_type"] == "single":
            assert "score" in p and isinstance(p["score"], float)


def test_fuzzy_amount_and_details():
    agent = ReconAgent()
    # ledger with similar but not exact detail
    ledger_rows = [
        {"invoice_no": "INV-900", "invoice_date": "2025-02-01", "details": "Annual subscription premium", "qty": "1", "unit_price": "1500"},
    ]
    ledger_path = _write_temp_ledger(ledger_rows)
    payments = [
        {"amount": 1500, "date": "2025-02-10", "reference": "Annual subscrptn premium by bank"},
    ]
    res = agent._match_payments({"payments": payments, "ledger": ledger_path})
    assert res.get("status") == "success"
    props = res.get("proposals")
    assert len(props) == 1
    p = props[0]
    # fuzzy should produce either a single match or candidate list including the invoice
    if p["match_type"] == "single":
        assert p["score"] >= 0.5
    else:
        # candidates should include at least one candidate with invoice_no or details
        candidates = p.get("candidates", [])
        assert any(c["invoice"]["invoice_no"] == "INV-900" for c in candidates)

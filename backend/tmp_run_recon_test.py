import tempfile
import csv
import sys
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


def run():
    agent = ReconAgent()
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
    print("Result:", res)
    if res.get("status") != "success":
        print("FAIL: status not success")
        sys.exit(1)
    if not isinstance(res.get("proposals"), list) or len(res.get("proposals")) != 2:
        print("FAIL: proposals structure unexpected")
        sys.exit(1)
    print("Basic matching test: PASS")

    # fuzzy test
    ledger_rows = [
        {"invoice_no": "INV-900", "invoice_date": "2025-02-01", "details": "Annual subscription premium", "qty": "1", "unit_price": "1500"},
    ]
    ledger_path = _write_temp_ledger(ledger_rows)
    payments = [
        {"amount": 1500, "date": "2025-02-10", "reference": "Annual subscrptn premium by bank"},
    ]
    res2 = agent._match_payments({"payments": payments, "ledger": ledger_path})
    print("Fuzzy Result:", res2)
    if res2.get("status") != "success":
        print("FAIL: fuzzy status not success")
        sys.exit(1)
    if len(res2.get("proposals", [])) != 1:
        print("FAIL: fuzzy proposals count")
        sys.exit(1)
    print("Fuzzy matching test: PASS")

if __name__ == '__main__':
    run()

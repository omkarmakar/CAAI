"""Demo script to run AuditOrchestrator end-to-end with sample inputs."""
import os
import json
from pathlib import Path

# Ensure we can import package modules
import sys
sys.path.append(str(Path(__file__).resolve().parents[1]))

from backend.main import get_all_agents


def run_demo():
    agents = get_all_agents()
    orchestrator = agents.get("AuditOrchestrator")
    if not orchestrator:
        print("AuditOrchestrator not available")
        return

    # Sample params: point to ledger and use an inline payments list
    ledger_path = os.path.join(os.path.dirname(__file__), '..', 'ledger.csv')
    payments = [
        {"amount": 20000, "date": "2025-01-11", "reference": "Invoice #1004 bank transfer"},
        {"amount": 7000, "date": "2025-01-16", "reference": "Payment for invoice 1006"},
        {"amount": 15000, "date": "2025-01-06", "reference": "Rent payment"}
    ]

    params = {
        "document_params": {},
        "recon_params": {"ledger": ledger_path, "payments": payments}
    }

    result = orchestrator.execute({"action": "orchestrate_audit", "params": params})
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    run_demo()

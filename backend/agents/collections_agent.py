from .base_agent import BaseAgent
from typing import Dict, Any


class CollectionsAgent(BaseAgent):
    """
    Collections & Accounts Payable agent.
    - Prioritizes accounts by risk
    - Drafts reminders and follow-ups
    - Updates CRM or ledger with collection state
    """
    def __init__(self):
        super().__init__("CollectionsAgent")

    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        action = task.get("action")
        params = task.get("params", {})

        if action == "prioritize_accounts":
            return self._prioritize_accounts(params)
        elif action == "draft_reminder":
            return self._draft_reminder(params)
        else:
            return {"status": "error", "message": f"Unknown action '{action}' for CollectionsAgent"}

    def _prioritize_accounts(self, params: Dict[str, Any]) -> Dict[str, Any]:
        accounts = params.get("accounts", [])
        # Simple placeholder: sort by outstanding amount
        sorted_accounts = sorted(accounts, key=lambda a: a.get("outstanding", 0), reverse=True)
        return {"status": "success", "count": len(sorted_accounts), "priority_list": sorted_accounts}

    def _draft_reminder(self, params: Dict[str, Any]) -> Dict[str, Any]:
        recipient = params.get("recipient")
        amount = params.get("amount")
        return {"status": "success", "recipient": recipient, "message": f"Reminder drafted for {amount}"}

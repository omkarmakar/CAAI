from .base_agent import BaseAgent
from typing import Dict, Any, List


class AuditOrchestrator(BaseAgent):
    """
    High-level orchestrator that coordinates auditing-related agents and human review.
    It can dispatch tasks to DocAuditAgent, ReconAgent, CollectionsAgent, etc.,
    and consolidate results into an audit plan.
    """
    def __init__(self, available_agents: Dict[str, BaseAgent] = None):
        super().__init__("AuditOrchestrator")
        self.available_agents = available_agents or {}

    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        action = task.get("action")
        params = task.get("params", {})

        if action == "orchestrate_audit":
            return self._orchestrate_audit(params)
        else:
            return {"status": "error", "message": f"Unknown action '{action}' for AuditOrchestrator"}

    def _orchestrate_audit(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Example orchestration: run document audit and reconciliation, then summarize
        results: List[Dict[str, Any]] = []

        # Run document audit if available
        doc_agent = self.available_agents.get("DocAuditAgent")
        if doc_agent:
            results.append({"doc_audit": doc_agent.execute({"action": "audit_document", "params": params.get("document_params", {})})})

        # Run recon if available
        recon = self.available_agents.get("ReconAgent")
        if recon:
            results.append({"recon": recon.execute({"action": "match_payments", "params": params.get("recon_params", {})})})

        # Simple summarization
        return {"status": "success", "components": results}

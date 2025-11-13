from .base_agent import BaseAgent
from typing import Dict, Any, List, Optional
import json

# Gemini import
try:
    import google.generativeai as genai
except ImportError:
    genai = None


class AuditOrchestrator(BaseAgent):
    """
    AI-powered audit orchestrator for Chartered Accountants.
    Coordinates multiple auditing agents with intelligent risk assessment and planning.
    
    Actions:
    - orchestrate_audit: Coordinate multi-agent audit workflow
    - risk_assessment: AI-powered audit risk analysis
    - audit_planning: Generate comprehensive audit plan
    - summarize_findings: Consolidate and explain audit results
    """
    def __init__(self, available_agents: Dict[str, BaseAgent] = None, gemini_api_key: Optional[str] = None):
        super().__init__("AuditOrchestrator")
        self.available_agents = available_agents or {}
        self.gemini_api_key = gemini_api_key
        self.gemini_client = None
        
        if self.gemini_api_key and genai:
            try:
                genai.configure(api_key=self.gemini_api_key)
                self.gemini_client = genai.GenerativeModel("gemini-2.0-flash")
            except Exception as e:
                print(f"⚠️ Failed to initialize Gemini for AuditOrchestrator: {e}")

    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        action = task.get("action")
        params = task.get("params", {})

        if action == "orchestrate_audit":
            return self._orchestrate_audit(params)
        elif action == "risk_assessment":
            return self._risk_assessment(params)
        elif action == "audit_planning":
            return self._audit_planning(params)
        elif action == "summarize_findings":
            return self._summarize_findings(params)
        else:
            return {"status": "error", "message": f"Unknown action '{action}' for AuditOrchestrator"}

    def _orchestrate_audit(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Orchestrate comprehensive audit with AI-powered coordination
        """
        results: List[Dict[str, Any]] = []
        execution_log = []

        # Run document audit if available
        doc_agent = self.available_agents.get("DocAuditAgent")
        if doc_agent:
            execution_log.append("Executing document audit...")
            try:
                doc_result = doc_agent.execute({
                    "action": "audit_document", 
                    "params": params.get("document_params", {})
                })
                results.append({"agent": "DocAuditAgent", "result": doc_result})
                execution_log.append("Document audit completed")
            except Exception as e:
                execution_log.append(f"Document audit failed: {str(e)}")

        # Run reconciliation if available
        recon = self.available_agents.get("ReconAgent")
        if recon:
            execution_log.append("Executing reconciliation...")
            try:
                recon_result = recon.execute({
                    "action": "match_payments", 
                    "params": params.get("recon_params", {})
                })
                results.append({"agent": "ReconAgent", "result": recon_result})
                execution_log.append("Reconciliation completed")
            except Exception as e:
                execution_log.append(f"Reconciliation failed: {str(e)}")

        # Run compliance checks if available
        compliance = self.available_agents.get("ComplianceCheckAgent")
        if compliance:
            execution_log.append("Executing compliance checks...")
            try:
                compliance_result = compliance.execute({
                    "action": "run_checks",
                    "params": params.get("compliance_params", {})
                })
                results.append({"agent": "ComplianceCheckAgent", "result": compliance_result})
                execution_log.append("Compliance checks completed")
            except Exception as e:
                execution_log.append(f"Compliance checks failed: {str(e)}")

        # AI-powered consolidation and summary
        if self.gemini_client and results:
            try:
                summary = self._generate_audit_summary(results)
                return {
                    "status": "success",
                    "audit_components": results,
                    "ai_summary": summary,
                    "execution_log": execution_log,
                    "agents_executed": len(results)
                }
            except Exception as e:
                return {
                    "status": "success",
                    "audit_components": results,
                    "execution_log": execution_log,
                    "note": f"AI summary failed: {str(e)}"
                }
        
        return {
            "status": "success", 
            "audit_components": results,
            "execution_log": execution_log,
            "agents_executed": len(results)
        }

    def _generate_audit_summary(self, results: List[Dict[str, Any]]) -> str:
        """Generate AI-powered audit summary"""
        if not self.gemini_client:
            return "AI summary not available"
        
        prompt = f"""As a senior Chartered Accountant conducting an audit review, analyze these audit findings:

{json.dumps(results, indent=2)}

Provide a professional audit summary including:
1. Executive Summary
2. Key Findings by Category
3. Risk Assessment (High/Medium/Low risks identified)
4. Material Discrepancies and Issues
5. Compliance Status
6. Recommended Actions with Priority
7. Areas Requiring Further Investigation

Format as a professional audit report suitable for audit committee presentation."""

        response = self.gemini_client.generate_content(prompt)
        return response.text.strip()

    def _risk_assessment(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        AI-powered audit risk assessment
        """
        financial_data = params.get("financial_data", {})
        industry = params.get("industry", "")
        previous_audits = params.get("previous_audits", [])
        
        if not self.gemini_client:
            return {
                "status": "error",
                "message": "Gemini AI required for risk assessment"
            }
        
        try:
            prompt = f"""As an audit partner conducting risk assessment, analyze:

Industry: {industry}
Financial Data: {json.dumps(financial_data, indent=2)}
Previous Audit Findings: {json.dumps(previous_audits, indent=2)}

Provide comprehensive risk assessment:
1. Inherent Risk Analysis (High/Medium/Low)
2. Control Risk Evaluation
3. Detection Risk Factors
4. Material Misstatement Risk Areas
5. Fraud Risk Indicators
6. Industry-Specific Risk Factors
7. Recommended Audit Procedures by Risk Level
8. Materiality Thresholds

Format as professional audit risk assessment documentation."""

            response = self.gemini_client.generate_content(prompt)
            
            return {
                "status": "success",
                "risk_assessment": response.text.strip(),
                "industry": industry,
                "assessed_at": self._get_timestamp()
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Risk assessment failed: {str(e)}"
            }

    def _audit_planning(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive audit plan with AI assistance
        """
        client_info = params.get("client_info", {})
        audit_scope = params.get("audit_scope", "")
        timeline = params.get("timeline", "")
        
        if not self.gemini_client:
            return {
                "status": "error",
                "message": "Gemini AI required for audit planning"
            }
        
        try:
            prompt = f"""As an audit manager, create a comprehensive audit plan:

Client Information: {json.dumps(client_info, indent=2)}
Audit Scope: {audit_scope}
Timeline: {timeline}

Develop detailed audit plan covering:
1. Audit Objectives and Scope
2. Risk-Based Audit Approach
3. Audit Procedures by Account/Area:
   - Revenue Recognition
   - Inventory Valuation
   - Fixed Assets
   - Receivables/Payables
   - Cash and Bank
   - GST Compliance
4. Sampling Methodology
5. Timeline and Resource Allocation
6. Key Personnel and Responsibilities
7. Documentation Requirements
8. Client Coordination Points
9. Expected Deliverables

Format as professional audit engagement plan."""

            response = self.gemini_client.generate_content(prompt)
            
            return {
                "status": "success",
                "audit_plan": response.text.strip(),
                "client": client_info.get("name", "Unknown"),
                "prepared_at": self._get_timestamp()
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Audit planning failed: {str(e)}"
            }

    def _summarize_findings(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Consolidate and explain audit findings with AI insights
        """
        findings = params.get("findings", [])
        audit_type = params.get("audit_type", "statutory")
        
        if not self.gemini_client:
            return {
                "status": "success",
                "findings_count": len(findings),
                "findings": findings,
                "note": "AI summary not available"
            }
        
        try:
            prompt = f"""As a Chartered Accountant finalizing an audit, summarize these findings:

Audit Type: {audit_type}
Findings: {json.dumps(findings, indent=2)}

Provide:
1. Executive Summary for Management
2. Categorized Findings (Critical/High/Medium/Low)
3. Financial Impact Analysis
4. Root Cause Analysis
5. Management Response Required
6. Corrective Action Recommendations
7. Follow-up Items
8. Opinion Impact Assessment

Format as professional audit findings report suitable for audit committee."""

            response = self.gemini_client.generate_content(prompt)
            
            return {
                "status": "success",
                "findings_summary": response.text.strip(),
                "findings_count": len(findings),
                "audit_type": audit_type,
                "summarized_at": self._get_timestamp()
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Findings summarization failed: {str(e)}"
            }

    def _get_timestamp(self) -> str:
        """Return current timestamp in ISO format"""
        from datetime import datetime
        return datetime.utcnow().isoformat() + "Z"

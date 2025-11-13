from .base_agent import BaseAgent
from typing import Dict, Any, Optional
import os
from pathlib import Path

# Gemini import
try:
    import google.generativeai as genai
except ImportError:
    genai = None


class ContractAgent(BaseAgent):
    """
    AI-powered contract analysis agent for Chartered Accountants.
    Extracts key clauses, identifies risks, ensures compliance, and highlights financial implications.
    
    Actions:
    - analyze_contract: Comprehensive contract analysis
    - extract_obligations: Extract financial and legal obligations
    - risk_assessment: Identify contract risks
    - compare_contracts: Compare contract terms
    """
    def __init__(self, gemini_api_key: Optional[str] = None):
        super().__init__("ContractAgent")
        self.gemini_api_key = gemini_api_key
        self.gemini_client = None
        
        if self.gemini_api_key and genai:
            try:
                genai.configure(api_key=self.gemini_api_key)
                self.gemini_client = genai.GenerativeModel("gemini-2.0-flash")
            except Exception as e:
                print(f"⚠️ Failed to initialize Gemini for ContractAgent: {e}")

    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        action = task.get("action")
        params = task.get("params", {})

        if action == "analyze_contract":
            return self._analyze_contract(params)
        elif action == "extract_obligations":
            return self._extract_obligations(params)
        elif action == "risk_assessment":
            return self._risk_assessment(params)
        elif action == "compare_contracts":
            return self._compare_contracts(params)
        else:
            return {"status": "error", "message": f"Unknown action '{action}' for ContractAgent"}

    def _read_contract_text(self, path: str) -> str:
        """Read contract text from file"""
        if not path or not os.path.exists(path):
            return ""
        
        try:
            file_path = Path(path)
            # Handle different file types
            if file_path.suffix.lower() == '.pdf':
                # For PDF, we'd need a PDF library - placeholder
                return f"[PDF content from {path}]"
            else:
                # Text files
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()
        except Exception:
            return ""

    def _analyze_contract(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive AI-powered contract analysis
        """
        path = params.get("contract_path")
        contract_type = params.get("contract_type", "general")
        
        if not path or not os.path.exists(path):
            return {"status": "error", "message": "Contract file missing"}
        
        contract_text = self._read_contract_text(path)
        
        if not self.gemini_client:
            return {
                "status": "success",
                "summary": "Contract file found. AI analysis requires Gemini API key.",
                "file": path,
                "note": "Basic check completed - detailed AI analysis not available"
            }
        
        try:
            prompt = f"""As a Chartered Accountant reviewing contracts, analyze this {contract_type} contract:

Contract Content:
{contract_text[:10000]}  # Limit to first 10k chars

Provide comprehensive analysis:
1. Executive Summary
2. Parties Involved
3. Financial Terms:
   - Payment amounts and schedule
   - Pricing structure
   - Currency and exchange rate provisions
   - Late payment penalties
4. Key Commercial Terms:
   - Scope of work/services
   - Deliverables and milestones
   - Duration and renewal terms
5. Financial Obligations:
   - Advance payments
   - Performance guarantees
   - Retention money
   - Tax responsibilities
6. Risk Factors:
   - Liability caps and indemnities
   - Force majeure clauses
   - Termination penalties
   - Dispute resolution mechanisms
7. Compliance Considerations:
   - GST implications
   - TDS requirements
   - Regulatory compliance
8. Red Flags and Concerns
9. Recommendations for negotiation
10. Missing critical clauses

Format as professional contract review memorandum."""

            response = self.gemini_client.generate_content(prompt)
            
            return {
                "status": "success",
                "contract_path": path,
                "contract_type": contract_type,
                "analysis": response.text.strip(),
                "analyzed_at": self._get_timestamp()
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Contract analysis failed: {str(e)}"
            }

    def _extract_obligations(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract financial and legal obligations from contract
        """
        path = params.get("contract_path")
        
        if not path or not os.path.exists(path):
            return {"status": "error", "message": "Contract file missing"}
        
        contract_text = self._read_contract_text(path)
        
        if not self.gemini_client:
            return {
                "status": "error",
                "message": "Gemini AI required for obligation extraction"
            }
        
        try:
            prompt = f"""As a CA reviewing contractual obligations, extract all obligations from:

Contract:
{contract_text[:10000]}

Extract and categorize:
1. Financial Obligations:
   - Payment amounts and dates
   - Invoicing schedule
   - Tax payments (GST, TDS)
   - Guarantee/deposit amounts
   - Penalty provisions
2. Operational Obligations:
   - Deliverables with deadlines
   - Performance standards
   - Reporting requirements
3. Compliance Obligations:
   - Licenses and permits
   - Insurance requirements
   - Audit rights
   - Record keeping
4. Contingent Obligations:
   - Warranty commitments
   - Indemnity provisions
   - Minimum volume commitments
5. Timeline Summary:
   - Key dates and deadlines
   - Milestone schedule
   - Review/renewal dates

Format as obligation matrix suitable for tracking and compliance monitoring."""

            response = self.gemini_client.generate_content(prompt)
            
            return {
                "status": "success",
                "contract_path": path,
                "obligations": response.text.strip(),
                "extracted_at": self._get_timestamp()
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Obligation extraction failed: {str(e)}"
            }

    def _risk_assessment(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Identify and assess contract risks
        """
        path = params.get("contract_path")
        company_context = params.get("company_context", "")
        
        if not path or not os.path.exists(path):
            return {"status": "error", "message": "Contract file missing"}
        
        contract_text = self._read_contract_text(path)
        
        if not self.gemini_client:
            return {
                "status": "error",
                "message": "Gemini AI required for risk assessment"
            }
        
        try:
            prompt = f"""As a risk advisory CA, assess risks in this contract:

Company Context: {company_context}
Contract:
{contract_text[:10000]}

Provide risk assessment:
1. Financial Risks (High/Medium/Low):
   - Payment default risk
   - Currency risk
   - Price escalation risk
   - Working capital impact
2. Operational Risks:
   - Performance penalties
   - Capacity constraints
   - Dependency risks
3. Legal/Compliance Risks:
   - Unfavorable terms
   - Ambiguous clauses
   - Jurisdiction issues
   - Regulatory non-compliance
4. Reputational Risks
5. Risk Mitigation Strategies:
   - Negotiation points
   - Insurance coverage needed
   - Hedging mechanisms
   - Exit clauses to negotiate
6. Overall Risk Rating: High/Medium/Low
7. Recommended Actions before signing
8. Deal-breaker issues

Format as professional risk assessment report."""

            response = self.gemini_client.generate_content(prompt)
            
            return {
                "status": "success",
                "contract_path": path,
                "risk_assessment": response.text.strip(),
                "assessed_at": self._get_timestamp()
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Risk assessment failed: {str(e)}"
            }

    def _compare_contracts(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare multiple contract versions or alternatives
        """
        contracts = params.get("contracts", [])  # List of contract paths
        
        if len(contracts) < 2:
            return {"status": "error", "message": "At least 2 contracts required for comparison"}
        
        if not self.gemini_client:
            return {
                "status": "error",
                "message": "Gemini AI required for contract comparison"
            }
        
        try:
            contract_texts = []
            for i, path in enumerate(contracts[:3]):  # Limit to 3 contracts
                if os.path.exists(path):
                    text = self._read_contract_text(path)
                    contract_texts.append(f"CONTRACT {i+1} ({path}):\n{text[:5000]}")
            
            prompt = f"""As a CA comparing contract alternatives, analyze:

{chr(10).join(contract_texts)}

Provide comparative analysis:
1. Key Differences Summary
2. Financial Terms Comparison:
   - Pricing differences
   - Payment terms
   - Cost implications
3. Risk Profile Comparison
4. Flexibility and Exit Options
5. Compliance Requirements
6. Operational Impact
7. Pros and Cons of each option
8. Recommendation with rationale
9. Negotiation strategy

Format as comparative contract analysis."""

            response = self.gemini_client.generate_content(prompt)
            
            return {
                "status": "success",
                "contracts_compared": len(contract_texts),
                "comparison": response.text.strip(),
                "compared_at": self._get_timestamp()
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Contract comparison failed: {str(e)}"
            }

    def _get_timestamp(self) -> str:
        """Return current timestamp in ISO format"""
        from datetime import datetime
        return datetime.utcnow().isoformat() + "Z"

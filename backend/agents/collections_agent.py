from .base_agent import BaseAgent
from typing import Dict, Any, List, Optional
import json

# Gemini import
try:
    import google.generativeai as genai
except ImportError:
    genai = None


class CollectionsAgent(BaseAgent):
    """
    AI-powered Collections & Accounts Receivable agent for CAs.
    Intelligently prioritizes accounts, drafts professional reminders, and optimizes collection strategies.
    
    Actions:
    - prioritize_accounts: AI-driven account prioritization by risk
    - draft_reminder: Generate professional collection reminders
    - collection_strategy: Develop optimal collection approach
    - aging_analysis: Analyze receivables aging with insights
    """
    def __init__(self, gemini_api_key: Optional[str] = None):
        super().__init__("CollectionsAgent")
        self.gemini_api_key = gemini_api_key
        self.gemini_client = None
        
        if self.gemini_api_key and genai:
            try:
                genai.configure(api_key=self.gemini_api_key)
                self.gemini_client = genai.GenerativeModel("gemini-2.0-flash")
            except Exception as e:
                print(f"⚠️ Failed to initialize Gemini for CollectionsAgent: {e}")

    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        action = task.get("action")
        params = task.get("params", {})

        if action == "prioritize_accounts":
            return self._prioritize_accounts(params)
        elif action == "draft_reminder":
            return self._draft_reminder(params)
        elif action == "collection_strategy":
            return self._collection_strategy(params)
        elif action == "aging_analysis":
            return self._aging_analysis(params)
        else:
            return {"status": "error", "message": f"Unknown action '{action}' for CollectionsAgent"}

    def _prioritize_accounts(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        AI-powered account prioritization with risk scoring
        """
        accounts = params.get("accounts", [])
        
        if not accounts:
            return {"status": "success", "count": 0, "priority_list": []}
        
        # Basic sorting by outstanding amount
        sorted_accounts = sorted(accounts, key=lambda a: a.get("outstanding", 0), reverse=True)
        
        if not self.gemini_client:
            return {
                "status": "success",
                "count": len(sorted_accounts),
                "priority_list": sorted_accounts,
                "note": "Basic prioritization - AI analysis not available"
            }
        
        try:
            prompt = f"""As a credit control manager, analyze and prioritize these accounts receivable:

Accounts: {json.dumps(accounts, indent=2)}

For each account, assess:
1. Collection Priority (Critical/High/Medium/Low)
2. Risk Score (1-10, with 10 being highest risk)
3. Risk Factors:
   - Days overdue
   - Outstanding amount
   - Payment history
   - Customer creditworthiness signals
4. Recommended Action:
   - Immediate legal action
   - Final notice
   - Friendly reminder
   - Payment plan offer
5. Optimal contact approach (email/call/visit)
6. Suggested timeline for follow-up

Provide prioritized list with actionable recommendations for CA review."""

            response = self.gemini_client.generate_content(prompt)
            
            return {
                "status": "success",
                "count": len(sorted_accounts),
                "basic_priority_list": sorted_accounts[:10],  # Top 10 by amount
                "ai_analysis": response.text.strip(),
                "analyzed_at": self._get_timestamp()
            }
        except Exception as e:
            return {
                "status": "success",
                "count": len(sorted_accounts),
                "priority_list": sorted_accounts,
                "note": f"AI analysis failed: {str(e)}"
            }

    def _draft_reminder(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate professional collection reminder with appropriate tone
        """
        recipient = params.get("recipient", "")
        recipient_name = params.get("recipient_name", "Valued Customer")
        amount = params.get("amount", 0)
        invoice_no = params.get("invoice_no", "")
        due_date = params.get("due_date", "")
        days_overdue = params.get("days_overdue", 0)
        tone = params.get("tone", "friendly")  # friendly, firm, final, legal
        
        if not self.gemini_client:
            return {
                "status": "success",
                "recipient": recipient,
                "message": f"Dear {recipient_name},\n\nThis is a reminder about the outstanding amount of ₹{amount:,.2f} for invoice {invoice_no}.\n\nPlease arrange payment at the earliest.\n\nThank you,\nAccounts Department",
                "note": "Basic template - AI drafting not available"
            }
        
        try:
            prompt = f"""As a professional Chartered Accountant, draft a collection reminder email:

Recipient: {recipient_name}
Outstanding Amount: ₹{amount:,.2f}
Invoice Number: {invoice_no}
Original Due Date: {due_date}
Days Overdue: {days_overdue}
Tone Required: {tone}

Draft professional email considering:
1. Appropriate tone for overdue period:
   - Friendly: 0-30 days overdue
   - Firm: 31-60 days overdue
   - Final: 61-90 days overdue
   - Legal: 90+ days overdue
2. Clear payment details
3. Payment options/plans if applicable
4. Consequences of non-payment (if firm/final/legal tone)
5. Contact information for queries
6. Professional yet assertive language

Format as ready-to-send email with subject line."""

            response = self.gemini_client.generate_content(prompt)
            
            return {
                "status": "success",
                "recipient": recipient,
                "recipient_name": recipient_name,
                "amount": amount,
                "invoice_no": invoice_no,
                "message": response.text.strip(),
                "tone": tone,
                "generated_at": self._get_timestamp()
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Reminder drafting failed: {str(e)}"
            }

    def _collection_strategy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Develop optimal collection strategy for accounts
        """
        portfolio = params.get("portfolio", [])
        industry = params.get("industry", "")
        collection_costs = params.get("collection_costs", {})
        
        if not self.gemini_client:
            return {
                "status": "error",
                "message": "Gemini AI required for strategy development"
            }
        
        try:
            prompt = f"""As a credit control consultant, develop collection strategy:

Receivables Portfolio: {json.dumps(portfolio, indent=2)}
Industry: {industry}
Collection Costs: {json.dumps(collection_costs, indent=2)}

Provide comprehensive collection strategy:
1. Segmentation Strategy:
   - High value accounts (VIP treatment)
   - Standard accounts
   - Small balance accounts (cost-benefit analysis)
2. Collection Timeline by Segment:
   - Day 0-15: Proactive reminders
   - Day 16-30: Phone follow-ups
   - Day 31-60: Escalation process
   - Day 61-90: Final demands
   - Day 90+: Legal action consideration
3. Communication Channels by segment
4. Incentive Programs:
   - Early payment discounts
   - Payment plan options
5. Cost-Benefit Analysis:
   - When to write off
   - When to engage collection agency
   - Legal action threshold
6. Relationship Management:
   - Preserving customer relationships
   - Win-win negotiations
7. Performance Metrics to track
8. Team training requirements

Format as professional credit control strategy document."""

            response = self.gemini_client.generate_content(prompt)
            
            return {
                "status": "success",
                "collection_strategy": response.text.strip(),
                "portfolio_size": len(portfolio),
                "prepared_at": self._get_timestamp()
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Strategy development failed: {str(e)}"
            }

    def _aging_analysis(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze receivables aging with AI insights
        """
        aging_data = params.get("aging_data", {})
        comparison_period = params.get("comparison_period", "previous_month")
        
        if not self.gemini_client:
            return {
                "status": "error",
                "message": "Gemini AI required for aging analysis"
            }
        
        try:
            prompt = f"""As a Chartered Accountant analyzing receivables, review:

Aging Data: {json.dumps(aging_data, indent=2)}
Comparison Period: {comparison_period}

Provide detailed aging analysis:
1. Aging Summary:
   - Current (0-30 days): Amount & %
   - 31-60 days: Amount & %
   - 61-90 days: Amount & %
   - 90+ days: Amount & %
2. Trend Analysis vs {comparison_period}:
   - Improving/deteriorating
   - Bucket migration analysis
3. Collection Effectiveness Index
4. Days Sales Outstanding (DSO)
5. Bad Debt Risk Assessment:
   - Provision requirements
   - Write-off recommendations
6. Red Flags and Concerns
7. Customer Concentration Risk
8. Action Items by priority:
   - Immediate attention required
   - Follow-up needed
   - Monitoring required
9. Root Cause Analysis
10. Recommendations for improvement

Format as professional receivables aging analysis report."""

            response = self.gemini_client.generate_content(prompt)
            
            return {
                "status": "success",
                "aging_analysis": response.text.strip(),
                "comparison_period": comparison_period,
                "analyzed_at": self._get_timestamp()
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Aging analysis failed: {str(e)}"
            }

    def _get_timestamp(self) -> str:
        """Return current timestamp in ISO format"""
        from datetime import datetime
        return datetime.utcnow().isoformat() + "Z"

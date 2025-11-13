from .base_agent import BaseAgent
from typing import Dict, Any, Optional
import json

# Gemini import
try:
    import google.generativeai as genai
except ImportError:
    genai = None


class TreasuryAgent(BaseAgent):
    """
    AI-powered treasury agent for Chartered Accountants.
    Advanced cash management, forecasting, and liquidity optimization.
    
    Actions:
    - forecast_cash: AI-powered cash flow forecasting
    - what_if: Scenario analysis for treasury planning
    - optimize_liquidity: Liquidity optimization recommendations
    - working_capital: Working capital management insights
    """
    def __init__(self, gemini_api_key: Optional[str] = None):
        super().__init__("TreasuryAgent")
        self.gemini_api_key = gemini_api_key
        self.gemini_client = None
        
        if self.gemini_api_key and genai:
            try:
                genai.configure(api_key=self.gemini_api_key)
                self.gemini_client = genai.GenerativeModel("gemini-2.0-flash")
            except Exception as e:
                print(f"⚠️ Failed to initialize Gemini for TreasuryAgent: {e}")

    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        action = task.get("action")
        params = task.get("params", {})

        if action == "forecast_cash":
            return self._forecast_cash(params)
        elif action == "what_if":
            return self._what_if(params)
        elif action == "optimize_liquidity":
            return self._optimize_liquidity(params)
        elif action == "working_capital":
            return self._working_capital(params)
        else:
            return {"status": "error", "message": f"Unknown action '{action}' for TreasuryAgent"}

    def _forecast_cash(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        AI-powered cash flow forecasting
        """
        horizon = params.get("days", 30)
        historical_data = params.get("historical_data", [])
        assumptions = params.get("assumptions", {})
        
        if not self.gemini_client:
            return {
                "status": "success",
                "horizon_days": horizon,
                "forecast": {"balance": 10000},
                "note": "Basic forecast - AI analysis not available"
            }
        
        try:
            prompt = f"""As a treasury manager CA, create detailed cash flow forecast:

Forecast Horizon: {horizon} days
Historical Cash Data: {json.dumps(historical_data, indent=2)}
Assumptions: {json.dumps(assumptions, indent=2)}

Provide comprehensive forecast:
1. Opening Cash Balance
2. Expected Cash Inflows:
   - Customer collections (by aging bucket)
   - Other operating receipts
   - Investment income
   - Loan proceeds (if any)
   - Daily/weekly breakdown
3. Expected Cash Outflows:
   - Supplier payments schedule
   - Payroll and benefits
   - Tax payments (GST, TDS, Income Tax)
   - Loan repayments
   - Capital expenditure
   - Operating expenses
   - Daily/weekly breakdown
4. Net Cash Flow by period
5. Closing Cash Balance forecast
6. Peak funding requirements
7. Surplus cash deployment opportunities
8. Key Assumptions and Sensitivities
9. Risk Factors:
   - Collection delays
   - Unexpected expenses
   - Timing risks
10. Recommended Actions:
    - Working capital optimization
    - Funding arrangements needed
    - Investment opportunities

Format as professional treasury forecast suitable for CFO/board review."""

            response = self.gemini_client.generate_content(prompt)
            
            return {
                "status": "success",
                "horizon_days": horizon,
                "forecast_analysis": response.text.strip(),
                "generated_at": self._get_timestamp()
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Cash forecast failed: {str(e)}"
            }

    def _what_if(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Advanced scenario analysis for treasury planning
        """
        scenario = params.get("scenario", "default")
        base_case = params.get("base_case", {})
        variables = params.get("variables", {})
        
        if not self.gemini_client:
            return {
                "status": "success",
                "scenario": scenario,
                "impact": "estimate generated - AI analysis not available"
            }
        
        try:
            prompt = f"""As a treasury risk manager, perform what-if scenario analysis:

Scenario Name: {scenario}
Base Case: {json.dumps(base_case, indent=2)}
Variable Changes: {json.dumps(variables, indent=2)}

Analyze and provide:
1. Scenario Description and Assumptions
2. Impact Analysis:
   - Cash position impact
   - Liquidity ratio changes
   - Working capital effect
   - Debt covenant implications
3. Quantitative Assessment:
   - Best case outcome
   - Most likely outcome
   - Worst case outcome
   - Probability-weighted average
4. Timeline of Effects:
   - Immediate impact (0-30 days)
   - Short term (1-3 months)
   - Medium term (3-12 months)
5. Mitigation Strategies:
   - Preventive measures
   - Contingency plans
   - Risk transfer options
6. Decision Triggers:
   - When to act
   - Leading indicators to monitor
7. Comparison with Base Case:
   - Key variances
   - Break-even analysis
8. Strategic Recommendations:
   - Optimal course of action
   - Alternative approaches
   - Risk-reward assessment

Format as professional scenario analysis for management decision-making."""

            response = self.gemini_client.generate_content(prompt)
            
            return {
                "status": "success",
                "scenario": scenario,
                "analysis": response.text.strip(),
                "generated_at": self._get_timestamp()
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Scenario analysis failed: {str(e)}"
            }

    def _optimize_liquidity(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Liquidity optimization recommendations
        """
        current_position = params.get("current_position", {})
        constraints = params.get("constraints", {})
        objectives = params.get("objectives", [])
        
        if not self.gemini_client:
            return {
                "status": "error",
                "message": "Gemini AI required for liquidity optimization"
            }
        
        try:
            prompt = f"""As a treasury optimization consultant CA, recommend liquidity improvements:

Current Liquidity Position: {json.dumps(current_position, indent=2)}
Constraints: {json.dumps(constraints, indent=2)}
Objectives: {json.dumps(objectives, indent=2)}

Provide optimization strategy:
1. Current State Assessment:
   - Liquidity ratios (Current, Quick, Cash)
   - Cash conversion cycle
   - Days cash on hand
   - Idle cash levels
2. Optimization Opportunities:
   - Receivables acceleration:
     * Early payment discounts
     * Factoring/discounting
     * Collection efficiency
   - Payables optimization:
     * Payment terms extension
     * Dynamic discounting
     * Supply chain financing
   - Inventory management:
     * Just-in-time approaches
     * Consignment arrangements
     * Working capital release
3. Cash Pooling Strategies:
   - Notional pooling
   - Physical pooling
   - Zero balance accounts
4. Short-term Investment Options:
   - Liquid mutual funds
   - Treasury bills
   - Fixed deposits
   - Risk-return trade-offs
5. Funding Optimization:
   - Credit line structuring
   - Cost of funds analysis
   - Funding mix optimization
6. Technology Solutions:
   - Real-time cash visibility
   - Payment automation
   - Cash forecasting tools
7. Policy Recommendations:
   - Minimum cash balance
   - Investment guidelines
   - Approval authorities
8. Implementation Roadmap:
   - Quick wins (0-3 months)
   - Medium term (3-12 months)
   - Long term (1-3 years)

Format as professional treasury optimization proposal."""

            response = self.gemini_client.generate_content(prompt)
            
            return {
                "status": "success",
                "optimization_strategy": response.text.strip(),
                "prepared_at": self._get_timestamp()
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Liquidity optimization failed: {str(e)}"
            }

    def _working_capital(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Working capital management insights
        """
        financial_data = params.get("financial_data", {})
        industry = params.get("industry", "")
        
        if not self.gemini_client:
            return {
                "status": "error",
                "message": "Gemini AI required for working capital analysis"
            }
        
        try:
            prompt = f"""As a working capital specialist CA, analyze:

Financial Data: {json.dumps(financial_data, indent=2)}
Industry: {industry}

Provide working capital analysis:
1. Working Capital Metrics:
   - Working capital ratio
   - Net working capital
   - Working capital turnover
   - Cash conversion cycle components:
     * Days inventory outstanding (DIO)
     * Days sales outstanding (DSO)
     * Days payables outstanding (DPO)
2. Industry Benchmarking:
   - Peer comparison
   - Best-in-class standards
   - Gap analysis
3. Trend Analysis:
   - Historical performance
   - Seasonality patterns
   - Growth impact
4. Efficiency Assessment:
   - Receivables management
   - Inventory management
   - Payables management
5. Cash Flow Impact:
   - Working capital as % of revenue
   - Incremental working capital needs
   - Cash trapped in working capital
6. Optimization Opportunities:
   - Receivables improvement potential
   - Inventory reduction scope
   - Payables optimization
   - Estimated cash release
7. Risk Assessment:
   - Over-trading risk
   - Liquidity constraints
   - Credit risk
8. Action Plan:
   - Priority initiatives
   - Responsibility matrix
   - Target metrics
   - Timeline

Format as professional working capital management report."""

            response = self.gemini_client.generate_content(prompt)
            
            return {
                "status": "success",
                "working_capital_analysis": response.text.strip(),
                "industry": industry,
                "analyzed_at": self._get_timestamp()
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Working capital analysis failed: {str(e)}"
            }

    def _get_timestamp(self) -> str:
        """Return current timestamp in ISO format"""
        from datetime import datetime
        return datetime.utcnow().isoformat() + "Z"

from .base_agent import BaseAgent
from typing import Dict, Any, List, Optional
import json

# Gemini import
try:
    import google.generativeai as genai
except ImportError:
    genai = None


class CashFlowAgent(BaseAgent):
    """
    AI-powered cash flow management agent for Chartered Accountants.
    Monitors bank data, forecasts cash flow, analyzes trends, and provides liquidity alerts.
    
    Actions:
    - update_forecast: Update cash flow forecast with AI insights
    - alert_low_liquidity: Monitor and alert on liquidity issues
    - analyze_cash_trend: AI-powered cash flow trend analysis
    - scenario_analysis: What-if scenarios for cash planning
    """
    def __init__(self, gemini_api_key: Optional[str] = None):
        super().__init__("CashFlowAgent")
        self.gemini_api_key = gemini_api_key
        self.gemini_client = None
        
        if self.gemini_api_key and genai:
            try:
                genai.configure(api_key=self.gemini_api_key)
                self.gemini_client = genai.GenerativeModel("gemini-2.0-flash")
            except Exception as e:
                print(f"⚠️ Failed to initialize Gemini for CashFlowAgent: {e}")

    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        action = task.get("action")
        params = task.get("params", {})

        if action == "update_forecast":
            return self._update_forecast(params)
        elif action == "alert_low_liquidity":
            return self._alert_low_liquidity(params)
        elif action == "analyze_cash_trend":
            return self._analyze_cash_trend(params)
        elif action == "scenario_analysis":
            return self._scenario_analysis(params)
        else:
            return {"status": "error", "message": f"Unknown action '{action}' for CashFlowAgent"}

    def _update_forecast(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update cash flow forecast with AI-powered analysis
        """
        source = params.get("source", "")  # bank feed file path
        historical_data = params.get("historical_data", [])
        forecast_period = params.get("forecast_period", 30)  # days
        
        if not self.gemini_client:
            return {
                "status": "success",
                "updated": True,
                "forecast_period": forecast_period,
                "note": "Basic forecast updated - AI analysis not available"
            }
        
        try:
            prompt = f"""As a Chartered Accountant specializing in cash flow management, analyze and forecast:

Forecast Period: {forecast_period} days
Historical Cash Flow Data: {json.dumps(historical_data, indent=2)}
Bank Feed Source: {source if source else 'Manual entry'}

Provide comprehensive cash flow forecast:
1. Expected Cash Inflows (by category)
   - Customer receipts
   - Other income
2. Expected Cash Outflows (by category)
   - Supplier payments
   - Operating expenses
   - GST/tax payments
   - Loan repayments
3. Net Cash Position forecast
4. Key Assumptions
5. Risk Factors affecting forecast
6. Recommended Actions for cash optimization
7. Early warning indicators to monitor

Format as professional treasury report."""

            response = self.gemini_client.generate_content(prompt)
            
            return {
                "status": "success",
                "updated": True,
                "forecast": response.text.strip(),
                "forecast_period": forecast_period,
                "generated_at": self._get_timestamp()
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Forecast update failed: {str(e)}"
            }

    def _alert_low_liquidity(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Monitor and alert on liquidity issues with AI insights
        """
        threshold = params.get("threshold", 50000)  # minimum cash threshold
        current_balance = params.get("current_balance", 0)
        projected_cash = params.get("projected_cash", [])
        
        alert_triggered = current_balance < threshold
        
        if not self.gemini_client:
            return {
                "status": "success",
                "threshold": threshold,
                "current_balance": current_balance,
                "alert": alert_triggered,
                "severity": "high" if alert_triggered else "normal"
            }
        
        try:
            if alert_triggered or any(p.get("balance", float('inf')) < threshold for p in projected_cash):
                prompt = f"""As a treasury manager, analyze this liquidity situation:

Minimum Cash Threshold: ₹{threshold:,.2f}
Current Balance: ₹{current_balance:,.2f}
Projected Cash Positions: {json.dumps(projected_cash, indent=2)}

Provide urgent liquidity analysis:
1. Severity Assessment (Critical/High/Medium)
2. Immediate Actions Required
3. Sources of Quick Liquidity:
   - Accelerating receivables
   - Credit line utilization
   - Short-term financing options
4. Expense deferral opportunities
5. Communication plan for stakeholders
6. Contingency measures
7. Preventive measures for future

Format as urgent treasury advisory."""

                response = self.gemini_client.generate_content(prompt)
                
                return {
                    "status": "success",
                    "threshold": threshold,
                    "current_balance": current_balance,
                    "alert": True,
                    "severity": "high",
                    "ai_advisory": response.text.strip(),
                    "generated_at": self._get_timestamp()
                }
            else:
                return {
                    "status": "success",
                    "threshold": threshold,
                    "current_balance": current_balance,
                    "alert": False,
                    "severity": "normal",
                    "message": "Cash position is healthy"
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Liquidity alert analysis failed: {str(e)}"
            }

    def _analyze_cash_trend(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        AI-powered cash flow trend analysis
        """
        cash_flow_data = params.get("cash_flow_data", [])
        period = params.get("period", "monthly")
        
        if not self.gemini_client:
            return {
                "status": "error",
                "message": "Gemini AI required for trend analysis"
            }
        
        try:
            prompt = f"""As a financial analyst CA, analyze cash flow trends:

Period: {period}
Cash Flow Data: {json.dumps(cash_flow_data, indent=2)}

Provide detailed trend analysis:
1. Overall Cash Flow Trend (improving/deteriorating/stable)
2. Inflow Analysis:
   - Customer payment patterns
   - Collection efficiency trends
   - Seasonal variations
3. Outflow Analysis:
   - Payment timing patterns
   - Major expense categories
   - Working capital changes
4. Cash Conversion Cycle Analysis
5. Key Performance Indicators:
   - Operating cash flow ratio
   - Cash flow coverage ratio
   - Days cash on hand
6. Red Flags and Concerns
7. Opportunities for improvement
8. Strategic recommendations

Format as professional cash flow analysis report."""

            response = self.gemini_client.generate_content(prompt)
            
            return {
                "status": "success",
                "trend_analysis": response.text.strip(),
                "period": period,
                "data_points": len(cash_flow_data),
                "analyzed_at": self._get_timestamp()
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Trend analysis failed: {str(e)}"
            }

    def _scenario_analysis(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        What-if scenario analysis for cash planning
        """
        base_case = params.get("base_case", {})
        scenarios = params.get("scenarios", [])
        
        if not self.gemini_client:
            return {
                "status": "error",
                "message": "Gemini AI required for scenario analysis"
            }
        
        try:
            prompt = f"""As a CFO conducting scenario planning, analyze:

Base Case: {json.dumps(base_case, indent=2)}
Scenarios to Evaluate: {json.dumps(scenarios, indent=2)}

For each scenario, provide:
1. Impact on Cash Position
2. Timeline of effects
3. Mitigating actions available
4. Probability assessment
5. Risk level (High/Medium/Low)

Then provide:
6. Most Likely Scenario
7. Best Case Scenario
8. Worst Case Scenario
9. Recommended Hedging Strategies
10. Decision Points and triggers
11. Contingency Plans

Format as professional scenario analysis for board presentation."""

            response = self.gemini_client.generate_content(prompt)
            
            return {
                "status": "success",
                "scenario_analysis": response.text.strip(),
                "scenarios_evaluated": len(scenarios),
                "analyzed_at": self._get_timestamp()
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Scenario analysis failed: {str(e)}"
            }

    def _get_timestamp(self) -> str:
        """Return current timestamp in ISO format"""
        from datetime import datetime
        return datetime.utcnow().isoformat() + "Z"

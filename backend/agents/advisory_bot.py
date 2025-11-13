from .base_agent import BaseAgent
from typing import Dict, Any, Optional
import json

# Gemini import
try:
    import google.generativeai as genai
except ImportError:
    genai = None


class AdvisoryBot(BaseAgent):
    """
    Advisory agent with Gemini AI: provides professional tax-saving recommendations, 
    cashflow forecasts and business insights suitable for Chartered Accountants.
    
    Actions:
    - recommendations: AI-powered tax and financial recommendations
    - forecast: AI-powered business forecast analysis
    - analyze_financials: Comprehensive financial analysis with CA-level insights
    - tax_planning: Strategic tax planning recommendations
    """
    def __init__(self, gemini_api_key: Optional[str] = None):
        super().__init__("AdvisoryBot")
        self.gemini_api_key = gemini_api_key
        self.gemini_client = None
        
        if self.gemini_api_key and genai:
            try:
                genai.configure(api_key=self.gemini_api_key)
                self.gemini_client = genai.GenerativeModel("gemini-2.0-flash")
            except Exception as e:
                print(f"⚠️ Failed to initialize Gemini for AdvisoryBot: {e}")

    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        action = task.get("action")
        params = task.get("params", {})

        if action == "recommendations":
            return self._recommendations(params)
        elif action == "forecast":
            return self._forecast(params)
        elif action == "analyze_financials":
            return self._analyze_financials(params)
        elif action == "tax_planning":
            return self._tax_planning(params)
        else:
            return {"status": "error", "message": f"Unknown action '{action}' for AdvisoryBot"}

    def _recommendations(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate AI-powered tax-saving and financial recommendations for CAs
        """
        context = params.get("context", "")
        financial_data = params.get("financial_data", {})
        
        if not self.gemini_client:
            # Fallback recommendations
            return {
                "status": "success", 
                "recommendations": [
                    "Consider accelerating receivables to improve cash flow",
                    "Review and optimize input tax credit utilization",
                    "Evaluate opportunities for tax deductions under Section 80C-80U",
                    "Consider capital expenditure planning for depreciation benefits"
                ],
                "note": "Gemini AI not available - showing basic recommendations"
            }
        
        try:
            prompt = f"""As a senior Chartered Accountant (CA), provide professional financial and tax-saving recommendations.

Context: {context}
Financial Data: {json.dumps(financial_data, indent=2)}

Please provide:
1. Top 5 actionable tax-saving recommendations
2. Cash flow optimization strategies
3. Compliance risk areas to monitor
4. Strategic financial planning suggestions

Format your response as a professional CA advisory report suitable for client presentation."""

            response = self.gemini_client.generate_content(prompt)
            
            return {
                "status": "success",
                "recommendations": response.text.strip(),
                "timestamp": self._get_timestamp(),
                "context_analyzed": bool(context or financial_data)
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"AI recommendation generation failed: {str(e)}",
                "fallback_recommendations": [
                    "Consider accelerating receivables",
                    "Optimize input tax credit utilization",
                    "Review tax deduction opportunities"
                ]
            }

    def _forecast(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate AI-powered business forecast with professional CA insights
        """
        horizon = params.get("horizon", 30)  # days
        historical_data = params.get("historical_data", {})
        business_context = params.get("business_context", "")
        
        if not self.gemini_client:
            return {
                "status": "success",
                "forecast": {
                    "horizon_days": horizon,
                    "projected_cash": 12000,
                    "confidence": "low - AI not available"
                }
            }
        
        try:
            prompt = f"""As a Chartered Accountant with expertise in financial forecasting, analyze the following data and provide a professional forecast.

Forecast Horizon: {horizon} days
Historical Data: {json.dumps(historical_data, indent=2)}
Business Context: {business_context}

Provide:
1. Cash flow forecast for the period
2. Revenue projections with assumptions
3. Expected GST liability estimates
4. Key risk factors and sensitivities
5. Recommendations for financial planning

Present findings in a format suitable for board presentations and stakeholder reports."""

            response = self.gemini_client.generate_content(prompt)
            
            return {
                "status": "success",
                "forecast": {
                    "horizon_days": horizon,
                    "analysis": response.text.strip(),
                    "generated_at": self._get_timestamp(),
                    "confidence": "high - AI-powered analysis"
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Forecast generation failed: {str(e)}"
            }

    def _analyze_financials(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive financial analysis with CA-level insights
        """
        financial_statements = params.get("financial_statements", {})
        industry = params.get("industry", "general")
        
        if not self.gemini_client:
            return {
                "status": "error",
                "message": "Gemini AI required for comprehensive financial analysis"
            }
        
        try:
            prompt = f"""As a Chartered Accountant conducting a financial analysis, review the following financial statements:

Industry: {industry}
Financial Statements: {json.dumps(financial_statements, indent=2)}

Provide comprehensive analysis covering:
1. Liquidity ratios and working capital analysis
2. Profitability metrics and trends
3. Leverage and solvency assessment
4. Efficiency ratios (inventory turnover, receivables days, etc.)
5. Industry benchmarking insights
6. Red flags or areas of concern
7. Strategic recommendations for improvement

Present as a professional CA report with actionable insights."""

            response = self.gemini_client.generate_content(prompt)
            
            return {
                "status": "success",
                "financial_analysis": response.text.strip(),
                "industry": industry,
                "analyzed_at": self._get_timestamp()
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Financial analysis failed: {str(e)}"
            }

    def _tax_planning(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Strategic tax planning recommendations for businesses
        """
        business_type = params.get("business_type", "")
        annual_income = params.get("annual_income", 0)
        current_tax_regime = params.get("current_tax_regime", "")
        
        if not self.gemini_client:
            return {
                "status": "error",
                "message": "Gemini AI required for tax planning analysis"
            }
        
        try:
            prompt = f"""As a tax specialist Chartered Accountant, provide strategic tax planning advice:

Business Type: {business_type}
Annual Income: ₹{annual_income:,.2f}
Current Tax Regime: {current_tax_regime}

Provide:
1. Optimal tax structure recommendations
2. Deductions and exemptions analysis (Section 80C, 80D, 80G, etc.)
3. GST optimization strategies
4. Investment planning for tax efficiency
5. Timing strategies for income and expenses
6. Corporate tax vs personal tax considerations
7. Compliance calendar and key deadlines

Format as a professional tax advisory suitable for client consultation."""

            response = self.gemini_client.generate_content(prompt)
            
            return {
                "status": "success",
                "tax_planning": response.text.strip(),
                "business_type": business_type,
                "prepared_at": self._get_timestamp()
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Tax planning analysis failed: {str(e)}"
            }

    def _get_timestamp(self) -> str:
        """Return current timestamp in ISO format"""
        from datetime import datetime
        return datetime.utcnow().isoformat() + "Z"

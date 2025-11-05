from .memory import MemoryModule
from .planning import PlanningAndReasoningEngine
from typing import Dict, Any, List

class CoreAIAgent:
    def __init__(self, available_tools):
        self.available_tools = available_tools


    def process_request(self, user_input):
        """
        Very basic command parser for MVP.
        """
        user_input = user_input.lower()
        plan = []

        if user_input.startswith("audit document"):
            plan.append({
                "tool": "DocAuditAgent",
                "action": "audit_document"
            })
        elif user_input.startswith("send reminder"):
            plan.append({
                "tool": "ClientCommAgent",
                "action": "send_reminder"
            })
        # Add more command patterns as needed
        elif user_input.startswith("bookbotagent categorize"):
            plan.append({
                "tool": "BookBotAgent",
                "action": "categorize"
            })
        elif user_input.startswith("bookbotagent pnl"):
            plan.append({
                "tool": "BookBotAgent",
                "action": "pnl"
            })
        elif user_input.startswith("bookbotagent journalize"):
            plan.append({
                "tool": "BookBotAgent",
                "action": "journalize"
            })
        elif user_input.startswith("compliance run_checks"):
            plan.append({
                "tool": "ComplianceCheckAgent",
                "action": "run_checks"
            })
        elif user_input.startswith("gstagent anomalies"):
            plan.append({
                "tool": "GSTAgent",
                "action": "detect_anomalies"
            })
        elif user_input.startswith("gstagent query"):
            plan.append({
                "tool": "GSTAgent",
                "action": "query"
            })
        elif user_input.startswith("gstagent summarize"):
            plan.append({
                "tool": "GSTAgent",
                "action": "summarize"
            })
        elif user_input.startswith("insight summarize_period"):
            plan.append({"tool": "InsightBotAgent", "action": "summarize_period"})
        elif user_input.startswith("insight top_customers"):
            plan.append({"tool": "InsightBotAgent", "action": "top_customers"})
        elif user_input.startswith("insight anomaly_scan"):
            plan.append({"tool": "InsightBotAgent", "action": "anomaly_scan"})
        elif user_input.startswith("insight ai_summary"):
            plan.append({"tool": "InsightBotAgent", "action": "ai_summary"})
        elif user_input.startswith("insight ai_explain_anomalies"):
            plan.append({"tool": "InsightBotAgent", "action": "ai_explain_anomalies"})
        elif user_input.startswith("insight ai_forecast"):
            plan.append({"tool": "InsightBotAgent", "action": "ai_forecast"})
        elif user_input.startswith("insight ai_query"):
            plan.append({"tool": "InsightBotAgent", "action": "ai_query"})
        elif user_input.startswith("taxbot extract"):
            plan.append({"tool": "TaxBot", "action": "extract"})
        elif user_input.startswith("taxbot calculate"):
            plan.append({"tool": "TaxBot", "action": "calculate"})
        elif user_input.startswith("taxbot autofill"):
            plan.append({"tool": "TaxBot", "action": "autofill"})
        elif user_input.startswith("taxbot remind"):
            plan.append({"tool": "TaxBot", "action": "remind"})
        elif user_input.startswith("taxbot ai-summarize"):
            plan.append({"tool": "TaxBot", "action": "ai-summarize"})
        elif user_input.startswith("taxbot ai-categorize"):
            plan.append({"tool": "TaxBot", "action": "ai-categorize"})
        elif user_input.startswith("taxbot ai-check-deductions"):
            plan.append({"tool": "TaxBot", "action": "ai-check-deductions"})
        elif user_input.startswith("recon match"):
            plan.append({"tool": "ReconAgent", "action": "match_payments"})
        elif user_input.startswith("recon summarize"):
            plan.append({"tool": "ReconAgent", "action": "summarize_discrepancies"})
        elif user_input.startswith("treasury forecast"):
            plan.append({"tool": "TreasuryAgent", "action": "forecast_cash"})
        elif user_input.startswith("treasury whatif"):
            plan.append({"tool": "TreasuryAgent", "action": "what_if"})
        elif user_input.startswith("collections prioritize"):
            plan.append({"tool": "CollectionsAgent", "action": "prioritize_accounts"})
        elif user_input.startswith("collections remind"):
            plan.append({"tool": "CollectionsAgent", "action": "draft_reminder"})
        elif user_input.startswith("audit orchestrate"):
            plan.append({"tool": "AuditOrchestrator", "action": "orchestrate_audit"})
        elif user_input.startswith("tds calculate"):
            plan.append({"tool": "TDSAgent", "action": "calculate_tds"})
        elif user_input.startswith("advisory recommend"):
            plan.append({"tool": "AdvisoryBot", "action": "recommendations"})
        elif user_input.startswith("contract analyze"):
            plan.append({"tool": "ContractAgent", "action": "analyze_contract"})
        elif user_input.startswith("cashflow update"):
            plan.append({"tool": "CashFlowAgent", "action": "update_forecast"})
        elif user_input.startswith("matchmaking find"):
            plan.append({"tool": "MatchmakingAgent", "action": "find_expert"})

        return plan

# class CoreAIAgent:
#     """
#     The central AI agent that orchestrates the perception, core, and action layers.
#     """
#     def __init__(self, available_tools: List[str]):
#         """
#         Initializes the CoreAIAgent.
#         """
#         self.memory = MemoryModule()
#         self.planner = PlanningAndReasoningEngine(available_tools)
#         # In a real application, you would initialize your LLM here.
#         from transformers import AutoModelForCausalLM, AutoTokenizer
#         self.llm = AutoModelForCausalLM.from_pretrained("gpt2")
#         self.tokenizer = AutoTokenizer.from_pretrained("gpt2")

#     def process_request(self, user_query: str, document_path: str = None) -> Any:
#         """
#         Processes a user request from start to finish.

#         Args:
#             user_query (str): The query from the user.
#             document_path (str, optional): Path to an associated document. Defaults to None.

#         Returns:
#             Any: The result of the executed plan.
#         """
#         # 1. Perception
#         # (Assuming NLU and Document Processing are done before calling this)
#         self.memory.add_to_short_term({"role": "user", "content": user_query})

#         # 2. Agent Core (Planning)
#         context = self.memory.get_short_term_context()
#         plan = self.planner.create_plan(user_query, context)

#         # 3. Action (Execution)
#         # The execution of the plan would happen in the main application loop,
#         # which would call the appropriate tools.
#         # For this example, we'll just return the plan.
#         return plan
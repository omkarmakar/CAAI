"""
Comprehensive test script for Gemini-integrated agents.
Tests all AI-powered CA agents to ensure they work correctly for professional use.
"""
import sys
import os
import json
from pathlib import Path

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from agents.advisory_bot import AdvisoryBot
from agents.audit_orchestrator import AuditOrchestrator
from agents.cashflow_agent import CashFlowAgent
from agents.collections_agent import CollectionsAgent
from agents.contract_agent import ContractAgent
from agents.matchmaking_agent import MatchmakingAgent
from agents.recon_agent import ReconAgent
from agents.treasury_agent import TreasuryAgent
import config

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}")
    print(f"{text:^80}")
    print(f"{'='*80}{Colors.ENDC}\n")

def print_success(text):
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")

def print_error(text):
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")

def print_info(text):
    print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")

def print_result(result):
    """Pretty print agent result"""
    if isinstance(result, dict):
        print(json.dumps(result, indent=2, default=str)[:500])  # Limit output
    else:
        print(str(result)[:500])

def test_advisory_bot():
    """Test AdvisoryBot with Gemini integration"""
    print_header("Testing AdvisoryBot")
    
    try:
        gemini_key = config.GEMINI_API_KEY
        agent = AdvisoryBot(gemini_api_key=gemini_key)
        
        # Test 1: Recommendations
        print_info("Test 1: AI Tax & Financial Recommendations")
        result = agent.execute({
            "action": "recommendations",
            "params": {
                "context": "Small manufacturing business, annual turnover 2 Cr",
                "financial_data": {"revenue": 20000000, "expenses": 15000000}
            }
        })
        print_result(result)
        if result.get("status") == "success":
            print_success("Recommendations test passed")
        else:
            print_error(f"Recommendations test failed: {result.get('message')}")
        
        # Test 2: Forecast
        print_info("\nTest 2: AI Business Forecast")
        result = agent.execute({
            "action": "forecast",
            "params": {
                "horizon": 90,
                "business_context": "Seasonal business with Q4 peak"
            }
        })
        print_result(result)
        if result.get("status") == "success":
            print_success("Forecast test passed")
        else:
            print_error(f"Forecast test failed: {result.get('message')}")
        
        print_success("\n✅ AdvisoryBot: All tests completed\n")
        return True
        
    except Exception as e:
        print_error(f"AdvisoryBot test failed with exception: {str(e)}")
        return False

def test_audit_orchestrator():
    """Test AuditOrchestrator with Gemini integration"""
    print_header("Testing AuditOrchestrator")
    
    try:
        gemini_key = config.GEMINI_API_KEY
        agent = AuditOrchestrator(gemini_api_key=gemini_key)
        
        # Test: Risk Assessment
        print_info("Test: AI Audit Risk Assessment")
        result = agent.execute({
            "action": "risk_assessment",
            "params": {
                "financial_data": {
                    "revenue": 50000000,
                    "high_value_transactions": 15,
                    "related_party_transactions": 3
                },
                "industry": "Manufacturing"
            }
        })
        print_result(result)
        if result.get("status") == "success":
            print_success("Risk assessment test passed")
        else:
            print_error(f"Risk assessment test failed: {result.get('message')}")
        
        print_success("\n✅ AuditOrchestrator: All tests completed\n")
        return True
        
    except Exception as e:
        print_error(f"AuditOrchestrator test failed with exception: {str(e)}")
        return False

def test_cashflow_agent():
    """Test CashFlowAgent with Gemini integration"""
    print_header("Testing CashFlowAgent")
    
    try:
        gemini_key = config.GEMINI_API_KEY
        agent = CashFlowAgent(gemini_api_key=gemini_key)
        
        # Test: Cash Forecast
        print_info("Test: AI Cash Flow Forecast")
        result = agent.execute({
            "action": "update_forecast",
            "params": {
                "forecast_period": 30,
                "historical_data": [
                    {"date": "2024-01", "inflow": 500000, "outflow": 450000},
                    {"date": "2024-02", "inflow": 520000, "outflow": 470000}
                ]
            }
        })
        print_result(result)
        if result.get("status") == "success":
            print_success("Cash forecast test passed")
        else:
            print_error(f"Cash forecast test failed: {result.get('message')}")
        
        print_success("\n✅ CashFlowAgent: All tests completed\n")
        return True
        
    except Exception as e:
        print_error(f"CashFlowAgent test failed with exception: {str(e)}")
        return False

def test_collections_agent():
    """Test CollectionsAgent with Gemini integration"""
    print_header("Testing CollectionsAgent")
    
    try:
        gemini_key = config.GEMINI_API_KEY
        agent = CollectionsAgent(gemini_api_key=gemini_key)
        
        # Test 1: Prioritize Accounts
        print_info("Test 1: AI Account Prioritization")
        result = agent.execute({
            "action": "prioritize_accounts",
            "params": {
                "accounts": [
                    {"customer": "ABC Corp", "outstanding": 250000, "days_overdue": 45},
                    {"customer": "XYZ Ltd", "outstanding": 150000, "days_overdue": 90},
                    {"customer": "PQR Inc", "outstanding": 100000, "days_overdue": 15}
                ]
            }
        })
        print_result(result)
        if result.get("status") == "success":
            print_success("Account prioritization test passed")
        else:
            print_error(f"Account prioritization test failed: {result.get('message')}")
        
        # Test 2: Draft Reminder
        print_info("\nTest 2: AI Draft Collection Reminder")
        result = agent.execute({
            "action": "draft_reminder",
            "params": {
                "recipient": "abc@example.com",
                "recipient_name": "ABC Corporation",
                "amount": 250000,
                "invoice_no": "INV-2024-001",
                "due_date": "2024-01-15",
                "days_overdue": 45,
                "tone": "firm"
            }
        })
        print_result(result)
        if result.get("status") == "success":
            print_success("Reminder drafting test passed")
        else:
            print_error(f"Reminder drafting test failed: {result.get('message')}")
        
        print_success("\n✅ CollectionsAgent: All tests completed\n")
        return True
        
    except Exception as e:
        print_error(f"CollectionsAgent test failed with exception: {str(e)}")
        return False

def test_contract_agent():
    """Test ContractAgent with Gemini integration"""
    print_header("Testing ContractAgent")
    
    try:
        gemini_key = config.GEMINI_API_KEY
        agent = ContractAgent(gemini_api_key=gemini_key)
        
        # Create a sample contract file for testing
        test_contract_path = "test_contract.txt"
        with open(test_contract_path, "w", encoding="utf-8") as f:
            f.write("""
SERVICE AGREEMENT

This Service Agreement ("Agreement") is entered into on January 1, 2024.

PARTIES:
1. Service Provider: XYZ Consulting Pvt Ltd
2. Client: ABC Manufacturing Ltd

SCOPE OF SERVICES:
The Service Provider shall provide consulting services for a period of 12 months.

PAYMENT TERMS:
- Monthly retainer: Rs. 1,00,000/-
- Payment due within 30 days of invoice
- Late payment penalty: 2% per month

TERMINATION:
Either party may terminate with 30 days written notice.

GST:
All amounts exclusive of GST at applicable rates.
            """)
        
        print_info("Test: AI Contract Analysis")
        result = agent.execute({
            "action": "analyze_contract",
            "params": {
                "contract_path": test_contract_path,
                "contract_type": "service agreement"
            }
        })
        print_result(result)
        
        # Cleanup
        if os.path.exists(test_contract_path):
            os.remove(test_contract_path)
        
        if result.get("status") == "success":
            print_success("Contract analysis test passed")
        else:
            print_error(f"Contract analysis test failed: {result.get('message')}")
        
        print_success("\n✅ ContractAgent: All tests completed\n")
        return True
        
    except Exception as e:
        print_error(f"ContractAgent test failed with exception: {str(e)}")
        # Cleanup on error
        if os.path.exists("test_contract.txt"):
            os.remove("test_contract.txt")
        return False

def test_matchmaking_agent():
    """Test MatchmakingAgent with Gemini integration"""
    print_header("Testing MatchmakingAgent")
    
    try:
        gemini_key = config.GEMINI_API_KEY
        agent = MatchmakingAgent(gemini_api_key=gemini_key)
        
        # Test: Find Expert
        print_info("Test: AI Expert Matching")
        result = agent.execute({
            "action": "find_expert",
            "params": {
                "topic": "GST Audit",
                "query": "Need help with GST audit for manufacturing unit with interstate transactions",
                "client_profile": {
                    "business_type": "Manufacturing",
                    "turnover": 50000000,
                    "complexity": "moderate"
                }
            }
        })
        print_result(result)
        if result.get("status") == "success":
            print_success("Expert matching test passed")
        else:
            print_error(f"Expert matching test failed: {result.get('message')}")
        
        print_success("\n✅ MatchmakingAgent: All tests completed\n")
        return True
        
    except Exception as e:
        print_error(f"MatchmakingAgent test failed with exception: {str(e)}")
        return False

def test_recon_agent():
    """Test ReconAgent with Gemini integration"""
    print_header("Testing ReconAgent")
    
    try:
        gemini_key = config.GEMINI_API_KEY
        agent = ReconAgent(gemini_api_key=gemini_key)
        
        # Test: Explain Discrepancies
        print_info("Test: AI Explain Discrepancies")
        result = agent.execute({
            "action": "explain_discrepancies",
            "params": {
                "discrepancies": [
                    {"type": "amount_mismatch", "invoice": "INV-001", "expected": 10000, "found": 9500},
                    {"type": "missing_entry", "invoice": "INV-002", "amount": 5000},
                    {"type": "timing_difference", "invoice": "INV-003", "days_delay": 5}
                ],
                "context": "Monthly bank reconciliation for January 2024"
            }
        })
        print_result(result)
        if result.get("status") == "success":
            print_success("Discrepancy explanation test passed")
        else:
            print_error(f"Discrepancy explanation test failed: {result.get('message')}")
        
        print_success("\n✅ ReconAgent: All tests completed\n")
        return True
        
    except Exception as e:
        print_error(f"ReconAgent test failed with exception: {str(e)}")
        return False

def test_treasury_agent():
    """Test TreasuryAgent with Gemini integration"""
    print_header("Testing TreasuryAgent")
    
    try:
        gemini_key = config.GEMINI_API_KEY
        agent = TreasuryAgent(gemini_api_key=gemini_key)
        
        # Test 1: Cash Forecast
        print_info("Test 1: AI Treasury Forecast")
        result = agent.execute({
            "action": "forecast_cash",
            "params": {
                "days": 30,
                "historical_data": [
                    {"date": "2024-01", "opening": 1000000, "inflows": 500000, "outflows": 450000},
                    {"date": "2024-02", "opening": 1050000, "inflows": 520000, "outflows": 480000}
                ],
                "assumptions": {
                    "growth_rate": 0.05,
                    "collection_efficiency": 0.90
                }
            }
        })
        print_result(result)
        if result.get("status") == "success":
            print_success("Treasury forecast test passed")
        else:
            print_error(f"Treasury forecast test failed: {result.get('message')}")
        
        # Test 2: What-If Analysis
        print_info("\nTest 2: What-If Scenario Analysis")
        result = agent.execute({
            "action": "what_if",
            "params": {
                "scenario": "Major customer payment delay",
                "base_case": {"expected_collections": 500000},
                "variables": {"collection_delay": 30, "amount_affected": 200000}
            }
        })
        print_result(result)
        if result.get("status") == "success":
            print_success("What-if analysis test passed")
        else:
            print_error(f"What-if analysis test failed: {result.get('message')}")
        
        print_success("\n✅ TreasuryAgent: All tests completed\n")
        return True
        
    except Exception as e:
        print_error(f"TreasuryAgent test failed with exception: {str(e)}")
        return False

def main():
    """Run all tests"""
    print_header("GEMINI-INTEGRATED AGENTS COMPREHENSIVE TEST SUITE")
    print_info("Testing all AI-powered CA agents for professional use")
    
    # Check if Gemini API key is configured
    if not config.GEMINI_API_KEY:
        print_error("⚠️  GEMINI_API_KEY not configured in config!")
        print_info("Please set GEMINI_API_KEY in your .env file or config.py")
        return
    else:
        print_success(f"✓ Gemini API Key configured: {config.GEMINI_API_KEY[:20]}...")
    
    results = {}
    
    # Run all tests
    results["AdvisoryBot"] = test_advisory_bot()
    results["AuditOrchestrator"] = test_audit_orchestrator()
    results["CashFlowAgent"] = test_cashflow_agent()
    results["CollectionsAgent"] = test_collections_agent()
    results["ContractAgent"] = test_contract_agent()
    results["MatchmakingAgent"] = test_matchmaking_agent()
    results["ReconAgent"] = test_recon_agent()
    results["TreasuryAgent"] = test_treasury_agent()
    
    # Summary
    print_header("TEST SUMMARY")
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for agent_name, passed_test in results.items():
        if passed_test:
            print_success(f"{agent_name}: PASSED")
        else:
            print_error(f"{agent_name}: FAILED")
    
    print(f"\n{Colors.BOLD}Results: {passed}/{total} agents passed{Colors.ENDC}")
    
    if passed == total:
        print_success("\n🎉 All tests passed! Agents are ready for professional CA use.")
    else:
        print_error(f"\n⚠️  {total - passed} agent(s) failed. Please review errors above.")

if __name__ == "__main__":
    main()

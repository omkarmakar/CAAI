import shlex
import os
import json
from fastapi import FastAPI, Request, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from perception.nlu import NaturalLanguageUnderstanding
from perception.data_processing import DocumentProcessor
from agent_core.agent import CoreAIAgent
from action.human_in_the_loop import HumanInTheLoop
from agents.doc_audit_agent import DocAuditAgent
from agents.client_comm_agent import ClientCommAgent
from agents.gst_agent import GSTAgent, OrgInfo
from agents.insight_bot_agent import InsightBotAgent
from agents.tax_bot_agent import TaxBot
from agents.compliance_check_agent import ComplianceCheckAgent
from agents.book_bot_agent import BookBotAgent
from pathlib import Path


try:
    # When running as a package module (e.g., `uvicorn backend.main:app`)
    from . import config  # type: ignore
except Exception:
    # When running as a script from backend/ (e.g., `python main.py`)
    import config  # type: ignore

# --- Import all agent files dynamically ---
import importlib
import pkgutil


def get_all_agents():
    agents = {}
    # Prefer environment-provided key; fall back to empty string if not set.
    gemini_api_key = config.GEMINI_API_KEY or ""
    doc_processor = DocumentProcessor()
    agent_pkg = "agents"

    for _, modname, _ in pkgutil.iter_modules([os.path.join(os.path.dirname(__file__), "agents")]):
        module = importlib.import_module(f"{agent_pkg}.{modname}")
        for attr in dir(module):
            if attr.endswith("Agent") and attr != "CoreAIAgent":
                agent_cls = getattr(module, attr)

                if attr == "DocAuditAgent":
                    agents[attr] = agent_cls(doc_processor, gemini_api_key)
                elif attr == "ClientCommAgent":
                    agents[attr] = agent_cls(gemini_api_key)
                elif attr == "BookBotAgent":
                    agents[attr] = agent_cls(gemini_api_key)
                elif attr == "ComplianceCheckAgent":
                    agents[attr] = agent_cls(gemini_api_key)
                elif attr == "InsightBotAgent":
                    agents[attr] = agent_cls(gemini_api_key=gemini_api_key)
                elif attr == "GSTAgent":
                    # Hardcode or load org config
                    org = OrgInfo("DemoOrg", "29ABCDE1234F2Z5", "29", "monthly")
                    agents[attr] = agent_cls(org, Path("./output"), gemini_api_key=gemini_api_key)
                elif attr == "TaxBot":
                    agents[attr] = agent_cls(
                        out_dir=Path("./output/taxbot"),
                        gemini_api_key=gemini_api_key
                    )

                else:
                    try:
                        agents[attr] = agent_cls()
                    except Exception:
                        pass
    return agents


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Agent initialization (reuse for CLI and API) ---
doc_processor = DocumentProcessor()
available_agents = get_all_agents()
core_agent = CoreAIAgent(available_tools=list(available_agents.keys()))


def process_command(user_input: str):
    command_parts = shlex.split(user_input)
    plan = core_agent.process_request(user_input)
    if not plan:
        return {"error": "Could not determine an action plan for your command."}

    results = []
    for step in plan:
        tool_name = step.get("tool")
        agent = available_agents.get(tool_name)
        if not agent:
            results.append({"error": f"Agent '{tool_name}' is not available."})
            continue

        params = {}
        if tool_name == "DocAuditAgent" and len(command_parts) > 2:
            params['document_path'] = command_parts[2]
        elif tool_name == "ClientCommAgent" and len(command_parts) > 2:
            params['recipient_email'] = command_parts[2]
        elif tool_name == "BookBotAgent" and len(command_parts) > 2:
            params['ledger'] = command_parts[2]
            if len(command_parts) > 3 and command_parts[3].startswith("kind="):
                params['kind'] = command_parts[3].split("=")[1]
        elif tool_name == "GSTAgent" and len(command_parts) > 2:
            if step.get("action") == "detect_anomalies":
                params["ledger"] = command_parts[2]
            elif step.get("action") == "query":
                params["ledger"] = command_parts[2]
                params["query"] = " ".join(command_parts[3:])
            elif step.get("action") == "summarize":
                params["context"] = command_parts[2]
                params["data"] = json.loads(command_parts[3]) if len(command_parts) > 3 else {}
        elif tool_name == "ComplianceCheckAgent":
            for arg in command_parts[2:]:
                if arg.startswith("sales="):
                    params["sales"] = arg.split("=", 1)[1]
                elif arg.startswith("purchases="):
                    params["purchases"] = arg.split("=", 1)[1]
                elif arg.startswith("period="):
                    params["period"] = arg.split("=", 1)[1]
        elif tool_name == "TaxBot":
            if step.get("action") == "extract":
                params["files"] = command_parts[2:]
            elif step.get("action") == "calculate":
                params["incomes"] = command_parts[2]
                if "--deductions" in command_parts:
                    idx = command_parts.index("--deductions")
                    params["deductions"] = command_parts[idx + 1]
                if "--rebate" in command_parts:
                    idx = command_parts.index("--rebate")
                    params["rebate"] = float(command_parts[idx + 1])
            elif step.get("action") == "autofill":
                params["template"] = command_parts[2]
                params["person"] = command_parts[4]
                params["incomes"] = command_parts[6]
                if "--deductions" in command_parts:
                    idx = command_parts.index("--deductions")
                    params["deductions"] = command_parts[idx + 1]
                params["out"] = command_parts[-1]
            elif step.get("action") == "remind":
                params["date"] = command_parts[2]
                params["message"] = " ".join(command_parts[3:])
            elif step.get("action") in ["ai-summarize", "ai-categorize"]:
                params["text"] = Path(command_parts[2]).read_text(encoding="utf-8")
            elif step.get("action") == "ai-check-deductions":
                params["incomes"] = json.loads(Path(command_parts[2]).read_text(encoding="utf-8")).get(
                    "incomes", [])
                params["deductions"] = json.loads(Path(command_parts[3]).read_text(encoding="utf-8")).get(
                    "deductions", [])
        elif tool_name == "InsightBotAgent":
            if step.get("action") in ["summarize_period", "ai_summary", "ai_forecast"]:
                params["sales"] = command_parts[2]
                params["purchases"] = command_parts[4] if len(command_parts) > 4 else None
            elif step.get("action") in ["top_customers"]:
                params["sales"] = command_parts[2]
                params["top_n"] = int(command_parts[4]) if len(command_parts) > 4 else 10
            elif step.get("action") in ["anomaly_scan", "ai_explain_anomalies"]:
                params["sales"] = command_parts[2]
            elif step.get("action") == "ai_query":
                params["sales"] = command_parts[2]
                params["query"] = " ".join(command_parts[3:])

        task = {"action": step.get("action"), "params": params}
        try:
            result = agent.execute(task)
            results.append(result)
        except Exception as e:
            results.append({"error": str(e)})
    return {"plan": plan, "results": results}


@app.post("/agent")
async def agent_endpoint(request: Request):
    data = await request.json()
    user_input = data.get("command", "")
    response = process_command(user_input)
    return response


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    upload_dir = "uploaded_files"
    os.makedirs(upload_dir, exist_ok=True)
    if not file.filename:
        return {"error": "No filename provided"}
    file_location = os.path.join(upload_dir, file.filename)
    with open(file_location, "wb") as f:
        f.write(await file.read())
    # Return relative path for backend usage
    return {"path": file_location}


def main():
    """
    Main function to run the AI Agent (Phase 1 MVP).
    """
    print("Initializing AI Agent components...")
    doc_processor = DocumentProcessor()

    available_agents = get_all_agents()
    core_agent = CoreAIAgent(available_tools=list(available_agents.keys()))

    print("\n--- AI Agent for CA Firm ---")
    print("Available Agents: " + ", ".join(available_agents.keys()))
    print("Example Commands:")
    if "DocAuditAgent" in available_agents:
        print("  audit document \"/path/to/your/invoice.pdf\"")
    if "ClientCommAgent" in available_agents:
        print("  send reminder client_abc@example.com")
    if "BookBotAgent" in available_agents:
        print("  bookbotagent categorize ./path/to/ledger.csv")
        print("  bookbotagent pnl ./path/to/ledger.csv")
        print("  bookbotagent journalize ./path/to/ledger.csv kind=sales")
    if "ComplianceCheckAgent" in available_agents:
        print("  compliance run_checks sales=./sales.csv purchases=./purchases.csv period=2025-07")
    if "GSTAgent" in available_agents:
        print("  gstagent anomalies --ledger ./path/to/sales")
        print("  gstagent query ./path/to/sales 'high value invoices above 5L'")
        print("  gstagent summarize --context 'Monthly filing' --data '{...}'")
    if "InsightBotAgent" in available_agents:
        print("  insight summarize_period --sales ./sales.csv --purchases ./purchases.csv")
        print("  insight top_customers --sales ./sales.csv --top_n 5")
        print("  insight anomaly_scan --sales ./sales.csv")
        print("  insight ai_summary --sales ./sales.csv --purchases ./purchases.csv")
        print("  insight ai_explain_anomalies --sales ./sales.csv")
        print("  insight ai_forecast --sales ./sales.csv --purchases ./purchases.csv")
        print("  insight ai_query --sales ./sales.csv 'show invoices above 5 lakh'")
    if "TaxBot" in available_agents:
        print("  taxbot extract --files ./salary.pdf ./interest.pdf")
        print(
            "  taxbot calculate --incomes ./taxbot_output/extracted.json --deductions ./deductions.json --rebate 12500")
        print(
            "  taxbot autofill --template ./template.json --person ./person.json --incomes ./incomes.json --deductions ./deductions.json --out ./filled.json")
        print("  taxbot remind --date 2025-07-31 --message 'File your returns!'")
        print("  taxbot ai-summarize --file ./salary.pdf")
        print("  taxbot ai-categorize --file ./salary.pdf")
        print("  taxbot ai-check-deductions --incomes ./incomes.json --deductions ./deductions.json")

    # for agent_name in available_agents:
    #     if agent_name not in ["DocAuditAgent", "ClientCommAgent", "BookBotAgent"]:
    #         print(f"  {agent_name.lower()} <your_parameters_here>")
    # print("Enter your command (or 'exit' to quit):")

    while True:
        try:
            user_input = input("> ")
            if user_input.lower() in ['exit', 'quit']:
                print("Exiting agent. Goodbye!")
                break
            if not user_input.strip():
                continue
            response = process_command(user_input)
            print(f"Generated Plan: {response.get('plan')}")
            if "error" in response:
                print(f"Error: {response['error']}")
                continue
            for result in response.get("results", []):
                print("\n--- Execution Result ---")
                if isinstance(result, dict):
                    for key, value in result.items():
                        print(f"{key.replace('_', ' ').capitalize()}: {value}")
                else:
                    print(result)
                print("------------------------\n")
        except (KeyboardInterrupt, EOFError):
            print("\nExiting agent. Goodbye!")
            break
        except Exception as e:
            print(f"\nAn unexpected error occurred: {e}\nPlease try again.\n")


if __name__ == "__main__":
    for dir_name in ["perception", "agent_core", "action", "agents"]:
        os.makedirs(dir_name, exist_ok=True)
        with open(os.path.join(dir_name, "__init__.py"), "w") as f:
            pass
    # Run FastAPI server
    # Use config-driven host/port if provided
    uvicorn.run(app, host=config.UVICORN_HOST, port=config.UVICORN_PORT)
    # Optionally, keep CLI for local testing
    # main()

# To run the backend, use the following command in your terminal:
# (Make sure you are in the backend folder and have all dependencies installed.)

# If you have Python and uvicorn installed:
# > uvicorn main:app --host 0.0.0.0 --port 8000

# Or, simply run:
# > python main.py

# This will start the FastAPI server on http://localhost:8000
# Make sure your backend is running before using the frontend.
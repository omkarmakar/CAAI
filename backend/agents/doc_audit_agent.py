from agents.base_agent import BaseAgent
from perception.data_processing import DocumentProcessor
from typing import Dict, Any
import os
import google.generativeai as genai


class DocAuditAgent(BaseAgent):
    """
    Agent for document processing and auditing using Google Gemini LLM.
    """
    def __init__(self, doc_processor: DocumentProcessor, gemini_api_key: str):
        """
        Initializes the DocAuditAgent.

        Args:
            doc_processor (DocumentProcessor): Instance of DocumentProcessor to process documents.
            gemini_api_key (str): Your Google Gemini API key.
        """
        super().__init__("DocAuditAgent")
        self.doc_processor = doc_processor

        # Configure Gemini API
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel("gemini-2.0-flash")
    
    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes a document auditing task.

        Args:
            task (Dict[str, Any]): The task dictionary containing the action and parameters.

        Returns:
            Dict[str, Any]: The result of the audit.
        """
        action = task.get("action")
        params = task.get("params", {})

        if action == "audit_document":
            return self._audit_document(params)
        else:
            return {"status": "error", "message": f"Unknown action '{action}' for DocAuditAgent"}

    def _audit_document(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processes and audits a given document using Gemini LLM.

        Args:
            params (Dict[str, Any]): Parameters for the audit, must include 'document_path'.

        Returns:
            Dict[str, Any]: A dictionary containing the audit findings.
        """
        document_path = params.get("document_path")
        if not document_path or not os.path.exists(document_path):
            return {"status": "error", "message": f"Document not found at path: {document_path}"}

        print(f"Auditing document with Gemini: {document_path}")

        try:
            # Step 1: Process the document to extract text
            processed_doc = self.doc_processor.process_document(document_path)
            content = processed_doc.get("content", "").strip()

            if not content:
                return {"status": "error", "message": "No text extracted from the document."}

            # Step 2: Let Gemini LLM audit the content
            prompt = (
                "You are an AI document auditor. Analyze the following document text and "
                "provide a list of key findings, including potential risks, compliance issues, "
                "or useful categorization. Keep responses concise and factual.\n\n"
                f"Document content:\n{content}\n\n"
                "Output your findings as a bullet list."
            )

            response = self.model.generate_content(prompt)
            findings_text = response.text.strip()
            findings_list = [line.strip("-• ").strip() for line in findings_text.split("\n") if line.strip()]

            return {
                "status": "success",
                "document_path": document_path,
                "findings": findings_list if findings_list else ["No issues found."]
            }

        except Exception as e:
            return {"status": "error", "message": f"An error occurred during document audit: {e}"}

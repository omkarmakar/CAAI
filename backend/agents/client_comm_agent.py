from .base_agent import BaseAgent
from typing import Dict, Any
import re
import google.generativeai as genai
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class ClientCommAgent(BaseAgent):
    """
    Agent for client communication tasks.
    """
    def __init__(self, gemini_api_key: str = None):
        super().__init__("ClientCommAgent")
        self.gemini_api_key = gemini_api_key

    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes a client communication task.

        Args:
            task (Dict[str, Any]): The task dictionary.

        Returns:
            Dict[str, Any]: The result of the communication task.
        """
        action = task.get("action")
        params = task.get("params", {})

        if action == "send_reminder":
            return self._send_reminder(params)
        else:
            return {"status": "error", "message": f"Unknown action '{action}' for ClientCommAgent"}

    def _send_reminder(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Uses Gemini API to generate subject/body and sends an actual email.

        Args:
            params (Dict[str, Any]): Parameters, must include 'recipient_email'.

        Returns:
            Dict[str, Any]: Status of the email.
        """
        recipient_email = params.get("recipient_email")

        # Basic email validation
        if not recipient_email or not re.match(r"[^@]+@[^@]+\.[^@]+", recipient_email):
            return {"status": "error", "message": f"Invalid recipient email provided: {recipient_email}"}

        # Gemini API setup (use the key passed to the agent)
        if not self.gemini_api_key:
            return {"status": "error", "message": "Gemini API key not provided."}
        genai.configure(api_key=self.gemini_api_key)

        prompt = (
            "Write a polite email reminder to a client asking for pending document submission. "
            "Return the subject and body."
        )
        try:
            model = genai.GenerativeModel("gemini-2.0-flash")
            response = model.generate_content(prompt)
            content = response.text
            # Expecting: Subject: ...\nBody: ...
            subject_match = re.search(r"Subject:\s*(.*)", content)
            body_match = re.search(r"Body:\s*(.*)", content, re.DOTALL)
            subject = subject_match.group(1).strip() if subject_match else "Gentle Reminder"
            body = body_match.group(1).strip() if body_match else content.strip()
        except Exception as e:
            return {"status": "error", "message": f"Gemini API error: {str(e)}"}

        # Send email using SMTP (update with your SMTP details)
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        smtp_user = "omkarmakar.pe.ug@jadavpuruniversity.in"
        smtp_password = "xyyi nmar alhh hhob"

        msg = MIMEMultipart()
        msg["From"] = smtp_user
        msg["To"] = recipient_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        try:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.sendmail(smtp_user, recipient_email, msg.as_string())
        except Exception as e:
            return {"status": "error", "message": f"Email sending failed: {str(e)}"}

        return {"status": "success", "message": f"Reminder sent to {recipient_email}"}

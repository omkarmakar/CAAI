#!/usr/bin/env python3
"""
TaxBot Agent with optional Gemini integration.

Usage examples:
  python taxbot_gemini.py extract --files doc1.pdf doc2.pdf --out ./extracted.json
  python taxbot_gemini.py calculate --incomes ./extracted.json --out ./tax_summary.json
  python taxbot_gemini.py ai-summarize --file ./extracted.json --gemini-key YOUR_KEY
  python taxbot_gemini.py remind --date 2025-10-15 --message "Pay advance tax" --to alice@example.com --gemini-key YOUR_KEY

Notes:
 - To enable Gemini helpers, install google-generativeai and pass API key.
   pip install google-generativeai
 - Gemini models and naming may change; adjust model names as required.
"""

from __future__ import annotations
import argparse
import csv
import datetime as dt
import hashlib
import json
import math
import os
import re
import smtplib
import sys
from dataclasses import dataclass, asdict
from email.message import EmailMessage
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

# Optional heavy deps
try:
    import pandas as pd
except Exception:
    pd = None

try:
    import pdfplumber
except Exception:
    pdfplumber = None

try:
    from PIL import Image
    import pytesseract
except Exception:
    pytesseract = None

# Gemini client (optional)
try:
    import google.generativeai as genai  # pip install google-generativeai
except Exception:
    genai = None

from dateutil.parser import parse as dateparse

# ------------------------- Utilities -------------------------
ROUND2 = lambda x: float(f"{x:.2f}")

def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)

def parse_date_safe(x) -> Optional[dt.date]:
    try:
        return dateparse(str(x)).date()
    except Exception:
        return None

# ------------------------- Data Models -------------------------
@dataclass
class Person:
    name: str
    pan: Optional[str] = None
    dob: Optional[str] = None
    email: Optional[str] = None

@dataclass
class IncomeRecord:
    source: str
    amount: float
    date: Optional[dt.date] = None
    details: Optional[str] = None

@dataclass
class Deduction:
    section: str
    amount: float
    details: Optional[str] = None

@dataclass
class TaxSummary:
    gross_income: float
    total_deductions: float
    taxable_income: float
    tax_before_rebate: float
    rebate: float
    health_cess: float
    tax_payable: float
    effective_rate: float

# ------------------------- Extractors -------------------------
class Extractor:
    @staticmethod
    def from_pdf_text(path: Path) -> str:
        if pdfplumber is None:
            raise RuntimeError("pdfplumber missing - install with: pip install pdfplumber")
        text = []
        with pdfplumber.open(path) as pdf:
            for p in pdf.pages:
                text.append(p.extract_text() or "")
        return "\n".join(text)

    @staticmethod
    def from_image_ocr(path: Path) -> str:
        if pytesseract is None:
            raise RuntimeError("pytesseract missing - install with: pip install pytesseract pillow")
        img = Image.open(path)
        return pytesseract.image_to_string(img)

    @staticmethod
    def from_excel(path: Path):
        if pd is None:
            raise RuntimeError("pandas missing - install with: pip install pandas openpyxl")
        return pd.read_excel(path)

    @staticmethod
    def from_csv(path: Path):
        if pd is None:
            raise RuntimeError("pandas missing - install with: pip install pandas")
        return pd.read_csv(path)

# ------------------------- Heuristic parsers -------------------------
class HeuristicParser:
    PAN_RE = re.compile(r"[A-Z]{5}[0-9]{4}[A-Z]")
    AMT_RE = re.compile(r"(?:INR|Rs\.?|₹)?\s?([0-9,]+(?:\.[0-9]{1,2})?)")

    @staticmethod
    def extract_person_from_text(text: str) -> Person:
        name = None
        pan = None
        email = None
        dob = None
        m = HeuristicParser.PAN_RE.search(text)
        if m:
            pan = m.group(0)
        m2 = re.search(r"[\w.%-]+@[\w.-]+\.[A-Za-z]{2,}", text)
        if m2:
            email = m2.group(0)
        m3 = re.search(r"Name[:\s]+([A-Z][A-Za-z\s]{2,50})", text)
        if m3:
            name = m3.group(1).strip()
        m4 = re.search(r"DOB[:\s]+([0-9/\-]{6,10})", text)
        if m4:
            dob = m4.group(1)
        if not name:
            name = "Unknown"
        return Person(name=name, pan=pan, dob=dob, email=email)

    @staticmethod
    def extract_amounts(text: str) -> List[IncomeRecord]:
        records: List[IncomeRecord] = []
        for line in text.splitlines():
            if not line.strip():
                continue
            if ':' in line:
                left, right = line.split(':', 1)
                if any(k.lower() in left.lower() for k in ['salary','income','interest','rent','dividend','professional']):
                    m = HeuristicParser.AMT_RE.search(right)
                    if m:
                        try:
                            amt = float(m.group(1).replace(',', ''))
                            records.append(IncomeRecord(source=left.strip(), amount=amt, details=line.strip()))
                        except Exception:
                            continue
        if not records:
            for m in HeuristicParser.AMT_RE.finditer(text):
                try:
                    amt = float(m.group(1).replace(',', ''))
                    records.append(IncomeRecord(source='uncategorized', amount=amt))
                except Exception:
                    continue
        return records

# ------------------------- Tax Calculator -------------------------
class TaxCalculator:
    SLABS = [
        (250000, 0.0),
        (500000, 0.05),
        (1000000, 0.20),
        (float('inf'), 0.30),
    ]
    HEALTH_CESS_RATE = 0.04

    @staticmethod
    def compute_tax(gross_income: float, deductions: float = 0.0, rebate: float = 0.0) -> TaxSummary:
        taxable = max(gross_income - deductions, 0.0)
        remaining = taxable
        tax = 0.0
        lower = 0.0
        for limit, rate in TaxCalculator.SLABS:
            slab_amount = max(min(remaining, limit - lower), 0.0)
            tax += slab_amount * rate
            lower = limit
            remaining = max(taxable - lower, 0.0)
            if remaining <= 0:
                break
        tax_before_rebate = ROUND2(tax)
        applicable_rebate = min(rebate, tax_before_rebate)
        tax_after_rebate = tax_before_rebate - applicable_rebate
        health_cess = ROUND2(tax_after_rebate * TaxCalculator.HEALTH_CESS_RATE)
        total_payable = ROUND2(tax_after_rebate + health_cess)
        eff_rate = (total_payable / gross_income * 100.0) if gross_income > 0 else 0.0
        return TaxSummary(
            gross_income=ROUND2(gross_income),
            total_deductions=ROUND2(deductions),
            taxable_income=ROUND2(taxable),
            tax_before_rebate=tax_before_rebate,
            rebate=ROUND2(applicable_rebate),
            health_cess=health_cess,
            tax_payable=total_payable,
            effective_rate=ROUND2(eff_rate),
        )

# ------------------------- Autofill (Mock) -------------------------
class Autofiller:
    @staticmethod
    def fill_form_json(template: Dict, person: Person, incomes: List[IncomeRecord], deductions: List[Deduction], out_path: Path) -> Path:
        payload = {
            'person': asdict(person),
            'incomes': [asdict(i) for i in incomes],
            'deductions': [asdict(d) for d in deductions],
            'generated_at': dt.datetime.utcnow().isoformat()
        }
        ensure_dir(out_path.parent)
        out_path.write_text(json.dumps(payload, indent=2), encoding='utf-8')
        return out_path

# ------------------------- Reminders -------------------------
class ReminderScheduler:
    @staticmethod
    def send_email(smtp_cfg: Dict, to: str, subject: str, body: str) -> None:
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = smtp_cfg.get('from')
        msg['To'] = to
        msg.set_content(body)
        host = smtp_cfg.get('host')
        port = smtp_cfg.get('port', 587)
        username = smtp_cfg.get('username')
        password = smtp_cfg.get('password')
        use_tls = smtp_cfg.get('tls', True)
        with smtplib.SMTP(host, port, timeout=10) as s:
            if use_tls:
                s.starttls()
            if username and password:
                s.login(username, password)
            s.send_message(msg)

    @staticmethod
    def schedule_local(reminder_date: dt.date, message: str) -> None:
        print(f"[Reminder Scheduled] {reminder_date.isoformat()} -> {message}")

# ------------------------- TaxBot with Gemini helpers -------------------------
class TaxBot:
    def __init__(self, out_dir: Path = Path('./taxbot_output'), gemini_api_key: Optional[str] = None, gemini_model: str = "gemini-1.5-pro"):
        self.out_dir = out_dir
        ensure_dir(self.out_dir)
        self.gemini = None
        self.gemini_model = gemini_model
        if gemini_api_key:
            if genai is None:
                print("Warning: google-generativeai not installed; Gemini helpers disabled.")
            else:
                try:
                    genai.configure(api_key=gemini_api_key)
                    # Use a model handle if desired; keep client reference for calls
                    self.gemini = genai
                except Exception as e:
                    print(f"Warning: failed to configure Gemini client: {e}")
                    self.gemini = None

    # --- AI helpers ---
    def ai_summarize_document(self, text: str, max_chars: int = 4000) -> str:
        if not self.gemini:
            return "Gemini not configured"
        prompt = (
            "You are an expert tax assistant. Summarize the following document "
            "in clear bullet points and extract key numeric facts (gross salary, TDS, deductions, PAN if present). "
            "Be concise.\n\n"
            f"Document (first {max_chars} chars):\n{text[:max_chars]}"
        )
        try:
            resp = self.gemini.models.generate_content(model=self.gemini_model, contents=prompt)
            return resp.text.strip()
        except Exception as e:
            return f"Gemini error: {e}"

    def ai_categorize_income(self, text: str, max_chars: int = 4000) -> Dict[str, Any]:
        """
        Ask Gemini to propose income/deduction candidates in JSON form.
        Returns a parsed dict (best-effort) or a minimal fallback.
        """
        if not self.gemini:
            return {"error": "Gemini not configured"}
        prompt = (
            "You are a structured-data assistant. From the document below, return a JSON object with two arrays: "
            "'incomes' and 'deductions'. Each income should have: source, amount, details (optional). "
            "Each deduction should have: section, amount, details (optional). Respond only with valid JSON.\n\n"
            f"Document (first {max_chars} chars):\n{text[:max_chars]}"
        )
        try:
            resp = self.gemini.models.generate_content(model=self.gemini_model, contents=prompt)
            txt = resp.text.strip()
            # try to recover a JSON substring
            first = txt.find('{')
            last = txt.rfind('}')
            if first != -1 and last != -1:
                candidate = txt[first:last+1]
                try:
                    return json.loads(candidate)
                except Exception:
                    pass
            # fallback: attempt direct JSON parse
            return json.loads(txt)
        except Exception as e:
            return {"error": f"Gemini error: {e}"}

    def ai_check_deductions(self, incomes: List[IncomeRecord], deductions: List[Deduction]) -> str:
        if not self.gemini:
            return "Gemini not configured"
        payload = {
            "incomes": [asdict(i) for i in incomes],
            "deductions": [asdict(d) for d in deductions]
        }
        prompt = (
            "You are an Indian tax compliance assistant. Given the following incomes and deductions, "
            "check for likely errors, missing deductions, and opportunities to legally reduce tax. "
            "Return a numbered plain-English report. Data:\n" + json.dumps(payload, indent=2)
        )
        try:
            resp = self.gemini.models.generate_content(model=self.gemini_model, contents=prompt)
            return resp.text.strip()
        except Exception as e:
            return f"Gemini error: {e}"

    def ai_query_data(self, data: Dict[str, Any], nl_query: str) -> str:
        """
        Ask Gemini to answer a natural language question against a JSON data blob.
        """
        if not self.gemini:
            return "Gemini not configured"
        prompt = (
            "You are a data assistant. Given this JSON data and a user question, answer concisely. "
            "Data:\n" + json.dumps(data, indent=2) + "\n\nQuestion:\n" + nl_query
        )
        try:
            resp = self.gemini.models.generate_content(model=self.gemini_model, contents=prompt)
            return resp.text.strip()
        except Exception as e:
            return f"Gemini error: {e}"

    def ai_draft_reminder_email(self, to: str, subject_ctx: str, body_ctx: str) -> Dict[str, str]:
        """
        Drafts a polite reminder email (subject and body) using Gemini.
        """
        if not self.gemini:
            return {"subject": subject_ctx, "body": body_ctx}
        prompt = (
            "Draft a polite, professional reminder email to a client about tax-related action. "
            "Include clear next steps and a friendly closing. "
            f"Recipient: {to}\nContext/one-line subject idea: {subject_ctx}\nAdditional context: {body_ctx}"
        )
        try:
            resp = self.gemini.models.generate_content(model=self.gemini_model, contents=prompt)
            txt = resp.text.strip()
            # Simple split: first line as subject if shorter than 120 chars, rest as body
            lines = [l for l in txt.splitlines() if l.strip()]
            if not lines:
                return {"subject": subject_ctx, "body": body_ctx}
            subj = lines[0][:120]
            body = "\n".join(lines[1:]) or txt
            return {"subject": subj, "body": body}
        except Exception:
            return {"subject": subject_ctx, "body": body_ctx}

    # --- Core pipeline (non-AI) ---
    def extract(self, files: List[Path]) -> Tuple[Person, List[IncomeRecord]]:
        person = Person(name='Unknown')
        incomes: List[IncomeRecord] = []
        for f in files:
            if f.suffix.lower() == '.pdf' and pdfplumber is not None:
                text = Extractor.from_pdf_text(f)
                p = HeuristicParser.extract_person_from_text(text)
                if p and p.name != 'Unknown':
                    person = p
                incomes += HeuristicParser.extract_amounts(text)
            elif f.suffix.lower() in ('.png', '.jpg', '.jpeg', '.tiff') and pytesseract is not None:
                text = Extractor.from_image_ocr(f)
                p = HeuristicParser.extract_person_from_text(text)
                if p and p.name != 'Unknown':
                    person = p
                incomes += HeuristicParser.extract_amounts(text)
            elif f.suffix.lower() in ('.xls', '.xlsx') and pd is not None:
                df = Extractor.from_excel(f)
                for col in df.columns:
                    if any(k in col.lower() for k in ['amount', 'salary', 'income']):
                        for v in df[col].dropna().tolist():
                            try:
                                incomes.append(IncomeRecord(source=col, amount=float(v)))
                            except Exception:
                                continue
            elif f.suffix.lower() == '.csv' and pd is not None:
                df = Extractor.from_csv(f)
                for col in df.columns:
                    if any(k in col.lower() for k in ['amount', 'salary', 'income']):
                        for v in df[col].dropna().tolist():
                            try:
                                incomes.append(IncomeRecord(source=col, amount=float(v)))
                            except Exception:
                                continue
            else:
                # fallback: read as text
                try:
                    text = f.read_text(encoding='utf-8')
                    p = HeuristicParser.extract_person_from_text(text)
                    if p and p.name != 'Unknown':
                        person = p
                    incomes += HeuristicParser.extract_amounts(text)
                except Exception:
                    continue
        # merge incomes by source
        merged: Dict[str, float] = {}
        for rec in incomes:
            merged[rec.source] = merged.get(rec.source, 0.0) + rec.amount
        merged_list = [IncomeRecord(source=k, amount=ROUND2(v)) for k, v in merged.items()]
        return person, merged_list

    def calculate(self, incomes: List[IncomeRecord], deductions: List[Deduction], rebate: float = 0.0) -> TaxSummary:
        gross = sum(i.amount for i in incomes)
        ded = sum(d.amount for d in deductions)
        return TaxCalculator.compute_tax(gross_income=gross, deductions=ded, rebate=rebate)

    def autofill(self, template_json: Path, person: Person, incomes: List[IncomeRecord], deductions: List[Deduction], out_path: Path) -> Path:
        with open(template_json, 'r', encoding='utf-8') as f:
            template = json.load(f)
        return Autofiller.fill_form_json(template, person, incomes, deductions, out_path)

    def reminders(self, smtp_cfg: Optional[Dict], to: Optional[str], date: dt.date, message: str, use_gemini: bool = False) -> None:
        if use_gemini and self.gemini:
            draft = self.ai_draft_reminder_email(to or "Client", "Tax reminder", message)
            subject = draft.get("subject", "Tax reminder")
            body = draft.get("body", message)
        else:
            subject = "Tax reminder"
            body = message
        if smtp_cfg and to:
            ReminderScheduler.send_email(smtp_cfg, to, subject, body)
        else:
            ReminderScheduler.schedule_local(date, f"{subject}\n\n{body}")
    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        action = task.get("action")
        p = task.get("params", {}) or {}

        try:
            if action == "extract":
                files = [Path(f) for f in p.get("files", [])]
                person, incomes = self.extract(files)
                return {"status": "success", "person": asdict(person), "incomes": [asdict(i) for i in incomes]}

            elif action == "calculate":
                with open(p["incomes"], 'r', encoding='utf-8') as f:
                    data = json.load(f)
                incomes = [IncomeRecord(**i) for i in data.get("incomes", [])]
                deductions = []
                if "deductions" in p and p["deductions"]:
                    with open(p["deductions"], 'r', encoding='utf-8') as f:
                        ddata = json.load(f)
                    deductions = [Deduction(**d) for d in ddata.get("deductions", [])]
                rebate = float(p.get("rebate", 0.0))
                summary = self.calculate(incomes, deductions, rebate=rebate)
                return {"status": "success", "summary": asdict(summary)}

            elif action == "autofill":
                template = Path(p["template"])
                person_file = Path(p["person"])
                incomes_file = Path(p["incomes"])
                deductions_file = Path(p.get("deductions")) if p.get("deductions") else None
                out_file = Path(p["out"])

                with open(person_file, "r", encoding="utf-8") as f:
                    person = Person(**json.load(f).get("person", {}))
                with open(incomes_file, "r", encoding="utf-8") as f:
                    incomes = [IncomeRecord(**i) for i in json.load(f).get("incomes", [])]
                deductions = []
                if deductions_file and deductions_file.exists():
                    with open(deductions_file, "r", encoding="utf-8") as f:
                        deductions = [Deduction(**d) for d in json.load(f).get("deductions", [])]

                result = self.autofill(template, person, incomes, deductions, out_file)
                return {"status": "success", "autofill_output": str(result)}

            elif action == "remind":
                d = parse_date_safe(p["date"])
                msg = p["message"]
                self.reminders(None, p.get("to"), d or dt.date.today(), msg, use_gemini=p.get("use_gemini", False))
                return {"status": "success", "reminder": f"Reminder set for {d}"}

            elif action == "ai-summarize":
                text = p.get("text", "")
                return {"status": "success", "summary": self.ai_summarize_document(text)}

            elif action == "ai-categorize":
                text = p.get("text", "")
                return {"status": "success", "categorized": self.ai_categorize_income(text)}

            elif action == "ai-check-deductions":
                incomes = [IncomeRecord(**i) for i in p.get("incomes", [])]
                deductions = [Deduction(**d) for d in p.get("deductions", [])]
                return {"status": "success", "analysis": self.ai_check_deductions(incomes, deductions)}

            else:
                return {"status": "error", "message": f"Unknown action: {action}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}


# ------------------------- CLI -------------------------
def parse_args():
    p = argparse.ArgumentParser(description='TaxBot Agent – extract, calculate, autofill, reminders (with Gemini helpers)')
    sub = p.add_subparsers(dest='cmd', required=True)

    ext = sub.add_parser('extract', help='Extract data from documents')
    ext.add_argument('--files', nargs='+', required=True, type=Path)
    ext.add_argument('--out', type=Path, default=Path('./taxbot_output/extracted.json'))

    calc = sub.add_parser('calculate', help='Calculate tax from incomes and deductions')
    calc.add_argument('--incomes', type=Path, required=True, help='JSON file from extract step')
    calc.add_argument('--deductions', type=Path, required=False)
    calc.add_argument('--rebate', type=float, default=0.0)
    calc.add_argument('--out', type=Path, default=Path('./taxbot_output/tax_summary.json'))

    auto = sub.add_parser('autofill', help='Autofill a form (mock)')
    auto.add_argument('--template', required=True, type=Path)
    auto.add_argument('--person', required=True, type=Path)
    auto.add_argument('--incomes', required=True, type=Path)
    auto.add_argument('--deductions', required=False, type=Path)
    auto.add_argument('--out', required=True, type=Path)

    rem = sub.add_parser('remind', help='Schedule/send reminder')
    rem.add_argument('--date', required=True, help='YYYY-MM-DD')
    rem.add_argument('--message', required=True)
    rem.add_argument('--smtp', required=False, type=Path, help='smtp config JSON with host, port, username, password, from')
    rem.add_argument('--to', required=False, help='email recipient')
    rem.add_argument('--use-gemini', action='store_true', help='Draft email via Gemini')

    ai_sum = sub.add_parser('ai-summarize', help='Use Gemini to summarize extracted file')
    ai_sum.add_argument('--file', required=True, type=Path)
    ai_sum.add_argument('--gemini-key', required=False, help='Gemini API key (optional: env GEMINI_API_KEY)')

    ai_cat = sub.add_parser('ai-categorize', help='Use Gemini to auto-categorize incomes/deductions from text')
    ai_cat.add_argument('--file', required=True, type=Path)
    ai_cat.add_argument('--gemini-key', required=False, help='Gemini API key')

    ai_check = sub.add_parser('ai-check-deductions', help='Use Gemini to review deductions')
    ai_check.add_argument('--incomes', required=True, type=Path)
    ai_check.add_argument('--deductions', required=True, type=Path)
    ai_check.add_argument('--gemini-key', required=False, help='Gemini API key')

    return p.parse_args()

def main():
    args = parse_args()
    gemini_key = getattr(args, "gemini_key", None) or os.environ.get("GEMINI_API_KEY")
    bot = TaxBot(gemini_api_key=gemini_key)

    if args.cmd == 'extract':
        person, incomes = bot.extract(args.files)
        outp = {
            'person': asdict(person),
            'incomes': [asdict(i) for i in incomes],
            'extracted_at': dt.datetime.utcnow().isoformat()
        }
        ensure_dir(args.out.parent)
        args.out.write_text(json.dumps(outp, indent=2), encoding='utf-8')
        print(f"Extracted -> {args.out}")

    elif args.cmd == 'calculate':
        with open(args.incomes, 'r', encoding='utf-8') as f:
            data = json.load(f)
        incomes = [IncomeRecord(**i) for i in data.get('incomes', [])]
        deductions = []
        if args.deductions:
            with open(args.deductions, 'r', encoding='utf-8') as f:
                ddata = json.load(f)
            deductions = [Deduction(**d) for d in ddata.get('deductions', [])]
        summary = bot.calculate(incomes, deductions, rebate=args.rebate)
        ensure_dir(args.out.parent)
        args.out.write_text(json.dumps(asdict(summary), indent=2), encoding='utf-8')
        print(f"Tax summary -> {args.out}")

    elif args.cmd == 'autofill':
        with open(args.person, 'r', encoding='utf-8') as f:
            person = Person(**json.load(f).get('person', {}))
        with open(args.incomes, 'r', encoding='utf-8') as f:
            incomes = [IncomeRecord(**i) for i in json.load(f).get('incomes', [])]
        deductions = []
        if args.deductions:
            with open(args.deductions, 'r', encoding='utf-8') as f:
                deductions = [Deduction(**d) for d in json.load(f).get('deductions', [])]
        outp = bot.autofill(args.template, person, incomes, deductions, args.out)
        print(f"Autofilled form -> {outp}")

    elif args.cmd == 'remind':
        d = parse_date_safe(args.date) or dt.date.today()
        smtp_cfg = None
        if args.smtp:
            smtp_cfg = json.loads(args.smtp.read_text(encoding='utf-8'))
        bot.reminders(smtp_cfg, args.to, d, args.message, use_gemini=args.use_gemini)
        print("Reminder scheduled/sent.")

    elif args.cmd == 'ai-summarize':
        # Read extracted JSON or raw file
        text = ""
        if args.file.suffix.lower() == '.json':
            data = json.loads(args.file.read_text(encoding='utf-8'))
            text = json.dumps(data, indent=2)
        elif args.file.suffix.lower() in ('.pdf',):
            text = Extractor.from_pdf_text(args.file)
        else:
            text = args.file.read_text(encoding='utf-8')
        print(bot.ai_summarize_document(text))

    elif args.cmd == 'ai-categorize':
        # feed text to Gemini categorizer
        if args.file.suffix.lower() == '.pdf':
            text = Extractor.from_pdf_text(args.file)
        else:
            text = args.file.read_text(encoding='utf-8')
        print(json.dumps(bot.ai_categorize_income(text), indent=2))

    elif args.cmd == 'ai-check-deductions':
        with open(args.incomes, 'r', encoding='utf-8') as f:
            incomes = [IncomeRecord(**i) for i in json.load(f).get('incomes', [])]
        with open(args.deductions, 'r', encoding='utf-8') as f:
            deductions = [Deduction(**d) for d in json.load(f).get('deductions', [])]
        print(bot.ai_check_deductions(incomes, deductions))

if __name__ == '__main__':
    main()

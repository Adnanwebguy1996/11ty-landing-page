from __future__ import annotations

import csv
import os
import smtplib
from dataclasses import dataclass
from email.message import EmailMessage
from pathlib import Path
from typing import Iterable, List


DATA_FILE = Path(__file__).parent / "data" / "sample_businesses.csv"


@dataclass
class Lead:
    name: str
    trade: str
    city: str
    email: str
    website: str


def load_leads() -> List[Lead]:
    leads: List[Lead] = []
    with DATA_FILE.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            leads.append(
                Lead(
                    name=row["name"].strip(),
                    trade=row["trade"].strip(),
                    city=row["city"].strip(),
                    email=row["email"].strip(),
                    website=row["website"].strip(),
                )
            )
    return leads


def find_leads(trade: str, city: str, max_results: int = 25) -> List[Lead]:
    trade = trade.strip().lower()
    city = city.strip().lower()
    results: List[Lead] = []

    for lead in load_leads():
        trade_match = trade in lead.trade.lower() if trade else True
        city_match = city in lead.city.lower() if city else True
        if trade_match and city_match:
            results.append(lead)

    # Deduplicate by email
    unique = {lead.email.lower(): lead for lead in results}
    return list(unique.values())[:max_results]


def render_email(subject_template: str, body_template: str, lead: Lead) -> tuple[str, str]:
    context = {
        "name": lead.name,
        "trade": lead.trade,
        "city": lead.city,
        "email": lead.email,
        "website": lead.website,
    }
    subject = subject_template.format(**context)
    body = body_template.format(**context)
    return subject, body


def send_campaign(
    leads: Iterable[Lead],
    subject_template: str,
    body_template: str,
    dry_run: bool = True,
) -> List[dict]:
    """Send personalized emails.

    Uses SMTP settings from env vars:
    SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, SMTP_FROM.
    In dry-run mode, no email is actually sent.
    """
    logs: List[dict] = []

    smtp_host = os.getenv("SMTP_HOST", "")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER", "")
    smtp_pass = os.getenv("SMTP_PASS", "")
    smtp_from = os.getenv("SMTP_FROM", smtp_user or "noreply@example.com")

    server = None
    if not dry_run:
        if not smtp_host:
            raise ValueError("SMTP_HOST must be set when dry_run is disabled.")
        server = smtplib.SMTP(smtp_host, smtp_port)
        server.starttls()
        if smtp_user:
            server.login(smtp_user, smtp_pass)

    try:
        for lead in leads:
            subject, body = render_email(subject_template, body_template, lead)
            status = "simulated"
            error = ""

            if not dry_run and server is not None:
                try:
                    msg = EmailMessage()
                    msg["Subject"] = subject
                    msg["From"] = smtp_from
                    msg["To"] = lead.email
                    msg.set_content(body + "\n\nTo opt out, reply with UNSUBSCRIBE.")
                    server.send_message(msg)
                    status = "sent"
                except Exception as exc:  # noqa: BLE001
                    status = "failed"
                    error = str(exc)

            logs.append(
                {
                    "lead": lead,
                    "subject": subject,
                    "status": status,
                    "error": error,
                }
            )
    finally:
        if server is not None:
            server.quit()

    return logs

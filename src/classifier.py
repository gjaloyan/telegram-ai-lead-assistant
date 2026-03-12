from __future__ import annotations

from dataclasses import dataclass
import re


@dataclass
class LeadResult:
    category: str
    intent: str
    name: str | None
    phone: str | None


LEAD_KEYWORDS = ["price", "pricing", "quote", "buy", "project", "automation", "need help", "service"]
FAQ_KEYWORDS = ["how", "what", "when", "faq", "works", "feature"]
SUPPORT_KEYWORDS = ["error", "issue", "bug", "not working", "problem", "support"]


def classify_text(text: str) -> LeadResult:
    t = (text or "").strip()
    lower = t.lower()

    category = "lead"
    if any(k in lower for k in SUPPORT_KEYWORDS):
        category = "support"
    elif any(k in lower for k in FAQ_KEYWORDS) and not any(k in lower for k in LEAD_KEYWORDS):
        category = "faq"

    phone_match = re.search(r"(\+?\d[\d\s\-()]{7,}\d)", t)
    phone = phone_match.group(1).strip() if phone_match else None

    # very naive name extraction
    name_match = re.search(r"(?:my name is|i am|i'm)\s+([A-Za-zА-Яа-я][A-Za-zА-Яа-я\-']+)", lower, re.IGNORECASE)
    name = name_match.group(1).title() if name_match else None

    intent = "purchase_inquiry" if category == "lead" else ("faq_question" if category == "faq" else "support_request")
    return LeadResult(category=category, intent=intent, name=name, phone=phone)

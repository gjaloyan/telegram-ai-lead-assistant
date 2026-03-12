from __future__ import annotations

import json
import os
import re
from typing import Optional

import httpx

from .classifier import LeadResult


def _extract_json(text: str) -> dict:
    text = (text or "").strip()
    if not text:
        return {}
    # try full JSON first
    try:
        return json.loads(text)
    except Exception:
        pass
    # try fenced code block
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.S)
    if m:
        try:
            return json.loads(m.group(1))
        except Exception:
            pass
    # try first object-like region
    m = re.search(r"(\{.*\})", text, re.S)
    if m:
        try:
            return json.loads(m.group(1))
        except Exception:
            pass
    return {}


async def classify_with_openai_compatible(text: str) -> Optional[LeadResult]:
    api_key = os.getenv("AI_API_KEY", "").strip()
    if not api_key:
        return None

    base_url = os.getenv("AI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    model = os.getenv("AI_MODEL", "gpt-4o-mini")
    timeout = float(os.getenv("AI_TIMEOUT_SECONDS", "15"))

    system = (
        "You classify Telegram inbound business messages. "
        "Return ONLY JSON with keys: category, intent, name, phone. "
        "category must be one of: lead, faq, support. "
        "intent short snake_case. name/phone nullable."
    )

    payload = {
        "model": model,
        "temperature": 0,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": text or ""},
        ],
        "response_format": {"type": "json_object"},
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    url = f"{base_url}/chat/completions"
    async with httpx.AsyncClient(timeout=timeout) as client:
        r = await client.post(url, headers=headers, json=payload)
        if r.status_code >= 300:
            return None
        data = r.json()

    content = (
        data.get("choices", [{}])[0]
        .get("message", {})
        .get("content", "")
    )

    obj = _extract_json(content)
    if not obj:
        return None

    category = str(obj.get("category", "lead")).lower().strip()
    if category not in {"lead", "faq", "support"}:
        category = "lead"

    intent = str(obj.get("intent", "purchase_inquiry")).strip() or "purchase_inquiry"
    name = obj.get("name")
    phone = obj.get("phone")

    name = str(name).strip() if isinstance(name, str) and name else None
    phone = str(phone).strip() if isinstance(phone, str) and phone else None

    return LeadResult(category=category, intent=intent, name=name, phone=phone)

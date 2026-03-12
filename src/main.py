from __future__ import annotations

import os
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv

from .classifier import classify_text
from .storage import append_lead, count_rows, utc_now_iso
from .notifier import notify_telegram


load_dotenv()
LEADS_CSV_PATH = os.getenv("LEADS_CSV_PATH", "data/leads.csv")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_MANAGER_CHAT_ID = os.getenv("TELEGRAM_MANAGER_CHAT_ID", "")

app = FastAPI(title="Telegram AI Lead Assistant", version="0.1.0")


class Chat(BaseModel):
    id: int


class Message(BaseModel):
    chat: Chat
    text: str = ""


class TelegramUpdate(BaseModel):
    message: Message | None = None


@app.get("/health")
def health():
    return {"ok": True, "service": "telegram-ai-lead-assistant"}


@app.get("/stats")
def stats():
    return {"leads_total": count_rows(LEADS_CSV_PATH)}


@app.post("/webhook/telegram")
async def telegram_webhook(update: TelegramUpdate):
    if not update.message:
        return {"ok": True, "ignored": "no_message"}

    chat_id = update.message.chat.id
    text = update.message.text or ""
    result = classify_text(text)

    row = {
        "timestamp_utc": utc_now_iso(),
        "chat_id": chat_id,
        "raw_text": text,
        "category": result.category,
        "intent": result.intent,
        "name": result.name,
        "phone": result.phone,
    }
    append_lead(LEADS_CSV_PATH, row)

    alert = (
        "📥 New inbound\n"
        f"Category: {result.category}\n"
        f"Intent: {result.intent}\n"
        f"Name: {result.name or '-'}\n"
        f"Phone: {result.phone or '-'}\n"
        f"Text: {text[:400]}"
    )
    await notify_telegram(TELEGRAM_BOT_TOKEN, TELEGRAM_MANAGER_CHAT_ID, alert)

    return {"ok": True, "classified_as": result.category}

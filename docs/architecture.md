# Architecture

```mermaid
flowchart LR
    U[Telegram User] --> W[Webhook /webhook/telegram]
    W --> C[Classifier\nlead | faq | support]
    C --> S[CSV Storage\ndata/leads.csv]
    C --> N[Telegram Notifier\nManager Chat]
    S --> T[/stats endpoint]
```

## Components
- **FastAPI app** (`src/main.py`): webhook + health + stats
- **Classifier** (`src/classifier.py`): intent/category extraction
- **Storage** (`src/storage.py`): CSV append + counters
- **Notifier** (`src/notifier.py`): Telegram sendMessage alerts


from fastapi import FastAPI
from datetime import datetime, timezone

app = FastAPI(
    title="POCKET AI SIGNAL SYSTEM",
    description="AI Trading Analysis and Demo System",
    version="1.0.0"
)

@app.get("/")
def home():
    return {
        "system": "POCKET AI SIGNAL SYSTEM",
        "status": "ONLINE",
        "mode": "SAFE DEVELOPMENT",
        "trading": "DISABLED",
        "time": datetime.now(timezone.utc).isoformat()
    }

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "ai_engine": "waiting",
        "signal_engine": "waiting",
        "demo_trading": "disabled"
    }

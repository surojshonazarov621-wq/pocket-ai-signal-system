
from fastapi import FastAPI
from datetime import datetime, timezone
from pydantic import BaseModel

app = FastAPI(
    title="POCKET AI SIGNAL SYSTEM",
    description="AI Trading Signals API",
    version="3.0.0"
)

signals_history = []

class Signal(BaseModel):
    pair: str
    direction: str
    timeframe: str

@app.get("/")
def home():
    return {
        "system": "POCKET AI SIGNAL SYSTEM",
        "status": "ONLINE",
        "version": "3.0.0",
        "mode": "DEMO",
        "real_trading": False,
        "time": datetime.now(timezone.utc).isoformat()
    }

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "signal_engine": "ready",
        "real_trading": "disabled"
    }

@app.get("/signals")
def get_signals():
    return {
        "total": len(signals_history),
        "signals": signals_history
    }

@app.post("/signals")
def create_signal(data: Signal):
    if data.direction not in ["BUY", "SELL"]:
        return {"error": "Invalid direction"}

    signal = {
        "pair": data.pair,
        "direction": data.direction,
        "timeframe": data.timeframe,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "DEMO"
    }

    signals_history.append(signal)

    return {
        "status": "success",
        "signal": signal
    }

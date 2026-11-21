
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime, timezone

from trading.demo_trading import DemoTrading

app = FastAPI(
    title="POCKET AI SIGNAL SYSTEM",
    description="AI Trading Analysis and Demo System",
    version="2.0.0"
)

demo = DemoTrading(initial_balance=100.00)


class OpenTrade(BaseModel):
    signal: str


class CloseTrade(BaseModel):
    outcome: str
    payout: float = 0.80


@app.get("/")
def home():
    return {
        "system": "POCKET AI SIGNAL SYSTEM",
        "status": "ONLINE",
        "mode": "DEMO",
        "real_trading": "DISABLED",
        "time": datetime.now(timezone.utc).isoformat()
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "demo_trading": "ready",
        "ai_engine": "development",
        "real_trading": "disabled"
    }


@app.get("/demo/balance")
def balance():
    return {
        "balance": demo.balance,
        "currency": "USD"
    }


@app.post("/demo/open")
def open_demo_trade(data: OpenTrade):

    result = demo.open_trade(data.signal)

    if "error" in result:
        raise HTTPException(400, result["error"])

    return result


@app.post("/demo/close")
def close_demo_trade(data: CloseTrade):

    result = demo.close_trade(
        data.outcome,
        data.payout
    )

    if "error" in result:
        raise HTTPException(400, result["error"])

    return result


@app.get("/demo/statistics")
def statistics():
    return demo.get_statistics()

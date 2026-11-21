
from datetime import datetime, timezone
from typing import Literal

import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from signals.signal_engine import generate_signal
from trading.demo_trading import DemoTrading


app = FastAPI(
    title="POCKET AI SIGNAL SYSTEM",
    description="AI Analysis and Demo Trading API",
    version="3.1.0"
)

demo = DemoTrading(initial_balance=100.00)
signals_history = []


class AnalyzeRequest(BaseModel):
    pair: str
    timeframe: str
    candles: list[dict]


class OpenTradeRequest(BaseModel):
    signal: Literal["BUY", "SELL"]


class CloseTradeRequest(BaseModel):
    outcome: Literal["WIN", "LOSS"]
    payout: float = Field(default=0.80, ge=0, le=1)


@app.get("/")
def home():
    return {
        "system": "POCKET AI SIGNAL SYSTEM",
        "status": "ONLINE",
        "version": "3.1.0",
        "mode": "DEMO",
        "real_trading": False,
        "time": datetime.now(timezone.utc).isoformat()
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "signal_engine": "connected",
        "demo_trading": "enabled",
        "real_trading": "disabled"
    }


@app.post("/signals/analyze")
def analyze_market(data: AnalyzeRequest):

    if not data.pair.strip() or not data.timeframe.strip():
        raise HTTPException(422, "Pair va timeframe kerak")

    if len(data.candles) < 30:
        raise HTTPException(422, "Kamida 30 ta sham kerak")

    try:
        candles = pd.DataFrame(data.candles)
        result = generate_signal(candles)

    except (ValueError, TypeError, KeyError) as error:
        raise HTTPException(422, str(error))

    record = {
        "pair": data.pair,
        "timeframe": data.timeframe,
        **result,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "mode": "DEMO"
    }

    signals_history.append(record)

    return {
        "status": "success",
        "analysis": record
    }


@app.get("/signals")
def get_signals():
    return {
        "total": len(signals_history),
        "signals": signals_history[-100:]
    }


@app.get("/demo/balance")
def get_balance():
    return {
        "balance": demo.balance,
        "currency": "USD"
    }


@app.post("/demo/open")
def open_demo_trade(data: OpenTradeRequest):

    result = demo.open_trade(data.signal)

    if "error" in result:
        raise HTTPException(400, result["error"])

    return result


@app.post("/demo/close")
def close_demo_trade(data: CloseTradeRequest):

    result = demo.close_trade(
        data.outcome,
        data.payout
    )

    if "error" in result:
        raise HTTPException(400, result["error"])

    return result


@app.get("/demo/statistics")
def get_statistics():
    return demo.get_statistics()

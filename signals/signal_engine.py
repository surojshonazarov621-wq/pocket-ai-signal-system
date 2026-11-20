
import pandas as pd
from ai_engine.indicators import calculate_indicators


def generate_signal(candles):
    if candles is None or len(candles) < 30:
        return {
            "signal": "NO TRADE",
            "reason": "Yetarli ma'lumot yo'q"
        }

    df = calculate_indicators(candles)
    last = df.iloc[-1]

    required = [
        "EMA_9", "EMA_21",
        "RSI_14", "MACD",
        "MACD_SIGNAL"
    ]

    if any(pd.isna(last[x]) for x in required):
        return {
            "signal": "NO TRADE",
            "reason": "Indikatorlar tayyor emas"
        }

    buy_checks = [
        last["EMA_9"] > last["EMA_21"],
        50 < last["RSI_14"] < 70,
        last["MACD"] > last["MACD_SIGNAL"]
    ]

    sell_checks = [
        last["EMA_9"] < last["EMA_21"],
        30 < last["RSI_14"] < 50,
        last["MACD"] < last["MACD_SIGNAL"]
    ]

    buy_score = sum(buy_checks)
    sell_score = sum(sell_checks)

    if buy_score == 3:
        decision = "BUY / CALL"
        reason = "Uchta indikator ham o'sish trendini tasdiqladi"

    elif sell_score == 3:
        decision = "SELL / PUT"
        reason = "Uchta indikator ham pasayish trendini tasdiqladi"

    else:
        decision = "NO TRADE"
        reason = "Indikatorlar yetarlicha kelishmadi"

    return {
        "signal": decision,
        "reason": reason,
        "buy_confirmations": buy_score,
        "sell_confirmations": sell_score,
        "rsi": round(float(last["RSI_14"]), 2),
        "ema_9": round(float(last["EMA_9"]), 6),
        "ema_21": round(float(last["EMA_21"]), 6)
    }

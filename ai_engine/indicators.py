
import pandas as pd


def calculate_indicators(candles):
    """
    candles: OHLC ma'lumotlari.
    Kerakli ustun: close
    """

    if candles is None or len(candles) < 30:
        raise ValueError("Kamida 30 ta sham kerak")

    df = candles.copy()

    if "close" not in df.columns:
        raise ValueError("Close ustuni topilmadi")

    df["close"] = pd.to_numeric(
        df["close"], errors="coerce"
    )

    if df["close"].isna().any():
        raise ValueError("Noto'g'ri narx ma'lumotlari")

    close = df["close"]

    # EMA
    df["EMA_9"] = close.ewm(
        span=9, adjust=False
    ).mean()

    df["EMA_21"] = close.ewm(
        span=21, adjust=False
    ).mean()

    # RSI
    delta = close.diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.ewm(
        alpha=1/14, adjust=False
    ).mean()

    avg_loss = loss.ewm(
        alpha=1/14, adjust=False
    ).mean()

    rs = avg_gain / avg_loss.where(avg_loss != 0)

    df["RSI_14"] = 100 - (100 / (1 + rs))

    df.loc[
        (avg_loss == 0) & (avg_gain > 0),
        "RSI_14"
    ] = 100

    df.loc[
        (avg_loss == 0) & (avg_gain == 0),
        "RSI_14"
    ] = 50

    # MACD
    ema12 = close.ewm(
        span=12, adjust=False
    ).mean()

    ema26 = close.ewm(
        span=26, adjust=False
    ).mean()

    df["MACD"] = ema12 - ema26

    df["MACD_SIGNAL"] = df["MACD"].ewm(
        span=9, adjust=False
    ).mean()

    # Bollinger Bands
    middle = close.rolling(20).mean()
    std = close.rolling(20).std()

    df["BB_UPPER"] = middle + (2 * std)
    df["BB_LOWER"] = middle - (2 * std)

    return df

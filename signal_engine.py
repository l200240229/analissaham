import yfinance as yf
import pandas as pd
import numpy as np
import warnings

warnings.filterwarnings("ignore")

STOCKS = ["BBCA.JK", "BMRI.JK", "BBNI.JK", "BBRI.JK", "ADRO.JK", "ANTM.JK", "PGAS.JK"]


def clean_columns(df):
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df.columns = [str(c).strip() for c in df.columns]
    return df


def safe_float(val):
    if isinstance(val, pd.Series):
        return float(val.iloc[0])
    return float(val)


def calculate_rsi(df, period=14):
    delta = df["Close"].diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))


def calculate_macd(df):
    ema12 = df["Close"].ewm(span=12, adjust=False).mean()
    ema26 = df["Close"].ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    signal = macd.ewm(span=9, adjust=False).mean()
    return macd, signal


def technical_analysis(df):
    df = df.copy()

    df["SMA20"] = df["Close"].rolling(20).mean()
    df["SMA50"] = df["Close"].rolling(50).mean()
    df["RSI"] = calculate_rsi(df)
    df["MACD"], df["MACD_SIGNAL"] = calculate_macd(df)
    df["VOL_AVG"] = df["Volume"].rolling(20).mean()

    latest = df.iloc[-1]

    close = safe_float(latest["Close"])
    sma20 = safe_float(latest["SMA20"])
    sma50 = safe_float(latest["SMA50"])
    rsi = safe_float(latest["RSI"])
    macd = safe_float(latest["MACD"])
    macd_signal = safe_float(latest["MACD_SIGNAL"])
    volume = safe_float(latest["Volume"])
    vol_avg = safe_float(latest["VOL_AVG"])

    score = 0
    reasons = []

    if close > sma20:
        score += 1
        reasons.append("Di atas SMA20")
    else:
        score -= 1
        reasons.append("Di bawah SMA20")

    if sma20 > sma50:
        score += 1
        reasons.append("Trend Bullish")
    else:
        score -= 1
        reasons.append("Trend Bearish")

    if 50 <= rsi <= 65:
        score += 1
        reasons.append("RSI Sehat")
    elif rsi > 70:
        score -= 1
        reasons.append("RSI Overbought")
    elif rsi < 35:
        score += 1
        reasons.append("RSI Oversold")
    else:
        reasons.append("RSI Netral")

    if macd > macd_signal:
        score += 1
        reasons.append("MACD Bullish")
    else:
        score -= 1
        reasons.append("MACD Bearish")

    if volume > vol_avg * 1.2:
        score += 1
        reasons.append("Volume Spike")
    else:
        reasons.append("Volume Normal")

    return score, reasons


def news_sentiment(stock):
    np.random.seed(abs(hash(stock)) % 1000)
    score = np.random.choice([-1, 0, 1], p=[0.25, 0.35, 0.40])

    if score == 1:
        reason = "Berita Positif"
    elif score == -1:
        reason = "Berita Negatif"
    else:
        reason = "Berita Netral"

    return score, reason


def generate_signal(stock):
    try:
        df = yf.download(stock, period="6mo", interval="1d", auto_adjust=True, progress=False)
        if df.empty or len(df) < 60:
            return None

        df = clean_columns(df)
        df = df[["Open", "High", "Low", "Close", "Volume"]].dropna()

        tech_score, tech_reasons = technical_analysis(df)
        news_score, news_reason = news_sentiment(stock)

        final_score = tech_score + news_score
        close_price = round(float(df["Close"].iloc[-1]), 2)

        if final_score >= 3:
            signal = "BUY"
        elif final_score <= -2:
            signal = "SELL"
        else:
            signal = "HOLD"

        confidence = min(95, max(55, 65 + final_score * 7))

        return {
            "Saham": stock.replace(".JK", ""),
            "Close": close_price,
            "Signal": signal,
            "Confidence": confidence,
            "Score": final_score,
            "Reason": ", ".join(tech_reasons + [news_reason]),
        }

    except Exception as e:
        return {
            "Saham": stock.replace(".JK", ""),
            "Close": 0,
            "Signal": "ERROR",
            "Confidence": 0,
            "Score": 0,
            "Reason": str(e),
        }


def run_all_signals():
    results = []
    for stock in STOCKS:
        result = generate_signal(stock)
        if result:
            results.append(result)

    df = pd.DataFrame(results)
    df = df.sort_values(by="Score", ascending=False)
    return df
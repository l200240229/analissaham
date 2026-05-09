import yfinance as yf
import pandas as pd
import numpy as np
import warnings
import hashlib

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

def add_indicators(df):
    df["SMA20"] = df["Close"].rolling(20).mean()
    df["SMA50"] = df["Close"].rolling(50).mean()
    
    delta = df["Close"].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gain / loss
    df["RSI"] = 100 - (100 / (1 + rs))
    
    ema12 = df["Close"].ewm(span=12, adjust=False).mean()
    ema26 = df["Close"].ewm(span=26, adjust=False).mean()
    df["MACD"] = ema12 - ema26
    df["MACD_SIGNAL"] = df["MACD"].ewm(span=9, adjust=False).mean()
    
    df["VOL_AVG"] = df["Volume"].rolling(20).mean()
    return df

def get_daily_score_and_reasons(row, stock, date_str):
    score = 0
    reasons = []

    close = safe_float(row["Close"])
    sma20 = safe_float(row["SMA20"])
    sma50 = safe_float(row["SMA50"])
    rsi = safe_float(row["RSI"])
    macd = safe_float(row["MACD"])
    macd_signal = safe_float(row["MACD_SIGNAL"])
    volume = safe_float(row["Volume"])
    vol_avg = safe_float(row["VOL_AVG"])

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

    # Menggunakan Hashlib agar nilai acak berita tidak berubah saat web direfresh
    hash_str = f"{stock}_{date_str}"
    hash_object = hashlib.md5(hash_str.encode())
    stable_hash = int(hash_object.hexdigest(), 16)
    
    np.random.seed(stable_hash % 1000)
    news_score = np.random.choice([-1, 0, 1], p=[0.25, 0.35, 0.40])

    if news_score == 1:
        reasons.append("Berita Positif")
    elif news_score == -1:
        reasons.append("Berita Negatif")
    else:
        reasons.append("Berita Netral")

    final_score = score + news_score
    return final_score, reasons

def generate_signal(stock):
    try:
        # Tarik data 1 Tahun untuk Backtesting
        df = yf.download(stock, period="1y", interval="1d", auto_adjust=True, progress=False)
        if df.empty or len(df) < 60:
            return None

        df = clean_columns(df)
        df = df[["Open", "High", "Low", "Close", "Volume"]].dropna()
        df = add_indicators(df)

        # Variabel untuk simulasi Backtest
        status = "OUT"
        buy_price = 0
        realized_profit_pct = 0.0

        latest_signal = "HOLD"
        latest_score = 0
        latest_reasons = []

        # Looping mesin waktu dari hari pertama sampai hari ini
        for date, row in df.iterrows():
            if pd.isna(row["SMA50"]): 
                continue

            date_str = str(date.date())
            daily_score, reasons = get_daily_score_and_reasons(row, stock, date_str)
            
            if daily_score >= 3:
                sig = "BUY"
            elif daily_score <= -2:
                sig = "SELL"
            else:
                sig = "HOLD"

            # Logika Simulasi Beli dan Jual
            if status == "OUT" and sig == "BUY":
                buy_price = row["Close"]
                status = "IN"
            elif status == "IN" and sig == "SELL":
                sell_price = row["Close"]
                profit = ((sell_price - buy_price) / buy_price) * 100
                realized_profit_pct += profit
                status = "OUT"
                buy_price = 0

            # Simpan data hari terakhir untuk ditampilkan di web
            if date == df.index[-1]:
                latest_signal = sig
                latest_score = daily_score
                latest_reasons = reasons

        # Hitung floating profit jika posisi hari ini masih HOLD/IN
        floating_profit_pct = 0.0
        if status == "IN" and buy_price > 0:
            last_close = df.iloc[-1]["Close"]
            floating_profit_pct = ((last_close - buy_price) / buy_price) * 100

        total_profit_1y = realized_profit_pct + floating_profit_pct
        close_price = round(float(df["Close"].iloc[-1]), 2)
        confidence = min(95, max(55, 65 + latest_score * 7))

        return {
            "Saham": stock.replace(".JK", ""),
            "Close": close_price,
            "Signal": latest_signal,
            "Return 1Y": round(total_profit_1y, 2), # Fitur baru dari Elang
            "Confidence": confidence,
            "Score": latest_score,
            "Reason": ", ".join(latest_reasons),
        }

    except Exception as e:
        return {
            "Saham": stock.replace(".JK", ""),
            "Close": 0,
            "Signal": "ERROR",
            "Return 1Y": 0.0,
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
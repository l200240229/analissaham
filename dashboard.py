import streamlit as st
from signal_engine import run_all_signals

st.set_page_config(page_title="Signal Saham Indo", layout="wide")

st.title("📈 Dashboard Signal Saham Indonesia")
st.caption("Signal harian untuk eksekusi besok (BBCA, BMRI, BBNI, BBRI, ADRO, ANTM, PGAS)")

df = run_all_signals()

buy_count = (df["Signal"] == "BUY").sum()
sell_count = (df["Signal"] == "SELL").sum()
hold_count = (df["Signal"] == "HOLD").sum()

col1, col2, col3 = st.columns(3)
col1.metric("BUY", buy_count)
col2.metric("HOLD", hold_count)
col3.metric("SELL", sell_count)

st.divider()

def color_signal(val):
    if val == "BUY":
        return "background-color: #16a34a; color: white;"
    elif val == "SELL":
        return "background-color: #dc2626; color: white;"
    elif val == "HOLD":
        return "background-color: #ca8a04; color: white;"
    return ""

styled_df = df.style.format({"Close": "Rp {:,.0f}"}).map(color_signal, subset=["Signal"])

st.subheader("Signal Hari Ini")

st.dataframe(styled_df, use_container_width=True, hide_index=True)

st.subheader("Top Signal")

top = df.iloc[0]
st.success(f"Top pick besok: **{top['Saham']}** → **{top['Signal']}** (Confidence {top['Confidence']}%)")

st.subheader("Detail Analisa")
selected = st.selectbox("Pilih saham", df["Saham"].tolist())

detail = df[df["Saham"] == selected].iloc[0]
st.write(f"### {detail['Saham']}")
st.write(f"**Signal:** {detail['Signal']}")
st.write(f"**Confidence:** {detail['Confidence']}%")
st.write(f"**Score:** {detail['Score']}")
st.write(f"**Reason:** {detail['Reason']}")
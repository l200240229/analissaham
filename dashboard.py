import streamlit as st
import numpy as np
import re
import yfinance as yf
import plotly.graph_objects as go
from signal_engine import run_all_signals

# Konfigurasi Halaman (Full Screen & Icon)
st.set_page_config(page_title="Quantum Signal Indo", page_icon="🚀", layout="wide")

# ==========================================
# 🎨 UI/UX PREMIUM STYLING (CSS)
# ==========================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;800&display=swap');
html, body, [class*="css"] { font-family: 'Poppins', sans-serif; }

.title-glow {
    font-size: 42px; font-weight: 800; text-align: center;
    background: -webkit-linear-gradient(45deg, #00C9FF, #92FE9D);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin-bottom: 0px; margin-top: -40px;
}
.subtitle { text-align: center; color: #94a3b8; margin-bottom: 30px; font-size: 16px; }

/* Glassmorphism Effect pada Metric Cards */
div[data-testid="metric-container"] {
    background: rgba(30, 41, 59, 0.4);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 15px; padding: 20px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    transition: transform 0.3s ease;
}
div[data-testid="metric-container"]:hover {
    transform: translateY(-5px);
    border-color: #00C9FF;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title-glow">QUANTUM SIGNAL INDO</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">AI-Powered Trading Algorithm & Visualized Insights</div>', unsafe_allow_html=True)

# Menarik data sinyal utama dari engine
df = run_all_signals()

# Membuat 3 Tab Halaman (Radar, Detail/Chart, Kalkulator)
tab1, tab2, tab3 = st.tabs(["📊 Radar Sinyal", "📈 Detail & Chart Saham", "💎 Kalkulator Proyeksi"])

# ================= TAB 1: RADAR SINYAL UTAMA =================
with tab1:
    # Bagian Ringkasan Sinyal (Metrics)
    buy_count = (df["Signal"] == "BUY").sum()
    sell_count = (df["Signal"] == "SELL").sum()
    hold_count = (df["Signal"] == "HOLD").sum()

    m1, m2, m3 = st.columns(3)
    m1.metric("🟢 TOTAL BUY", buy_count)
    m2.metric("🟡 TOTAL HOLD", hold_count)
    m3.metric("🔴 TOTAL SELL", sell_count)

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("📡 Live Market Scanner")
    
    # Fungsi Styling Tabel
    def color_signal(val):
        if val == "BUY": return "color: #34d399; font-weight: bold; background-color: rgba(52, 211, 153, 0.1);"
        elif val == "SELL": return "color: #f87171; font-weight: bold; background-color: rgba(248, 113, 113, 0.1);"
        return "color: #fbbf24; font-weight: bold; background-color: rgba(251, 191, 36, 0.1);"

    def color_return(val):
        return "color: #34d399; font-weight: bold;" if val > 0 else "color: #f87171; font-weight: bold;"

    styled_df = df.style.format({
        "Close": "Rp {:,.0f}", 
        "Return 1Y": "{:,.2f}%"
    }).map(color_signal, subset=["Signal"]).map(color_return, subset=["Return 1Y"])

    st.dataframe(styled_df, use_container_width=True, hide_index=True)

    # --- INI BAGIAN TOP PICK YANG DIKEMBALIKAN ---
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("🏆 Top Algorithm Recommendation")
    
    top = df.iloc[0] # Mengambil baris pertama (skor tertinggi)
    with st.container(border=True):
        c1, c2 = st.columns([1, 3])
        with c1:
            st.markdown(f"<h1 style='text-align: center; color: #34d399; margin: 0;'>{top['Saham']}</h1>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align: center; margin: 0;'>Score: {top['Score']}</p>", unsafe_allow_html=True)
        with c2:
            st.success(f"Berdasarkan analisa teknikal dan sentimen, **{top['Saham']}** adalah pilihan terbaik untuk besok dengan sinyal **{top['Signal']}**.")
            st.markdown(f"**Confidence Level:** {top['Confidence']}% | **Potensi Profit (Backtest 1Thn):** {top['Return 1Y']}%")
            st.caption(f"Alasan: {top['Reason']}")


# ================= TAB 2: DETAIL & CHART (ALA BIBIT) =================
with tab2:
    st.subheader("🔍 Visualisasi Pergerakan Harga")
    
    # Dropdown pilih saham
    selected_stock = st.selectbox("Pilih Saham untuk bedah grafik:", df["Saham"].tolist())
    detail = df[df["Saham"] == selected_stock].iloc[0]
    
    col_chart, col_info = st.columns([2, 1], gap="large")
    
    with col_chart:
        with st.spinner('Menarik data pasar...'):
            ticker = f"{selected_stock}.JK"
            hist = yf.download(ticker, period="6mo", interval="1d", progress=False)
            
            if not hist.empty:
                # Grafik Area Statis (Gaya Bibit)
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=hist.index,
                    y=hist['Close'].squeeze(),
                    fill='tozeroy',
                    mode='lines',
                    line=dict(color='#00b873', width=3),
                    fillcolor='rgba(0, 184, 115, 0.1)',
                    hovertemplate='Rp %{y:,.0f}<extra></extra>'
                ))
                
                fig.update_layout(
                    xaxis=dict(showgrid=False, fixedrange=True, visible=False),
                    yaxis=dict(showgrid=False, fixedrange=True, side='right', tickformat=",.0f"),
                    margin=dict(l=0, r=0, t=10, b=0),
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    height=350,
                    hovermode="x unified"
                )
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            else:
                st.warning("Data historis tidak tersedia.")

    with col_info:
        st.markdown(f"### {selected_stock}")
        st.markdown(f"## **{detail['Signal']}**")
        st.write(f"Harga: **Rp {detail['Close']:,.0f}**")
        st.progress(detail['Confidence'] / 100, text=f"Confidence: {detail['Confidence']}%")
        
        st.markdown("---")
        st.markdown("**💡 Key Indicators:**")
        reasons = detail['Reason'].split(", ")
        for r in reasons:
            icon = "✅" if any(x in r for x in ["Atas", "Bullish", "Sehat", "Positif", "Spike"]) else "❌"
            st.write(f"{icon} {r}")


# ================= TAB 3: KALKULATOR =================
with tab3:    
    col_in, col_res = st.columns([1, 2], gap="large")
    with col_in:
        with st.container(border=True):
            st.markdown("### ⚙️ Simulasi Investasi")
            setoran = st.text_input("Setoran per Bulan (Rp):", value="1.000.000")
            bunga = st.text_input("Estimasi Profit / Tahun (%):", value="15")
            tenor = st.text_input("Durasi (Tahun):", value="5")
            btn = st.button("HITUNG PROYEKSI", use_container_width=True, type="primary")

    with col_res:
        if btn:
            try:
                num_setoran = float(re.sub(r'[^0-9]', '', setoran))
                num_bunga = float(re.sub(r'[^0-9]', '', bunga)) / 100
                num_tenor = int(re.sub(r'[^0-9]', '', tenor))
                
                saldo = 0
                history = []
                for t in range(1, num_tenor + 1):
                    for b in range(12):
                        saldo = (saldo + num_setoran) * (1 + (num_bunga/12))
                    history.append(saldo)
                
                c_a, c_b = st.columns(2)
                c_a.metric("Saldo Akhir", f"Rp {saldo:,.0f}")
                c_b.metric("Total Modal", f"Rp {num_setoran * 12 * num_tenor:,.0f}")

                fig_inv = go.Figure(data=[go.Bar(x=[f"Thn {i+1}" for i in range(num_tenor)], y=history, marker_color='#3b82f6')])
                fig_inv.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='gray'), height=300)
                st.plotly_chart(fig_inv, use_container_width=True)
            except:
                st.error("Masukkan angka yang valid.")
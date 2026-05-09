import streamlit as st
import numpy as np
import re
import plotly.graph_objects as go
import plotly.express as px
from signal_engine import run_all_signals

# Konfigurasi Halaman
st.set_page_config(page_title="Quantum Signal Indo", page_icon="🚀", layout="wide")

# ==========================================
# 🎨 UI/UX ADVANCED STYLING
# ==========================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;800&display=swap');
html, body, [class*="css"] { font-family: 'Poppins', sans-serif; }

.title-glow {
    font-size: 48px; font-weight: 800; text-align: center;
    background: -webkit-linear-gradient(45deg, #00C9FF, #92FE9D);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin-bottom: 0px; margin-top: -40px;
}
.subtitle { text-align: center; color: #94a3b8; margin-bottom: 30px; font-size: 16px; }

/* Glassmorphism Metric */
div[data-testid="metric-container"] {
    background: rgba(30, 41, 59, 0.4);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 15px; padding: 20px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title-glow">QUANTUM SIGNAL INDO</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Visualized Algorithmic Trading Dashboard</div>', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📊 Radar Sinyal & Performa", "💎 Kalkulator Proyeksi"])

# ================= TAB 1: DASHBOARD SAHAM =================
with tab1:
    df = run_all_signals()
    
    # --- ROW 1: METRICS ---
    buy_count = (df["Signal"] == "BUY").sum()
    sell_count = (df["Signal"] == "SELL").sum()
    hold_count = (df["Signal"] == "HOLD").sum()

    m1, m2, m3 = st.columns(3)
    m1.metric("🟢 TOTAL BUY", buy_count)
    m2.metric("🟡 TOTAL HOLD", hold_count)
    m3.metric("🔴 TOTAL SELL", sell_count)

    # --- ROW 2: VISUAL CHART (BAGIAN BARU) ---
    st.markdown("<br>", unsafe_allow_html=True)
    col_chart1, col_chart2 = st.columns([1, 1.5])

    with col_chart1:
        # Donut Chart untuk Distribusi Sinyal
        fig_pie = px.pie(
            values=[buy_count, hold_count, sell_count], 
            names=['BUY', 'HOLD', 'SELL'],
            hole=0.6,
            color=['BUY', 'HOLD', 'SELL'],
            color_discrete_map={'BUY':'#10b981', 'HOLD':'#f59e0b', 'SELL':'#ef4444'},
            title="Market Sentiment Radar"
        )
        fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                              font=dict(color='white'), showlegend=False, margin=dict(t=40, b=0, l=0, r=0))
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_chart2:
        # Bar Chart untuk Performa Return 1 Tahun
        fig_perf = px.bar(
            df, x='Saham', y='Return 1Y',
            color='Return 1Y',
            color_continuous_scale='Tealgrn',
            title="Akurasi Algoritma (Return 1 Tahun Terakhir)",
            text_auto='.2s'
        )
        fig_perf.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                               font=dict(color='white'), margin=dict(t=40, b=0, l=0, r=0))
        fig_perf.update_coloraxes(showscale=False)
        st.plotly_chart(fig_perf, use_container_width=True)

    # --- ROW 3: DATA TABLE ---
    st.subheader("📡 Live Market Scanner")
    def color_signal(val):
        if val == "BUY": return "color: #34d399; font-weight: bold;"
        elif val == "SELL": return "color: #f87171; font-weight: bold;"
        return "color: #fbbf24; font-weight: bold;"

    styled_df = df.style.format({"Close": "Rp {:,.0f}", "Return 1Y": "{:,.2f}%"}).map(color_signal, subset=["Signal"])
    st.dataframe(styled_df, use_container_width=True, hide_index=True)

    # --- ROW 4: DETAIL ---
    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("🏆 Top Recommendation")
        top = df.iloc[0]
        st.success(f"Analisa hari ini memprioritaskan **{top['Saham']}** untuk strategi **{top['Signal']}**.")
    with c2:
        st.subheader("💡 Logic Breakdown")
        sel = st.selectbox("Bedah indikator saham:", df["Saham"].tolist())
        det = df[df["Saham"] == sel].iloc[0]
        st.info(f"**Alasan:** {det['Reason']}")

# ================= TAB 2: KALKULATOR INVESTASI =================
with tab2:    
    col_input, col_grafik = st.columns([1, 2.2], gap="large")

    with col_input:
        st.markdown("<br>", unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown("### ⚙️ Parameter")
            input_setoran = st.text_input("Setoran Rutin / Bulan:", value="1.500.000")
            input_return = st.text_input("Ekspektasi Return / Tahun (%):", value="15")
            input_tahun = st.text_input("Horizon Waktu (Tahun):", value="10")
            
            st.markdown("<br>", unsafe_allow_html=True)
            btn_hitung = st.button("🔥 JALANKAN PROYEKSI", use_container_width=True, type="primary")

    with col_grafik:
        if btn_hitung:
            try:
                def clean_number(text):
                    return re.sub(r'[^0-9]', '', text)

                pmt = float(clean_number(input_setoran))
                r_tahunan = float(clean_number(input_return)) / 100
                t_total = int(clean_number(input_tahun))
                
                if t_total > 50: t_total = 50

                r_bulanan = r_tahunan / 12
                saldo = 0
                saldo_per_tahun = []
                
                for thn in range(1, t_total + 1):
                    for bln in range(1, 13):
                        saldo = (saldo + pmt) * (1 + r_bulanan)
                    saldo_per_tahun.append(saldo)

                total_modal = pmt * t_total * 12
                keuntungan = saldo - total_modal

                m1, m2, m3 = st.columns(3)
                m1.metric("Modal Diinvestasikan", f"Rp {total_modal:,.0f}")
                m2.metric("Total Keuntungan (Bunga)", f"Rp {keuntungan:,.0f}")
                m3.metric("Estimasi Kekayaan", f"Rp {saldo:,.0f}")

                # GRAFIK PLOTLY YANG LEBIH MEWAH
                tahun_labels = [f"Thn {i}" for i in range(1, t_total + 1)]
                
                fig = go.Figure(data=[
                    go.Bar(
                        x=tahun_labels, 
                        y=saldo_per_tahun, 
                        marker=dict(
                            color=saldo_per_tahun,
                            colorscale='Teal', # Gradasi warna hijau-biru
                            showscale=False
                        ),
                        hovertemplate='<b>%{x}</b><br>Kekayaan: Rp %{y:,.0f}<extra></extra>'
                    )
                ])
                
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#cbd5e1', family="Poppins"),
                    xaxis=dict(showgrid=False),
                    yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)'),
                    margin=dict(l=0, r=0, t=30, b=0),
                    hovermode="x unified"
                )

                st.plotly_chart(fig, use_container_width=True)

            except Exception:
                st.error("Format angka salah. Pastikan hanya menggunakan angka.")
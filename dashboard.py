import streamlit as st
import numpy as np
import re
import plotly.graph_objects as go
from signal_engine import run_all_signals

# Konfigurasi Halaman (Full Screen & Icon)
st.set_page_config(page_title="Signal Saham Indo", page_icon="🚀", layout="wide", initial_sidebar_state="collapsed")

# ==========================================
# 🎨 UI/UX SUPER PREMIUM (CSS INJECTIONS)
# ==========================================
st.markdown("""
<style>
/* Import Font Premium (Poppins) */
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif;
}

/* Header Gradient & Glowing */
.title-glow {
    font-size: 52px;
    font-weight: 800;
    text-align: center;
    background: -webkit-linear-gradient(45deg, #00C9FF, #92FE9D);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 5px;
    margin-top: -30px;
}
.subtitle {
    text-align: center;
    color: #94a3b8;
    margin-bottom: 40px;
    font-size: 18px;
    font-weight: 300;
}

/* Glassmorphism & Neon Effect pada Metric Cards */
div[data-testid="metric-container"] {
    background: rgba(30, 41, 59, 0.4);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 20px;
    padding: 25px 20px;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
    border-left: 5px solid #00C9FF;
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}
div[data-testid="metric-container"]:hover {
    transform: translateY(-8px) scale(1.02);
    box-shadow: 0 15px 40px 0 rgba(0, 201, 255, 0.2);
    border-left: 5px solid #92FE9D;
}

/* Styling Tab Premium */
.stTabs [data-baseweb="tab-list"] {
    background-color: #0f172a;
    border-radius: 15px;
    padding: 5px;
    box-shadow: inset 0 2px 4px rgba(0,0,0,0.5);
    gap: 10px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 10px;
    color: #cbd5e1;
    padding: 10px 20px;
    transition: all 0.3s;
}
.stTabs [aria-selected="true"] {
    background: rgba(255, 255, 255, 0.05);
    color: #00C9FF !important;
    border-bottom: 2px solid #00C9FF;
}

/* Custom Table Background */
[data-testid="stDataFrame"] {
    border-radius: 15px;
    overflow: hidden;
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 🚀 HEADER SECTION
# ==========================================
st.markdown('<div class="title-glow">QUANTUM SIGNAL INDO</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">AI-Powered Trading Algorithm & Proyeksi Finansial</div>', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📊 Radar Saham & Backtest", "💎 Kalkulator Compounding"])

# ================= TAB 1: DASHBOARD SAHAM =================
with tab1:
    df = run_all_signals()

    # Layout Metric
    buy_count = (df["Signal"] == "BUY").sum()
    sell_count = (df["Signal"] == "SELL").sum()
    hold_count = (df["Signal"] == "HOLD").sum()

    col1, col2, col3 = st.columns(3)
    col1.metric("🔥 Momentum BUY", buy_count)
    col2.metric("🛡️ Fase HOLD", hold_count)
    col3.metric("⚠️ Sinyal SELL", sell_count)

    st.markdown("<br><br>", unsafe_allow_html=True)

    def color_signal(val):
        if val == "BUY":
            return "background-color: rgba(16, 185, 129, 0.15); color: #34d399; font-weight: 600;"
        elif val == "SELL":
            return "background-color: rgba(239, 68, 68, 0.15); color: #f87171; font-weight: 600;"
        elif val == "HOLD":
            return "background-color: rgba(245, 158, 11, 0.15); color: #fbbf24; font-weight: 600;"
        return ""

    def color_return(val):
        if val > 0:
            return "color: #34d399; font-weight: 800;"
        elif val < 0:
            return "color: #f87171; font-weight: 800;"
        return ""

    styled_df = df.style.format({
        "Close": "Rp {:,.0f}",
        "Return 1Y": "{:,.2f}%"
    }).map(color_signal, subset=["Signal"]).map(color_return, subset=["Return 1Y"])

    st.subheader("📡 Real-time Market Scanner")
    st.dataframe(styled_df, use_container_width=True, hide_index=True)

    st.markdown("<hr style='border-color: rgba(255,255,255,0.1);'>", unsafe_allow_html=True)

    col_detail1, col_detail2 = st.columns(2)
    with col_detail1:
        st.subheader("👑 Top Pick Algorithm")
        top = df.iloc[0]
        st.success(f"Sistem merekomendasikan **{top['Saham']}** dengan status **{top['Signal']}** (Confidence: **{top['Confidence']}%**).\n\n🚀 *Simulasi algoritma ini mencetak profit **{top['Return 1Y']}%** dalam 1 tahun terakhir.*", icon="🤖")

    with col_detail2:
        st.subheader("🧠 Logika Mesin")
        selected = st.selectbox("Pilih saham untuk dibedah:", df["Saham"].tolist(), label_visibility="collapsed")
        detail = df[df["Saham"] == selected].iloc[0]
        
        reasons_list = detail['Reason'].split(", ")
        for r in reasons_list:
            if "Di atas" in r or "Bullish" in r or "Sehat" in r or "Positif" in r or "Spike" in r:
                st.markdown(f"✅ <span style='color:#34d399'>{r}</span>", unsafe_allow_html=True)
            elif "Di bawah" in r or "Bearish" in r or "Overbought" in r or "Negatif" in r:
                st.markdown(f"❌ <span style='color:#f87171'>{r}</span>", unsafe_allow_html=True)
            else:
                st.markdown(f"➖ <span style='color:#94a3b8'>{r}</span>", unsafe_allow_html=True)


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
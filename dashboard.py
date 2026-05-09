import streamlit as st
import numpy as np
import re
import plotly.graph_objects as go
from signal_engine import run_all_signals

# Konfigurasi Halaman (Tambahkan Icon)
st.set_page_config(page_title="Signal Saham Indo", page_icon="📈", layout="wide")

# --- CUSTOM CSS UNTUK UI MODERN ---
st.markdown("""
<style>
/* Styling untuk Metric Card agar terlihat menonjol dan modern */
div[data-testid="metric-container"] {
    background-color: #1a1c23;
    border: 1px solid #2e323a;
    padding: 15px 20px;
    border-radius: 12px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.15);
    transition: transform 0.2s ease-in-out;
}
div[data-testid="metric-container"]:hover {
    transform: translateY(-3px);
    border-color: #3b82f6;
}
/* Menghilangkan background bawaan tab agar lebih clean */
.stTabs [data-baseweb="tab-list"] {
    gap: 20px;
}
.stTabs [data-baseweb="tab"] {
    padding-top: 10px;
    padding-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

# Membuat sistem Tab
tab1, tab2 = st.tabs(["📈 Dashboard Signal & Backtest", "💼 Kalkulator Investasi Pro"])

# ================= TAB 1: DASHBOARD SAHAM =================
with tab1:
    st.title("Dashboard Signal Saham")
    st.caption("Rekomendasi algoritma harian & simulasi akurasi 1 tahun terakhir (BBCA, BMRI, BBNI, BBRI, ADRO, ANTM, PGAS)")

    df = run_all_signals()

    # Layout Metric 3 Kolom
    buy_count = (df["Signal"] == "BUY").sum()
    sell_count = (df["Signal"] == "SELL").sum()
    hold_count = (df["Signal"] == "HOLD").sum()

    col1, col2, col3 = st.columns(3)
    col1.metric("🟢 Sinyal BUY", buy_count)
    col2.metric("🟡 Sinyal HOLD", hold_count)
    col3.metric("🔴 Sinyal SELL", sell_count)

    st.markdown("<br>", unsafe_allow_html=True)

    def color_signal(val):
        if val == "BUY":
            return "background-color: rgba(22, 163, 74, 0.2); color: #4ade80; font-weight: bold;"
        elif val == "SELL":
            return "background-color: rgba(220, 38, 38, 0.2); color: #f87171; font-weight: bold;"
        elif val == "HOLD":
            return "background-color: rgba(202, 138, 4, 0.2); color: #facc15; font-weight: bold;"
        return ""

    def color_return(val):
        if val > 0:
            return "color: #4ade80; font-weight: bold;"
        elif val < 0:
            return "color: #f87171; font-weight: bold;"
        return ""

    styled_df = df.style.format({
        "Close": "Rp {:,.0f}",
        "Return 1Y": "{:,.2f}%"
    }).map(color_signal, subset=["Signal"]).map(color_return, subset=["Return 1Y"])

    st.subheader("📊 Tabel Analisa Real-time")
    st.dataframe(styled_df, use_container_width=True, hide_index=True)

    # Layout 2 Kolom untuk Detail di bawahnya
    col_detail1, col_detail2 = st.columns(2)
    
    with col_detail1:
        st.subheader("🏆 Top Pick Besok")
        top = df.iloc[0]
        st.info(f"**{top['Saham']}** direkomendasikan **{top['Signal']}** dengan akurasi model **{top['Confidence']}%**.\n\nJika kamu mengikuti sinyal saham ini selama 1 tahun terakhir, profit tercatat sebesar **{top['Return 1Y']}%**.")

    with col_detail2:
        st.subheader("🔍 Detail Alasan")
        selected = st.selectbox("Cek alasan algoritma pada saham tertentu:", df["Saham"].tolist())
        detail = df[df["Saham"] == selected].iloc[0]
        st.write(f"**Indikator yang memicu sinyal {detail['Signal']}:**")
        
        # Format list alasan menjadi bullet points
        reasons_list = detail['Reason'].split(", ")
        for r in reasons_list:
            st.markdown(f"- {r}")


# ================= TAB 2: KALKULATOR INVESTASI =================
with tab2:
    st.title("Kalkulator Investasi Pro")
    st.caption("Hitung proyeksi compounding interest/bunga berbunga dari setoran rutinmu.")
    
    col_input, col_grafik = st.columns([1, 2.5], gap="large")

    with col_input:
        with st.container(border=True): # Menggunakan container bergaris bawaan Streamlit
            st.markdown("**📝 INPUT DATA**")
            input_setoran = st.text_input("Setoran Bulanan:", placeholder="Contoh: 1.000.000", value="1000000")
            input_return = st.text_input("Return Per Tahun (%):", placeholder="Contoh: 15", value="15")
            input_tahun = st.text_input("Lama Investasi (Tahun):", placeholder="Contoh: 10", value="10")
            
            st.markdown("<br>", unsafe_allow_html=True)
            btn_hitung = st.button("Hitung Proyeksi", use_container_width=True, type="primary")

    with col_grafik:
        if btn_hitung:
            try:
                def clean_number(text):
                    return re.sub(r'[^0-9]', '', text)

                pmt = float(clean_number(input_setoran))
                r_tahunan = float(clean_number(input_return)) / 100
                t_total = int(clean_number(input_tahun))
                
                if t_total > 50:
                    t_total = 50

                r_bulanan = r_tahunan / 12
                saldo = 0
                saldo_per_tahun = []
                
                for thn in range(1, t_total + 1):
                    for bln in range(1, 13):
                        saldo = (saldo + pmt) * (1 + r_bulanan)
                    saldo_per_tahun.append(saldo)

                total_modal = pmt * t_total * 12
                keuntungan = saldo - total_modal

                # Metric untuk Kalkulator
                m1, m2, m3 = st.columns(3)
                m1.metric("Modal Disetor", f"Rp {total_modal:,.0f}")
                m2.metric("Total Profit", f"Rp {keuntungan:,.0f}")
                m3.metric("Estimasi Saldo Akhir", f"Rp {saldo:,.0f}")

                # GRAFIK INTERAKTIF MENGGUNAKAN PLOTLY
                tahun_labels = [f"Thn {i}" for i in range(1, t_total + 1)]
                
                fig = go.Figure(data=[
                    go.Bar(
                        x=tahun_labels, 
                        y=saldo_per_tahun, 
                        marker_color='#3b82f6',
                        hovertemplate='<b>%{x}</b><br>Saldo: Rp %{y:,.0f}<extra></extra>' # Tooltip saat di-hover
                    )
                ])
                
                fig.update_layout(
                    title="📈 Grafik Pertumbuhan Dana (Compounding)",
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    xaxis=dict(showgrid=False),
                    yaxis=dict(showgrid=True, gridcolor='#334155'),
                    margin=dict(l=0, r=0, t=40, b=0)
                )

                st.plotly_chart(fig, use_container_width=True)

            except Exception:
                st.error("Error: Input harus angka! Jangan kosongkan kolom atau isi dengan format yang salah.")
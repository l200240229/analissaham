import streamlit as st
import numpy as np
import re
import yfinance as yf
import plotly.graph_objects as go
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
    font-size: 42px; font-weight: 800; text-align: center;
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

# Menarik data sinyal utama
df = run_all_signals()

# Membuat 3 Tab Halaman
tab1, tab2, tab3 = st.tabs(["📊 Radar Sinyal", "📈 Detail & Chart Saham", "💎 Kalkulator Proyeksi"])

# ================= TAB 1: RADAR SINYAL UTAMA =================
with tab1:
    buy_count = (df["Signal"] == "BUY").sum()
    sell_count = (df["Signal"] == "SELL").sum()
    hold_count = (df["Signal"] == "HOLD").sum()

    m1, m2, m3 = st.columns(3)
    m1.metric("🟢 TOTAL BUY", buy_count)
    m2.metric("🟡 TOTAL HOLD", hold_count)
    m3.metric("🔴 TOTAL SELL", sell_count)

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("📡 Live Market Scanner")
    
    def color_signal(val):
        if val == "BUY": return "color: #34d399; font-weight: bold;"
        elif val == "SELL": return "color: #f87171; font-weight: bold;"
        return "color: #fbbf24; font-weight: bold;"

    styled_df = df.style.format({"Close": "Rp {:,.0f}", "Return 1Y": "{:,.2f}%"}).map(color_signal, subset=["Signal"])
    st.dataframe(styled_df, use_container_width=True, hide_index=True)


# ================= TAB 2: DETAIL & CHART (ALA BIBIT) =================
with tab2:
    st.subheader("🔍 Halaman Detail Saham")
    
    # Dropdown pilih saham
    selected_stock = st.selectbox("Pilih Saham untuk melihat pergerakan harga:", df["Saham"].tolist())
    
    # Ambil detail sinyal dari dataframe
    detail = df[df["Saham"] == selected_stock].iloc[0]
    
    col_kiri, col_kanan = st.columns([2, 1])
    
    with col_kiri:
        with st.spinner('Memuat grafik harga...'):
            # Tarik data historis 6 bulan ke belakang khusus untuk saham yang dipilih
            ticker = f"{selected_stock}.JK"
            hist = yf.download(ticker, period="6mo", interval="1d", progress=False)
            
            if not hist.empty:
                # Membuat Grafik Area (Bibit Style)
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=hist.index,
                    y=hist['Close'].squeeze(), # Mengambil nilai harga Close
                    fill='tozeroy',
                    mode='lines',
                    line=dict(color='#00b873', width=2), # Warna Hijau khas Bibit
                    fillcolor='rgba(0, 184, 115, 0.15)', # Gradasi transparan di bawah garis
                    hovertemplate='Tanggal: %{x|%d %b %Y}<br>Harga: Rp %{y:,.0f}<extra></extra>'
                ))
                
                # Mematikan grid dan mengunci grafik agar statis (tidak bisa di-zoom/geser)
                fig.update_layout(
                    xaxis=dict(showgrid=False, fixedrange=True, visible=False), # Sumbu X disembunyikan agar bersih
                    yaxis=dict(showgrid=False, fixedrange=True, side='right', tickformat=",.0f"),
                    margin=dict(l=0, r=0, t=10, b=0),
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    height=300,
                    hovermode="x unified"
                )
                
                # config={'displayModeBar': False} menyembunyikan toolbar plotly di atas grafik
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            else:
                st.error("Gagal memuat data grafik.")

    with col_kanan:
        st.markdown(f"### Status: **{detail['Signal']}**")
        st.write(f"Harga Terakhir: **Rp {detail['Close']:,.0f}**")
        st.write(f"Akurasi AI: **{detail['Confidence']}%**")
        st.write(f"Profit Simulasi 1 Thn: **{detail['Return 1Y']}%**")
        
        st.markdown("---")
        st.markdown("**🧠 Alasan Algoritma:**")
        reasons_list = detail['Reason'].split(", ")
        for r in reasons_list:
            if "Di atas" in r or "Bullish" in r or "Sehat" in r or "Positif" in r or "Spike" in r:
                st.markdown(f"✅ <span style='color:#34d399'>{r}</span>", unsafe_allow_html=True)
            elif "Di bawah" in r or "Bearish" in r or "Overbought" in r or "Negatif" in r:
                st.markdown(f"❌ <span style='color:#f87171'>{r}</span>", unsafe_allow_html=True)
            else:
                st.markdown(f"➖ <span style='color:#94a3b8'>{r}</span>", unsafe_allow_html=True)


# ================= TAB 3: KALKULATOR =================
with tab3:    
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

                tahun_labels = [f"Thn {i}" for i in range(1, t_total + 1)]
                
                fig = go.Figure(data=[
                    go.Bar(
                        x=tahun_labels, 
                        y=saldo_per_tahun, 
                        marker=dict(
                            color=saldo_per_tahun,
                            colorscale='Teal', 
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
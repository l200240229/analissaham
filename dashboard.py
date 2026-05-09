import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import re
from signal_engine import run_all_signals

st.set_page_config(page_title="Signal Saham Indo", layout="wide")

# Membuat sistem Tab untuk memisahkan fitur
tab1, tab2 = st.tabs(["📈 Dashboard Signal & Backtest", "💼 Kalkulator Investasi Pro"])

# ================= TAB 1: DASHBOARD SAHAM =================
with tab1:
    st.title("📈 Dashboard Signal Saham Indonesia")
    st.caption("Signal harian untuk eksekusi besok beserta rekaman akurasi bot selama 1 tahun terakhir.")

    df = run_all_signals()

    buy_count = (df["Signal"] == "BUY").sum()
    sell_count = (df["Signal"] == "SELL").sum()
    hold_count = (df["Signal"] == "HOLD").sum()

    col1, col2, col3 = st.columns(3)
    col1.metric("Sinyal BUY", buy_count)
    col2.metric("Sinyal HOLD", hold_count)
    col3.metric("Sinyal SELL", sell_count)

    st.divider()

    def color_signal(val):
        if val == "BUY":
            return "background-color: #16a34a; color: white;"
        elif val == "SELL":
            return "background-color: #dc2626; color: white;"
        elif val == "HOLD":
            return "background-color: #ca8a04; color: white;"
        return ""

    def color_return(val):
        if val > 0:
            return "color: #16a34a; font-weight: bold;"
        elif val < 0:
            return "color: #dc2626; font-weight: bold;"
        return ""

    # Memasukkan format kolom baru "Return 1Y"
    styled_df = df.style.format({
        "Close": "Rp {:,.0f}",
        "Return 1Y": "{:,.2f}%"
    }).map(color_signal, subset=["Signal"]).map(color_return, subset=["Return 1Y"])

    st.subheader("Signal Hari Ini & Hasil Backtest 1 Tahun")
    st.dataframe(styled_df, use_container_width=True, hide_index=True)

    st.subheader("Top Signal")
    top = df.iloc[0]
    st.success(f"Top pick besok: **{top['Saham']}** → **{top['Signal']}** (Confidence {top['Confidence']}%) | Profit 1 Thn: **{top['Return 1Y']}%**")

    st.subheader("Detail Analisa")
    selected = st.selectbox("Pilih saham", df["Saham"].tolist())

    detail = df[df["Saham"] == selected].iloc[0]
    st.write(f"### {detail['Saham']}")
    st.write(f"**Signal:** {detail['Signal']}")
    st.write(f"**Profit Simulasi 1 Tahun:** {detail['Return 1Y']}%")
    st.write(f"**Confidence:** {detail['Confidence']}%")
    st.write(f"**Score:** {detail['Score']}")
    st.write(f"**Reason:** {detail['Reason']}")


# ================= TAB 2: KALKULATOR INVESTASI =================
with tab2:
    st.title("💼 Kalkulator Investasi Pro v2.1")
    st.caption("Hitung proyeksi compounding interest/bunga berbunga dari modal investasimu.")
    
    col_input, col_grafik = st.columns([1, 2])

    with col_input:
        st.markdown("**INPUT DATA**")
        input_setoran = st.text_input("Setoran Bulanan:", placeholder="Contoh: 1.000.000", value="1000000")
        input_return = st.text_input("Return Per Tahun (%):", placeholder="Contoh: 20", value="10")
        input_tahun = st.text_input("Lama Investasi:", placeholder="Contoh: 20 tahun", value="10")
        
        btn_hitung = st.button("HITUNG SEKARANG", use_container_width=True, type="primary")

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
                
                # Looping perhitungan dari kode asli Elang
                for thn in range(1, t_total + 1):
                    for bln in range(1, 13):
                        saldo = (saldo + pmt) * (1 + r_bulanan)
                    saldo_per_tahun.append(saldo)

                total_modal = pmt * t_total * 12
                keuntungan = saldo - total_modal

                m1, m2, m3 = st.columns(3)
                m1.metric("Total Modal", f"Rp {total_modal:,.0f}")
                m2.metric("Total Profit", f"Rp {keuntungan:,.0f}")
                m3.metric("Saldo Akhir", f"Rp {saldo:,.0f}")

                fig, ax = plt.subplots(figsize=(6, 4))
                tahun_labels = np.arange(1, t_total + 1)
                ax.bar(tahun_labels, saldo_per_tahun, color='#1f538d')
                ax.set_title("Proyeksi Pertumbuhan Dana")
                ax.yaxis.set_major_formatter(plt.FormatStrFormatter('%d'))
                
                # Membuat background grafik transparan menyatu dengan web
                fig.patch.set_alpha(0.0)
                ax.patch.set_alpha(0.0)
                ax.tick_params(colors='gray')
                ax.xaxis.label.set_color('gray')
                ax.yaxis.label.set_color('gray')
                ax.title.set_color('gray')

                st.pyplot(fig)

            except Exception:
                st.error("Error: Input harus angka! Jangan kosongkan kolom atau isi dengan format yang salah.")
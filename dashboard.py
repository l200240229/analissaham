import streamlit as st
import numpy as np
import re
import yfinance as yf
import plotly.graph_objects as go
import urllib.request
import xml.etree.ElementTree as ET
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
st.markdown('<div class="subtitle">Trading Algorithm & Visualized Insights</div>', unsafe_allow_html=True)

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
        val_str = str(val)
        if val_str.startswith("+"):
            return "color: #34d399; font-weight: bold;"
        elif val_str.startswith("-"):
            return "color: #f87171; font-weight: bold;"
        return ""

    # Format styling cukup nggo Close wae, Return 1Y ra perlu di-format maneh
    styled_df = df.style.format({
        "Close": "Rp {:,.0f}"
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
    # ==========================================
    # 📰 BAGIAN BARU: AGGREGATOR BERITA (GAMBAR & TANGGAL)
    # ==========================================
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("📰 Market Update (Real-Time)")
    
    # Fungsi pintar untuk mengambil RSS beserta Gambar dan Tanggal
    def fetch_news(url, limit=3):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            xml_data = urllib.request.urlopen(req, timeout=5).read()
            root = ET.fromstring(xml_data)
            
            news_list = []
            for item in root.findall('./channel/item')[:limit]:
                title = item.find('title').text
                link = item.find('link').text
                
                # Mengambil tanggal rilis (pubDate)
                pub_date_node = item.find('pubDate')
                pub_date = pub_date_node.text if pub_date_node is not None else "Waktu tidak diketahui"
                
                # Membersihkan format tanggal agar lebih rapi (menghapus zona waktu di belakangnya)
                if len(pub_date) > 20:
                    pub_date = pub_date[:22] # Memotong teks timezone seperti '+0700'
                
                # Mencari link gambar
                image_url = "https://via.placeholder.com/150x100?text=No+Image"
                enclosure = item.find('enclosure')
                if enclosure is not None and 'url' in enclosure.attrib:
                    image_url = enclosure.attrib['url']
                else:
                    desc = item.find('description')
                    if desc is not None and desc.text:
                        match = re.search(r'src="([^"]+)"', desc.text)
                        if match:
                            image_url = match.group(1)
                            
                news_list.append({
                    'title': title,
                    'link': link,
                    'image': image_url,
                    'date': pub_date # Menyimpan data tanggal
                })
            return news_list
        except Exception:
            return []

    with st.spinner("Menarik berita pasar terbaru..."):
        cnbc_news = fetch_news('https://www.cnbcindonesia.com/market/rss', 3)
        idx_news = fetch_news('https://www.idxchannel.com/rss', 3)
        
        col_cnbc, col_idx = st.columns(2, gap="large")
        
        # Kolom Kiri: CNBC Indonesia
        with col_cnbc:
            st.markdown("#### 🔴 CNBC Indonesia")
            if not cnbc_news:
                st.caption("Gagal memuat berita CNBC.")
            for news in cnbc_news:
                title = news['title']
                if len(title) > 65: title = title[:65] + "..."
                
                with st.container(border=True):
                    c_img, c_txt = st.columns([1, 2.5])
                    with c_img:
                        st.image(news['image'], use_container_width=True)
                    with c_txt:
                        st.markdown(f"**[{title}]({news['link']})**")
                        # Menampilkan jam/tanggal rilis berita
                        st.caption(f"⏱️ {news['date']} | CNBC Market")

        # Kolom Kanan: IDX Channel
        with col_idx:
            st.markdown("#### 🔵 IDX Channel")
            if not idx_news:
                st.caption("Gagal memuat berita IDX.")
            for news in idx_news:
                title = news['title']
                if len(title) > 65: title = title[:65] + "..."
                
                with st.container(border=True):
                    c_img, c_txt = st.columns([1, 2.5])
                    with c_img:
                        st.image(news['image'], use_container_width=True)
                    with c_txt:
                        st.markdown(f"**[{title}]({news['link']})**")
                        # Menampilkan jam/tanggal rilis berita
                        st.caption(f"⏱️ {news['date']} | BEI / IDX Channel")
            
    st.markdown("<br>", unsafe_allow_html=True)

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
            st.markdown("### ⚙️ Kakulator Proyeksi Investasi")
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
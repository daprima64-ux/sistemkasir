import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import io
import os

# --- KONFIGURASI TEMA & DESAIN ---
st.set_page_config(page_title="Pupis Manager", layout="wide")

# CSS untuk mempercantik tampilan
st.markdown("""
    <style>
    .stApp { background-color: #FFFDF5; }
    .stButton>button { 
        background-color: #F6BC25; 
        color: #5F3C2B; 
        border-radius: 10px; 
        font-weight: bold;
        border: 2px solid #5F3C2B;
    }
    .stMetric { 
        background-color: #ffffff; 
        padding: 20px; 
        border-radius: 15px; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border-left: 5px solid #F6BC25;
    }
    h1, h2, h3 { color: #5F3C2B !important; font-family: 'Arial'; }
    </style>
    """, unsafe_allow_html=True)

# --- DATABASE ---
FILE_JUAL = "db_penjualan.csv"
FILE_KELUAR = "db_pengeluaran.csv"

def load_csv(file, cols):
    if not os.path.exists(file): return pd.DataFrame(columns=cols)
    return pd.read_csv(file)

# --- DATA MENU ---
SEMUA_MENU = {
    "Pisang Wijen (Original)": 15000, "Pisang Wijen (Taro)": 15000, "Pisang Wijen (Tiramisu)": 15000,
    "Pisang Wijen (Coklat)": 15000, "Pisang Wijen (Strawberry)": 15000, "Pisang Wijen (Matcha)": 15000,
    "Pisang Wijen (Cappucino)": 15000, "Nasi Ayam Popcorn Matah": 18000, 
    "Mie Ayam Popcorn Matah": 18000, "Nasi Telor Sambal Matah": 15000,
    "Hekeng KW": 15000, "Pempek": 15000, "Kentang Goreng": 15000,
    "Lemon Tea": 8000, "Coklat": 10000, "Matcha": 10000, "Tiramisu": 10000,
    "Sunny Milkult": 15000, "Greeny Milkult": 15000
}

# --- HEADER ---
st.title("🍌 PUPIS - Dapur Pisang")
st.write("Sistem Kasir & Manajemen Keuangan Digital")

tab1, tab2, tab3, tab4 = st.tabs(["🛒 Kasir Digital", "💸 Catat Pengeluaran", "📈 Analisis Profit", "📂 Laporan Excel"])

# 1. KASIR
with tab1:
    col_in1, col_in2 = st.columns(2)
    with col_in1:
        with st.form("kasir_form", clear_on_submit=True):
            st.subheader("Input Pesanan")
            menu = st.selectbox("Menu", list(SEMUA_MENU.keys()))
            jml = st.number_input("Jumlah Porsi", min_value=1, value=1)
            top = st.number_input("Tambahan Topping (Rp)", min_value=0, step=1000)
            if st.form_submit_button("Selesaikan Transaksi"):
                total = (SEMUA_MENU[menu] * jml) + top
                df = load_csv(FILE_JUAL, ["Tanggal", "Menu", "Jumlah", "Total"])
                new_data = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d"), menu, jml, total]], columns=df.columns)
                pd.concat([df, new_data]).to_csv(FILE_JUAL, index=False)
                st.balloons()
                st.success(f"Berhasil dicatat: Rp {total:,}")

# 2. PENGELUARAN
with tab2:
    with st.form("keluar_form", clear_on_submit=True):
        st.subheader("Catat Pengeluaran")
        ket = st.text_input("Keterangan (misal: Beli Pisang, Gas, Plastik)")
        nom = st.number_input("Nominal Pengeluaran (Rp)", min_value=0, step=5000)
        if st.form_submit_button("Simpan Biaya"):
            df = load_csv(FILE_KELUAR, ["Tanggal", "Keterangan", "Total"])
            new_data = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d"), ket, nom]], columns=df.columns)
            pd.concat([df, new_data]).to_csv(FILE_KELUAR, index=False)
            st.success("Biaya berhasil dicatat!")

# 3. PROFIT
with tab3:
    df_j = load_csv(FILE_JUAL, ["Tanggal", "Menu", "Jumlah", "Total"])
    df_k = load_csv(FILE_KELUAR, ["Tanggal", "Keterangan", "Total"])
    
    c1, c2, c3 = st.columns(3)
    omzet = df_j['Total'].sum() if not df_j.empty else 0
    beban = df_k['Total'].sum() if not df_k.empty else 0
    c1.metric("Total Omzet", f"Rp {omzet:,}")
    c2.metric("Total Biaya", f"Rp {beban:,}")
    c3.metric("Profit Bersih", f"Rp {omzet - beban:,}")
    
    if not df_j.empty:
        st.write("---")
        fig = px.bar(df_j.groupby("Menu")["Total"].sum().reset_index(), 
                     x="Menu", y="Total", title="Penjualan per Menu",
                     color_discrete_sequence=['#F6BC25'])
        st.plotly_chart(fig, use_container_width=True)

# 4. EXCEL
with tab4:
    if st.button("Generate Laporan Excel"):
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            load_csv(FILE_JUAL, []).to_excel(writer, sheet_name='Data Penjualan', index=False)
            load_csv(FILE_KELUAR, []).to_excel(writer, sheet_name='Data Pengeluaran', index=False)
        st.download_button("Klik untuk Unduh Laporan", data=output.getvalue(), file_name="Laporan_Keuangan_Pupis.xlsx")
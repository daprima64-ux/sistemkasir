import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import io
import os

# --- 1. SETUP ---
st.set_page_config(page_title="Pupis Manager", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #FFFDF5; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border-left: 5px solid #F6BC25; }
    h1, h2, h3 { color: #5F3C2B !important; }
    </style>
    """, unsafe_allow_html=True)

# Fungsi untuk mendapatkan Hari dalam Bahasa Indonesia
def get_hari_indo():
    hari_dict = {"Monday": "Senin", "Tuesday": "Selasa", "Wednesday": "Rabu", "Thursday": "Kamis", "Friday": "Jumat", "Saturday": "Sabtu", "Sunday": "Minggu"}
    day_en = datetime.now().strftime("%A")
    return hari_dict.get(day_en, day_en)

# --- 2. DATABASE ---
FILE_JUAL = "db_penjualan.csv"
FILE_KELUAR = "db_pengeluaran.csv"

def load_csv(file, cols):
    if not os.path.exists(file): return pd.DataFrame(columns=cols)
    return pd.read_csv(file)

MAKANAN = {
    "Pisang Wijen (Original)": 15000, "Pisang Wijen (Taro)": 15000, "Pisang Wijen (Tiramisu)": 15000,
    "Pisang Wijen (Coklat)": 15000, "Pisang Wijen (Strawberry)": 15000, "Pisang Wijen (Matcha)": 15000,
    "Pisang Wijen (Cappucino)": 15000, "Nasi Ayam Popcorn Matah": 18000, 
    "Mie Ayam Popcorn Matah": 18000, "Nasi Telor Sambal Matah": 15000,
    "Hekeng KW": 15000, "Pempek": 15000, "Kentang Goreng": 15000
}
MINUMAN = {
    "Lemon Tea": 8000, "Coklat": 10000, "Matcha": 10000, "Tiramisu": 10000, 
    "Sunny Milkult": 15000, "Greeny Milkult": 15000
}

# --- 3. HEADER & SIDEBAR ---
st.title("🍌 PUPIS - Dapur Pisang")
modal_awal = st.sidebar.number_input("💰 Modal Awal Kas (Hari Ini)", value=0, step=1000)

tab1, tab2, tab3, tab4 = st.tabs(["🛒 Kasir Digital", "💸 Uang Keluar", "📊 Ringkasan Laporan", "📂 Ekspor Excel"])

# --- 4. TAB KASIR ---
with tab1:
    st.header("Catat Penjualan")
    with st.form("form_jual", clear_on_submit=True):
        col1, col2 = st.columns(2)
        pilihan_makanan = col1.selectbox("Makanan", ["-"] + list(MAKANAN.keys()))
        pilihan_minuman = col2.selectbox("Minuman", ["-"] + list(MINUMAN.keys()))
        qty = st.number_input("Jumlah Porsi", min_value=1, value=1)
        st.write("---")
        nama_topping = st.text_input("Nama Topping (isi '-' jika tidak ada)")
        harga_topping = st.number_input("Harga Topping (per porsi)", min_value=0, step=1000)
        
        if st.form_submit_button("Selesaikan Transaksi"):
            item_dipilih = pilihan_makanan if pilihan_makanan != "-" else pilihan_minuman
            harga_dasar = MAKANAN.get(pilihan_makanan, 0) if pilihan_makanan != "-" else MINUMAN.get(pilihan_minuman, 0)
            
            if item_dipilih != "-":
                total_harga = (harga_dasar + harga_topping) * qty
                catatan = f"{item_dipilih} + {nama_topping}" if nama_topping != "-" else item_dipilih
                
                # Menambah kolom Hari dan Tanggal
                df = load_csv(FILE_JUAL, ["Hari", "Tanggal", "Menu", "Jumlah", "Total"])
                new_data = pd.DataFrame([[get_hari_indo(), datetime.now().strftime("%Y-%m-%d"), catatan, qty, total_harga]], columns=df.columns)
                pd.concat([df, new_data]).to_csv(FILE_JUAL, index=False)
                st.success(f"✅ Berhasil dicatat: {catatan} x{qty} = Rp {total_harga:,}")
            else:
                st.error("Silakan pilih minimal satu menu!")

# --- 5. TAB PENGELUARAN ---
with tab2:
    st.header("Catat Uang Keluar (Belanja)")
    with st.form("form_keluar", clear_on_submit=True):
        item_beli = st.text_input("Nama Barang/Bahan")
        col_q, col_p = st.columns(2)
        qty_beli = col_q.number_input("Qty / Jumlah", min_value=1, value=1)
        harga_satuan = col_p.number_input("Harga Satuan (Rp)", min_value=0, step=500)
        
        if st.form_submit_button("Catat Pengeluaran"):
            total_keluar = qty_beli * harga_satuan
            df = load_csv(FILE_KELUAR, ["Hari", "Tanggal", "Keterangan", "Total"])
            new_data = pd.DataFrame([[get_hari_indo(), datetime.now().strftime("%Y-%m-%d"), f"{item_beli} (x{qty_beli})", total_keluar]], columns=df.columns)
            pd.concat([df, new_data]).to_csv(FILE_KELUAR, index=False)
            st.warning(f"⚠️ Pengeluaran {item_beli} x{qty_beli} tercatat sebesar Rp {total_keluar:,}")

# --- 6. TAB LAPORAN ---
with tab3:
    st.header("Ringkasan Laporan")
    df_j = load_csv(FILE_JUAL, ["Hari", "Tanggal", "Menu", "Jumlah", "Total"])
    df_k = load_csv(FILE_KELUAR, ["Hari", "Tanggal", "Keterangan", "Total"])
    
    total_masuk = df_j['Total'].sum() if not df_j.empty else 0
    total_keluar = df_k['Total'].sum() if not df_k.empty else 0
    sisa_uang = (modal_awal + total_masuk) - total_keluar
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Omzet", f"Rp {total_masuk:,}")
    col2.metric("Sisa Uang di Tangan", f"Rp {sisa_uang:,}")
    col3.metric("Profit Bersih", f"Rp {total_masuk - total_keluar:,}")

# --- 7. TAB EXCEL ---
with tab4:
    if st.button("Generate Master Excel"):
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            load_csv(FILE_JUAL, []).to_excel(writer, sheet_name='Data Penjualan', index=False)
            load_csv(FILE_KELUAR, []).to_excel(writer, sheet_name='Data Pengeluaran', index=False)
        st.download_button("📥 Download Laporan", data=output.getvalue(), file_name="Laporan_Pupis_Master.xlsx")

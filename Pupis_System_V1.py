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
                
                # SINI PERBAIKANNYA: Pastikan list data ada 5 item sesuai kolom CSV
                df = load_csv(FILE_JUAL, ["Hari", "Tanggal", "Menu", "Jumlah", "Total"])
                new_data = pd.DataFrame([[get_hari_indo(), datetime.now().strftime("%Y-%m-%d"), catatan, qty, total_harga]], columns=df.columns)
                pd.concat([df, new_data]).to_csv(FILE_JUAL, index=False)
                
                st.success(f"✅ Berhasil dicatat: {catatan} x{qty}")
            else:
                st.error("Silakan pilih minimal satu menu!")

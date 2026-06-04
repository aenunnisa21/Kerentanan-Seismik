import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io

# Konfigurasi Tampilan
st.set_page_config(page_title="Kalkulator Kg Mikrotremor", page_icon="🌍", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.write("## Tentang Aplikasi")
    st.info("Aplikasi ini dibuat untuk menghitung nilai Indeks Kerentanan Seismik (Kg) berdasarkan data mikrotremor menggunakan metode HVSR.")
    st.write("Dibuat oleh: **Aenunnisa**")
    st.write("---")
    st.write("© 2026")

# --- JUDUL UTAMA ---
st.title("🌍 Aplikasi Indeks Kerentanan Seismik ($K_g$)")
st.write("Aplikasi untuk menghitung nilai kerentanan seismik dari data Excel (A0 & f0) atau ekstrak otomatis dari file Geopsy (.hv).")

# Navigasi Tab
tab1, tab2 = st.tabs(["📁 Data Excel/CSV (A0 & f0)", "📈 Ekstrak File .HV (Geopsy)"])

# --- TAB 1: DATA EXCEL / CSV ---
with tab1:
    st.header("Proses Data dari Excel/CSV")
    st.info("Pastikan file Anda memiliki kolom bernama **A0** dan **f0** pada baris pertama (header).")
    
    uploaded_file = st.file_uploader("Upload File Excel/CSV", type=['csv', 'xlsx'])
    
    if uploaded_file:
        df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
        
        if 'A0' in df.columns and 'f0' in df.columns:
            df['Kg'] = (df['A0']**2) / df['f0']
            st.dataframe(df)
            
            towrite = io.BytesIO()
            df.to_excel(towrite, index=False, engine='xlsxwriter')
            st.download_button("⬇️ Download Hasil (Excel)", data=towrite.getvalue(), file_name="Hasil_Kg.xlsx")
        else:
            st.error("Gagal diproses: Kolom 'A0' atau 'f0' tidak ditemukan dalam file!")

# --- TAB 2: FILE .HV GEOPSY ---
with tab2:
    st.header("Analisis Langsung File .HV")
    st.write("Unggah file hasil ekspor Geopsy Anda di sini.")
    
    hv_file = st.file_uploader("Pilih file .hv / .txt", type=['hv', 'txt'])
    
    if hv_file:
        try:
            # Membaca data dengan mengabaikan header komentar '#'
            df_hv = pd.read_csv(hv_file, sep=r'\s+', comment='#', header=None)
            
            # FIX: Menyesuaikan jumlah kolom secara otomatis
            col_names = ['Freq', 'Avg']
            for i in range(2, len(df_hv.columns)):
                col_names.append(f'Col_{i}')
            df_hv.columns = col_names
            
            # Cari letak Peak tertinggi di kolom Avg
            idx_max = df_hv['Avg'].idxmax()
            f0_p = df_hv.loc[idx_max, 'Freq']
            a0_p = df_hv.loc[idx_max, 'Avg']
            
            # Hitung Kg
            kg_p = (a0_p**2) / f0_p
            
            # Tampilkan Hasil berupa angka
            c1, c2, c3 = st.columns(3)
            c1.metric("f0 (Peak)", f"{f0_p:.3f} Hz")
            c2.metric("A0 (Peak)", f"{a0_p:.3f}")
            c3.metric("Nilai Kg", f"{kg_p:.4f}")
            
            # Plot Kurva H/V
            fig, ax = plt.subplots(figsize=(10, 4))
            ax.plot(df_hv['Freq'], df_hv['Avg'], label='Kurva H/V', color='#1f77b4')
            ax.scatter(f0_p, a0_p, color='red', s=100, label=f'Peak (Kg = {kg_p:.2f})')
            ax.set_xlabel("Frekuensi (Hz)")
            ax.set_ylabel("Amplitudo")
            ax.set_title(f"Kurva H/V dan Titik Puncak - {hv_file.name}")
            ax.grid(True, alpha=0.3)
            ax.legend()
            
            st.pyplot(fig)
            
        except Exception as e:
            st.error(f"Gagal membaca file. Pastikan isinya sesuai format standar tabel Geopsy. Error detail: {e}")

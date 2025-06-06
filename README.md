# 🚦 SmartCity Bengkulu - Sistem Navigasi & Prediksi Kemacetan

Sistem ini merupakan aplikasi navigasi cerdas untuk Kota Bengkulu berbasis **AI (XGBoost Classifier)** dan **OpenStreetMap**, yang mampu memprediksi kemacetan lalu lintas dan menyarankan rute alternatif secara interaktif melalui peta.

---

## 📌 1. Model AI yang Digunakan

### 🔍 Model: **XGBoost Classifier**
**Alasan Pemilihan:**
- Lebih cepat dan akurat dibanding model dasar seperti Decision Tree.
- Mampu menangani data kecil maupun besar.
- Cocok untuk klasifikasi biner seperti: **macet (1)** atau **tidak macet (0)**.

Model dilatih berdasarkan fitur panjang jalan (`length`) dan menyimpan hasilnya dalam file `xgb_model.json`.

---

## 🗂️ 2. Jenis & Sumber Data

### 📍 Data Geospasial:
- **Sumber**: [OpenStreetMap (OSM)](https://www.openstreetmap.org)
- **Library**: `OSMnx`
- **File**: `bengkulu.graphml` → menyimpan data jalan Kota Bengkulu.

### ⚙️ Data Latih Model:
- Fitur: panjang jalan (`length`)
- Label: 1 (macet) jika panjang > 200 meter (asumsi)
- Model dilatih dalam file `smartcity_navigation.py`

---

## 🔄 3. Alur Kerja Sistem

### 🧭 Deskripsi Singkat:

1. Pengguna menjalankan Backend FastAPI terlebih dahulu
2. Pengguna membuka website dari `index.html`
3. Pengguna memasukkan **lokasi awal dan tujuan**.
4. Sistem akan:
   - Melakukan **geocoding** nama lokasi menjadi koordinat.
   - Mencari node terdekat pada peta.
   - Memuat graph jalan dari `bengkulu.graphml`.
   - Melakukan prediksi kemacetan tiap segmen menggunakan `xgb_model.json`.
   - Menghitung **rute utama (A*)** dan **rute alternatif** (menghindari macet).
5. Visualisasi rute muncul pada `navigation_map.html`.


### Diagram Alur Sistem
<img src="https://github.com/user-attachments/assets/44aba3ac-ba4a-412e-9771-028abb333cbb" alt="Diagram Alur Sistem" width="400"/>

---

## 📁 Struktur Folder

```
├── cache/                       # Folder penyimpanan cache (jika ada)
├── bengkulu.graphml             # Graph peta jalan OSM untuk Bengkulu
├── index1.html                  # (Opsional) Halaman HTML manual (jika digunakan)
├── navigation_map.html          # Output peta interaktif (hasil program)
├── requirements.txt             # Daftar dependency Python
├── smartcity_navigation.py      # Program utama (navigasi & prediksi)
├── xgb_model.json               # Model AI yang telah dilatih
```

---

## 🧪 Cara Menjalankan

### 1. Instalasi Dependency
```bash
pip install -r requirements.txt
```

### 2. Jalankan Server FastAPI
```bash
uvicorn smartcity_navigation:app --reload --host 0.0.0.0 --port 8001
```

### 3. Buka Index.html
Buka file `index.html` di browser untuk mencari rute dari lokasi awal ke lokasi tujuan.

### 4. Lihat Output
Tunggu peta dimuat dan menampilkan rute dan prediksi kemacetan di `index.html`.

---

## 🧠 Evaluasi Model

> Karena data latih dibuat secara simulatif (berdasarkan panjang jalan), akurasi tidak mencerminkan kondisi nyata, tapi arsitektur sudah siap menerima data kemacetan real.

### Metrik Potensial:
- Accuracy data dari sumber OSM
- Perbandingan waktu tempuh rute utama vs alternatif

---

## 🚀 Pengembangan Lanjutan

✅ Integrasi data kemacetan real-time  
✅ Aplikasi berbasis web atau mobile   
✅ Sistem pelaporan masyarakat  
✅ Prediksi kemacetan berdasarkan waktu (jam/hari)

---

## 🙋 Tentang Proyek

- **Nama, NPM**:
[Sallaa Fikriyatul Arifah G1A023015]
[Najwa Nabilah Wibisono G1A023065]
- **Mata Kuliah**: Kecerdasan Buatan
- **Dosen**: [Ir. Arie Vatresia, S.T., M.T.I., Ph.D]

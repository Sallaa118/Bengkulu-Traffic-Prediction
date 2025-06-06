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
├── index.html                  # (Opsional) Halaman HTML manual (jika digunakan)
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

## Pengujian Aplikasi
> Pengujian dilakukan dengan studi kasus yaitu melakukan pencarian rute dan prediksi kemacetan dari lokasi awal yaitu Lingkar Barat ke 10 Lokasi Tujuan yang berbeda
<div style="display: flex; flex-wrap: wrap; gap: 10px; justify-content: center;">

  <img src="https://github.com/user-attachments/assets/1d0bc73d-0a58-49c0-a281-6bc6cabdf05a" width="180"/>
  <img src="https://github.com/user-attachments/assets/935ac980-317d-4afe-9fe0-a020c5c194c8" width="180"/>
  <img src="https://github.com/user-attachments/assets/12a89b2a-8032-46cd-81f8-b2c49735ad5a" width="180"/>
  <img src="https://github.com/user-attachments/assets/26d2b358-e4ac-4e4e-a680-be4e3ca0e1c6" width="180"/>
  <img src="https://github.com/user-attachments/assets/24748897-cc5b-46d7-a8fc-715f5615ad9e" width="180"/>

  <img src="https://github.com/user-attachments/assets/ea0e205b-a567-4871-b531-5ecf7a876de6" width="180"/>
  <img src="https://github.com/user-attachments/assets/11c1c0da-2041-442e-a8dc-a38fb7ddce90" width="180"/>
  <img src="https://github.com/user-attachments/assets/9c58e844-8b18-47a0-ab7e-d4198c5dba53" width="180"/>
  <img src="https://github.com/user-attachments/assets/4e942662-4f6d-436f-b3f9-fa875196d35b" width="180"/>
  <img src="https://github.com/user-attachments/assets/264851f0-1eab-40d8-a3b0-2baf04190642" width="180"/>

</div>

> Pengujian selanjutnya membandingkan hasil output untuk `Rute dengan jarak terjauh`, `Rute tanpa prediksi kemacetan`, `Rute dengan prediksi kemacetan terpanjang`
<div style="display: flex; flex-wrap: wrap; gap: 10px; justify-content: center;">

  <img src="https://github.com/user-attachments/assets/0e104d6d-f6c9-4240-a80f-af99af804592" width="250"/>
  <img src="https://github.com/user-attachments/assets/935ac980-317d-4afe-9fe0-a020c5c194c8" width="250"/>
  <img src="https://github.com/user-attachments/assets/0e104d6d-f6c9-4240-a80f-af99af804592" width="250"/>

</div>

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

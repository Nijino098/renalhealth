# RenalHealth AI — Backend Setup

## Struktur Proyek

```
renalhealth/
├── app.py                  ← Flask backend (logika utama)
├── requirements.txt        ← Dependensi Python
├── static/
│   └── cara-kerja.png      ← Gambar modal "Cara Kerja Platform"
└── templates/
    ├── home.html           ← Halaman utama
    ├── deteksi.html        ← Form input parameter klinis
    └── hasil.html          ← Halaman hasil analisis
```

## Cara Menjalankan

### 1. Install dependensi
```bash
pip install -r requirements.txt
```

### 2. Jalankan server
```bash
python app.py
```

### 3. Buka di browser
```
http://127.0.0.1:5000
```

---

## Navigasi & Fitur

| Tombol / Link               | Aksi                                        |
|-----------------------------|---------------------------------------------|
| **Mulai Deteksi Sekarang**  | → `/deteksi` (form input parameter klinis)  |
| **Get Started** (navbar)    | → `/deteksi`                                |
| **Get Started** (CTA)       | → `/deteksi`                                |
| **Pelajari Lebih Lanjut**   | Buka modal gambar "Cara Kerja Platform"     |
| **Analisis Hasil** (form)   | POST ke `/deteksi` → redirect ke `/hasil`   |
| **Deteksi Ulang**           | → `/deteksi` (form baru)                    |
| **Cetak / Simpan PDF**      | `window.print()` untuk print/save PDF       |

---

## Logika Backend (`app.py`)

### Algoritma Risiko CKD
- **8 parameter** dianalisis: GDP, BP, Hb, Ureum, Creat, G2H, Chol, BMI
- Setiap parameter memiliki **4 level**: normal, ringan, sedang, berat
- Parameter diberi **bobot** sesuai signifikansi klinis:
  - Kreatinin (3.0) — tertinggi, indikator utama ginjal
  - Ureum (2.5) — biomarker filtrasi
  - Tekanan Darah (2.0) — faktor risiko utama CKD
  - GDP & G2H (1.5 masing-masing) — risiko diabetes
  - Hemoglobin (1.5) — anemia renal
  - Kolesterol (1.0) — risiko kardiovaskular
  - BMI (0.5)

### eGFR & Stadium CKD (KDIGO 2022)
| eGFR (mL/min/1.73m²) | Stadium | Label                |
|-----------------------|---------|----------------------|
| ≥ 90                  | G1      | Normal               |
| 60–89                 | G2      | Penurunan Ringan     |
| 45–59                 | G3a     | Ringan-Sedang        |
| 30–44                 | G3b     | Sedang-Berat         |
| 15–29                 | G4      | Penurunan Berat      |
| < 15                  | G5      | Gagal Ginjal         |

### Routes
| Route        | Method     | Deskripsi                        |
|--------------|------------|----------------------------------|
| `/`          | GET        | Halaman utama (home.html)        |
| `/deteksi`   | GET        | Form input (deteksi.html)        |
| `/deteksi`   | POST       | Proses form → redirect `/hasil`  |
| `/hasil`     | GET        | Tampilkan hasil (hasil.html)     |

---

## Disclaimer Medis
Aplikasi ini adalah **alat bantu skrining**, bukan pengganti diagnosa dokter.
Selalu konsultasikan hasil dengan dokter spesialis ginjal (Nefrolog).

<div align="center">

# 👁️ VisionCCTV

### Asisten pemantauan pintu masuk dan antrean untuk restoran & lobi hotel, dari CCTV yang sudah Anda punya

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![YOLOv8](https://img.shields.io/badge/Deteksi-YOLOv8-00A3E0)
![Tracker](https://img.shields.io/badge/Pelacak-ByteTrack-6C5CE7)
![Dashboard](https://img.shields.io/badge/Dashboard-Streamlit%20%7C%20Web-FF4B4B)
![Tests](https://img.shields.io/badge/Unit%20test-35%20kasus-2EA043)
![Status](https://img.shields.io/badge/Status-Prototipe-orange)

[Fitur](#-fitur-utama) · [Cara Kerja](#-cara-kerja) · [Mulai Cepat](#-mulai-cepat) · [Konfigurasi](#%EF%B8%8F-konfigurasi) · [Pengujian](#-pengujian) · [Privasi](#-privasi--keamanan) · [Roadmap](#%EF%B8%8F-roadmap)

</div>

---

## 🎯 Tentang Proyek

Banyak restoran dan hotel sudah punya CCTV, tetapi kameranya hanya merekam. **VisionCCTV mengubah kamera menjadi sumber data**: berapa orang masuk, kapan jam tersibuk, seberapa panjang antrean kasir, dan kapan perlu menambah pegawai.

Sistem ini dirancang sebagai **alat bantu keputusan manajer, bukan pengganti manajer**. Semua metrik bersifat agregat (tim/proses), tanpa pengenalan wajah dan tanpa penilaian individu.

> **Status:** prototipe untuk keperluan magang/edukasi. Belum dimaksudkan untuk produksi.

<!--
  TODO: tambahkan tangkapan layar atau GIF demo di sini.
  Contoh: ![Demo](docs/images/demo.gif)
-->

---

## ✨ Fitur Utama

| | Fitur | Yang dilakukan |
|---|---|---|
| 🚪 | **Penghitung pengunjung** | Menghitung orang masuk dan keluar saat melintasi garis virtual di pintu |
| ⏱️ | **Pemantau antrean kasir** | Menghitung jumlah orang di zona antrean dan lama menunggu tiap orang |
| 🔔 | **Alert Telegram** | Mengirim peringatan saat antrean panjang atau waktu tunggu terlalu lama |
| 📊 | **Dashboard manajer** | Grafik per jam, jam sibuk akhir pekan, dan saran penambahan pegawai |
| 🧪 | **Simulator data** | Mengisi database dengan data 4 minggu agar dashboard bisa dicoba tanpa kamera |

<details>
<summary><b>Detail teknis tiap fitur</b></summary>

**Penghitung pengunjung (`line_counter.py`)**
- Arah lintasan ditentukan dari *cross-product* posisi tengah bounding box sebelum dan sesudah bergerak.
- *Cooldown* dan histeresis per ID pelacak mencegah orang yang berdiri atau bergoyang di dekat garis terhitung berulang.

**Pemantau antrean (`queue_monitor.py`)**
- Zona kasir berupa poligon; keberadaan orang dicek dengan *point-in-polygon*.
- Waktu masuk tiap ID dicatat untuk menghitung durasi tunggu.
- *Lost grace period* (default 3 detik) mencegah ID yang hilang sesaat karena terhalang dianggap pergi.
- Alert dengan *cooldown* agar notifikasi tidak dikirim tiap frame:

| Alert | Pemicu (default) |
|---|---|
| `ALERT_ANTREAN_PANJANG` | Orang di zona ≥ 5 |
| `ALERT_TUNGGU_LAMA` | Ada orang menunggu ≥ 120 detik |

**Dashboard**
- **Web dashboard** (`flowtask-dashboard/`): tampilan *soft SaaS*, grafik per jam, slider persentil jam sibuk akhir pekan, dan rekomendasi penambahan pegawai.
- **Streamlit** (`dashboard.py`): analisis tren dan pelaporan dari database SQLite.

</details>

---

## 🧠 Cara Kerja

```mermaid
flowchart LR
    A["Video / RTSP<br/>kamera ONVIF"] --> B["monitor.py"]
    B --> C["YOLOv8<br/>deteksi orang"]
    C --> D["ByteTrack<br/>ID konsisten"]
    D --> E["line_counter.py<br/>garis pintu"]
    D --> F["queue_monitor.py<br/>zona kasir"]
    E -->|IN / OUT| G[("SQLite<br/>visits")]
    F -->|sampel & waktu tunggu| H[("SQLite<br/>queue_samples")]
    F -->|alert| I[("SQLite<br/>events")]
    I --> J["notifier.py<br/>Telegram"]
    G --> K["Dashboard"]
    H --> K
    I --> K
    K --> L["Web dashboard"]
    K --> M["Streamlit"]
```

**Prinsip desain:** modul logika (`line_counter.py`, `queue_monitor.py`) adalah *logika murni*, tidak mengimpor OpenCV atau YOLO. Hasilnya bisa diuji cepat tanpa kamera dan tanpa model.

---

## 🚀 Mulai Cepat

**Prasyarat:** Python 3.10+ dan Git.

```bash
# 1. Pasang dependensi
pip install -r requirements.txt

# 2. Isi database dengan data simulasi (tanpa kamera)
python simulate.py

# 3. Buka dashboard
python server.py                      # http://localhost:3000 (web dashboard)
# atau
streamlit run dashboard.py            # http://localhost:8501 (Streamlit)
# atau gunakan menu interaktif:
python menu.py                        # pilih opsi [2] atau [3]
```

Untuk menjalankan deteksi pada video atau kamera:

```bash
python monitor.py                     # tekan "q" pada jendela video untuk keluar
```

<details>
<summary><b>Semua perintah</b></summary>

| Perintah | Fungsi |
|---|---|
| `python -m pytest tests/ -v` | Menjalankan 35 unit test |
| `python simulate.py` | Mengisi `data.db` dengan data simulasi 4 minggu |
| `python monitor.py` | Deteksi video/CCTV secara real-time |
| `python server.py` | Web dashboard di `localhost:3000` |
| `streamlit run dashboard.py` | Dashboard Streamlit di `localhost:8501` |
| `python menu.py` | Pusat kontrol & command launcher interaktif |
| `python -m py_compile *.py` | Cek sintaks semua skrip Python |

</details>

> **Catatan data simulasi:** angka seperti jumlah kunjungan dan alert pada dashboard demo berasal dari `simulate.py`, **bukan** dari rekaman restoran sungguhan.

---

## ⚙️ Konfigurasi

Semua parameter ada di `config.json`.

```json
{
    "source": "samples/contoh.mp4",
    "line": { "pt1": [300, 400], "pt2": [900, 400], "in_direction": "down" },
    "queue_zone": [[100, 300], [500, 300], [500, 600], [100, 600]],
    "queue_max_people": 5,
    "queue_max_wait_sec": 120,
    "alert_cooldown_sec": 60,
    "lost_grace_sec": 3,
    "queue_sample_interval_sec": 30,
    "yolo_model": "yolov8n.pt",
    "confidence": 0.4,
    "tracker": "bytetrack.yaml",
    "telegram_token_env": "TELEGRAM_TOKEN",
    "telegram_chat_id_env": "TELEGRAM_CHAT_ID",
    "db_path": "data.db"
}
```

| Parameter | Arti |
|---|---|
| `source` | File video lokal atau URL RTSP kamera, mis. `rtsp://user:pass@192.168.1.100:554/...` |
| `line.pt1`, `line.pt2` | Dua titik garis virtual pintu (piksel) |
| `line.in_direction` | Arah dianggap "masuk": `down`/`positive` atau `up`/`negative` |
| `queue_zone` | Titik-titik poligon zona antrean kasir |
| `queue_max_people` | Batas jumlah orang untuk `ALERT_ANTREAN_PANJANG` |
| `queue_max_wait_sec` | Batas waktu tunggu (detik) untuk `ALERT_TUNGGU_LAMA` |
| `alert_cooldown_sec` | Jeda minimal antar alert sejenis |
| `lost_grace_sec` | Toleransi ID hilang sesaat sebelum dianggap pergi |
| `queue_sample_interval_sec` | Interval pencatatan sampel antrean |
| `yolo_model`, `confidence`, `tracker` | Model deteksi, ambang keyakinan, dan konfigurasi pelacak |
| `telegram_token_env`, `telegram_chat_id_env` | **Nama** variabel lingkungan (bukan nilainya) |
| `db_path` | Lokasi database SQLite |

### Mengatur notifikasi Telegram

Token dan chat ID dibaca dari variabel lingkungan, jangan ditulis di kode atau di-commit.

```bash
# Linux / macOS
export TELEGRAM_TOKEN="isi-token-bot"
export TELEGRAM_CHAT_ID="isi-chat-id"
```

```powershell
# Windows PowerShell
$env:TELEGRAM_TOKEN = "isi-token-bot"
$env:TELEGRAM_CHAT_ID = "isi-chat-id"
```

---

## 📷 Menghubungkan Kamera

| | |
|---|---|
| **Kamera target** | BARDI Smart Indoor PTZ IP Camera (WiFi 2.4GHz, indoor) |
| **Protokol** | ONVIF dan RTSP |
| **Codec disarankan** | H.264 (H.265 tidak selalu terbaca OpenCV) |
| **Stream** | Sub-stream resolusi rendah untuk komputasi lebih ringan bila tersedia |

**Langkah:**

1. Cari IP kamera di halaman admin router.
2. Aktifkan ONVIF dan buat akun ONVIF jika ada menunya (sering terpisah dari akun aplikasi).
3. Ambil URL RTSP dengan **ONVIF Device Manager** atau library `onvif-zeep` (`GetStreamUri`). Jangan menebak URL.
4. Uji URL di VLC, lalu isi `source` di `config.json`.

> ⚠️ **Kunci posisi PTZ** dan matikan patroli otomatis. Jika kamera bergeser, garis hitung dan zona antrean menjadi tidak akurat dan perlu dikalibrasi ulang.

---

## 🧪 Pengujian

```bash
python -m pytest tests/ -v
```

Suite berisi **24 unit test** untuk logika murni:

| Modul | Jumlah | Skenario yang diuji |
|---|---|---|
| `LineCounter` | 10 | Masuk, keluar, bergoyang di garis (cooldown), tetap di satu sisi, tepat di atas garis, dua orang bersamaan, bolak-balik, pembersihan ID lama |
| `QueueMonitor` | 14 | Di bawah dan di atas ambang, orang di luar zona, zona kosong, alert panjang dan lama, cooldown alert, ID hilang sesaat, status terkini |

Bagian deteksi YOLO dan dashboard diverifikasi manual dengan video. Catat hasil akurasi (hitungan manual vs sistem) di `docs/evaluasi.md`.

---

## 📁 Struktur Proyek

```text
Project_CCTV_Deteksi_Orang/
├── monitor.py                 # Program utama: YOLOv8 + ByteTrack + overlay
├── line_counter.py            # Logika murni garis virtual IN/OUT
├── queue_monitor.py           # Logika murni antrean & waktu tunggu
├── db.py                      # Akses SQLite (visits, queue_samples, events)
├── notifier.py                # Notifikasi Telegram
├── simulate.py                # Generator data simulasi
├── dashboard.py               # Dashboard Streamlit
├── config.json                # Parameter: sumber video, garis, zona, ambang
├── requirements.txt           # Dependensi Python
├── AGENTS.md                  # Aturan dan konvensi untuk AI agent
├── DESIGN.md                  # Sistem desain visual dashboard
│
├── flowtask-dashboard/        # Web dashboard (HTML, CSS, JS)
│   ├── index.html
│   ├── css/style.css
│   ├── js/app.js              # Grafik SVG, filter persentil, simulasi
│   ├── js/cctv_data.js        # Data yang diekspor dari data.db
│   └── README.md
│
├── tests/                     # Unit test
├── samples/                   # Video uji lokal (tidak di-commit) + SOURCES.md
└── docs/                      # Catatan evaluasi (evaluasi.md)
```

---

## 🔒 Privasi & Keamanan

- **Anonim.** Sistem hanya mendeteksi keberadaan orang. Tidak ada pengenalan wajah, identifikasi personal, atau estimasi usia/gender. ID pelacak bersifat sementara dan tidak disimpan ke database.
- **Kredensial aman.** Password RTSP, token Telegram, dan chat ID tidak ditanam di kode dan tidak di-commit.
- **Area publik saja.** Hanya untuk pintu masuk, lobi, dan zona kasir. Jangan dipakai di area privat (kamar, toilet, ruang ganti).
- **Metrik agregat.** Laporan berupa jumlah, rata-rata, dan jam sibuk, bukan penilaian per orang.
- **Kepatuhan.** Pasang pemberitahuan CCTV dan perhatikan UU Pelindungan Data Pribadi (UU PDP) bila dipakai di tempat usaha. Minta persetujuan peserta untuk rekaman uji.

---

## ⚠️ Batasan yang Diketahui

- Orang yang saling menutupi atau terhalang bisa terhitung kurang, dan ID pelacak kadang tertukar.
- Sudut kamera dari atas dan miring ke arah pintu paling akurat; dari samping lebih sulit.
- Mode malam (infrared) menurunkan akurasi deteksi.
- Stream WiFi 2.4GHz bisa putus-putus; gunakan kabel jika memungkinkan.
- Hasil pada video uji publik belum tentu sama pada kamera BARDI di lokasi nyata.
- Saran jam sibuk baru bermakna setelah data beberapa hari atau akhir pekan terkumpul.

---

## 🗺️ Roadmap

- [x] Penghitung pengunjung (garis virtual)
- [x] Pemantau antrean dan alert Telegram
- [x] Dashboard Streamlit dan web, simulasi data
- [ ] Okupansi meja dan durasi duduk
- [ ] Ringkasan harian otomatis untuk manajer
- [ ] Funnel pengunjung (masuk, duduk, ke kasir)
- [ ] Alat bantu menggambar garis dan zona dari screenshot
- [ ] Evaluasi akurasi pada rekaman kamera nyata

---

## 🤝 Kontribusi

Proyek ini berupa prototipe magang, tetapi masukan sangat diterima. Sebelum mengubah kode, baca `AGENTS.md` untuk aturan arsitektur (modul logika harus murni) dan konvensi. Jalankan `python -m pytest tests/` dan `python -m py_compile *.py` sebelum mengirim perubahan.

---

## 📄 Lisensi

Dibuat untuk keperluan magang dan edukasi. Gunakan dan kembangkan sesuai kebutuhan internal. Jika repositori akan dipublikasikan, tambahkan berkas `LICENSE` (mis. MIT) dan periksa lisensi video serta dataset uji yang dipakai.

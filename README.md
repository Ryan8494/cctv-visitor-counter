# VisionCCTV — Sistem Pemantauan Pintu Masuk & Antrean

Sistem pemantauan pengunjung dan manajemen antrean berbasis **Computer Vision (YOLOv8 + ByteTrack)** yang dirancang untuk restoran atau lobi hotel. Proyek ini memantau pintu masuk secara otomatis, melacak antrean kasir, menghitung durasi waktu tunggu, memberikan peringatan (*alert*) via Telegram, serta menyediakan analisis jam sibuk dan saran penambahan staf melalui dashboard interaktif.

---

## 📌 Ringkasan Fitur

1. **Penghitung Pengunjung Masuk/Keluar (*Virtual Line Counter*)**:
   - Mendeteksi dan menghitung orang melintasi garis virtual pintu masuk (`IN` dan `OUT`).
   - Penentuan arah berbasis *cross-product* vektor posisi tengah bounding box.
   - Dilengkapi *cooldown* dan histeresis per ID pelacak agar orang yang berdiri/bergoyang dekat garis tidak terhitung berulang.

2. **Manajemen Antrean & Waktu Tunggu (*Queue Zone Monitor*)**:
   - Memantau zona poligon kasir/check-in menggunakan algoritma *point-in-polygon*.
   - Mencatat waktu masuk tiap ID pelacak untuk menghitung durasi tunggu (*wait time*).
   - Fitur *lost grace period* (toleransi 3 detik) agar ID yang hilang sesaat karena oklusi tidak langsung dianggap pergi.
   - Peringatan otomatis:
     - `ALERT_ANTREAN_PANJANG`: Jumlah orang di zona antrean $\ge$ batas (default: 5 orang).
     - `ALERT_TUNGGU_LAMA`: Terdapat orang yang menunggu $\ge$ batas waktu (default: 120 detik).
   - Cooldown alert untuk mencegah spam notifikasi tiap frame.

3. **Notifikasi Alert Telegram**:
   - Terintegrasi dengan bot Telegram untuk mengirim pesan alert instan saat antrean penuh atau waktu tunggu melewati ambang.
   - Token bot dan Chat ID diamankan melalui variabel lingkungan (*environment variables*).

4. **Dashboard Manajer (2 Pilihan Antarmuka)**:
   - **Modern Web Dashboard (`flowtask-dashboard/`)**: Desain *soft SaaS* interaktif, visualisasi CCTV real-time, grafik per jam, **slider persentil jam sibuk akhir pekan**, dan **rekomendasi cerdas penambahan pegawai**.
   - **Streamlit Dashboard (`dashboard.py`)**: Dashboard Python interaktif untuk analisis tren dan pelaporan data SQLite.

5. **Simulasi Data Realistis (`simulate.py`)**:
   - Generator data buatan untuk mengisi database SQLite (`data.db`) selama 4 minggu dengan pola jam makan dan akhir pekan yang realistis untuk pengujian dashboard.

---

## 🏗️ Arsitektur & Alur Data

```mermaid
flowchart TD
    A["Sumber Video / RTSP Camera"] --> B["monitor.py"]
    B --> C["Deteksi YOLOv8 (Kelas Person)"]
    C --> D["Pelacak ByteTrack (ID Konsisten)"]
    D --> E["line_counter.py (Logika Garis)"]
    D --> F["queue_monitor.py (Logika Antrean)"]
    E -->|"Lintasan IN / OUT"| G["db.py (SQLite: visits)"]
    F -->|"Sampel Antrean & Tunggu"| H["db.py (SQLite: queue_samples)"]
    F -->|"Alert Pemicu"| I["db.py (SQLite: events)"]
    I --> J["notifier.py (Telegram Bot)"]
    G --> K["Dashboard Manajer"]
    H --> K
    I --> K
    K --> L["Web Dashboard (flowtask-dashboard/)"]
    K --> M["Streamlit Dashboard (dashboard.py)"]
```

---

## 📷 Batasan Perangkat Keras

* **Kamera Target**: **BARDI Smart Indoor PTZ IP Camera** (WiFi 2.4GHz, indoor).
* **Protokol**: **ONVIF** & **RTSP Stream**. URL RTSP diperoleh menggunakan tool seperti *ONVIF Device Manager (ODM)*.
* **Codec Disarankan**: H.264 (sub-stream resolusi rendah, misal 640x360 atau 1080p sub-stream) untuk komputasi OpenCV yang ringan dan stabil.
* **Kunci Posisi PTZ**: Posisi kamera **wajib dikunci** (tidak digeser/dirotasi) agar koordinat garis hitung virtual dan poligon antrean tetap akurat.

---

## 📁 Struktur Berkas

```text
Project_CCTV_Deteksi_Orang/
├── AGENTS.md                  # Panduan aturan, batasan arsitektur & konvensi kode
├── DESIGN.md                  # Sistem desain visual dan token UI dashboard
├── README.md                  # Dokumentasi proyek (berkas ini)
├── config.json                # Konfigurasi parameter (RTSP, koordinat garis & zona, ambang)
├── requirements.txt           # Daftar dependensi library Python
├── .gitignore                 # Mengabaikan data.db, file video, kredensial, & cache
│
├── monitor.py                 # Program utama deteksi CCTV (YOLOv8 + ByteTrack + Overlay)
├── line_counter.py            # Logika murni penghitung garis virtual IN/OUT
├── queue_monitor.py           # Logika murni pemantau antrean & waktu tunggu
├── db.py                      # Akses SQLite (skema tabel: visits, queue_samples, events)
├── notifier.py                # Pengirim notifikasi alert via Telegram Bot
├── simulate.py                # Pembuat data simulasi realistis ke data.db
├── dashboard.py               # Dashboard analisis manajer berbasis Streamlit
│
├── flowtask-dashboard/        # Modern Web Dashboard (HTML5, CSS3, JS)
│   ├── index.html             # Tampilan utama web dashboard
│   ├── css/style.css          # Desain soft SaaS, responsive grid, animations
│   ├── js/app.js              # Engine rendering chart SVG, filter persentil, dan simulasi
│   ├── js/cctv_data.js        # Dataset riil yang diekspor dari data.db
│   └── README.md              # Dokumentasi khusus web dashboard
│
├── tests/                     # Suite pengujian unit (24 test otomatis)
│   ├── test_line_counter.py   # Uji kasus lintasan masuk, keluar, cooldown, bolak-balik
│   └── test_queue_monitor.py  # Uji antrean di bawah/atas ambang, wait time, grace period
│
├── samples/                   # Folder video uji lokal (masuk .gitignore)
│   └── SOURCES.md             # Catatan sumber & lisensi video uji
│
└── docs/                      # Dokumen evaluasi & catatan pengujian
    └── evaluasi.md            # Format pencatatan akurasi manual vs sistem
```

---

## 🛠️ Instalasi & Persiapan

### 1. Prasyarat
* Python 3.10 atau versi lebih baru.
* Git.

### 2. Kloning & Instal Dependensi
```bash
# Masuk ke direktori proyek
cd Project_CCTV_Deteksi_Orang

# Instal dependensi Python
pip install -r requirements.txt
```

---

## ⚡ Perintah Terminal Lengkap

| Perintah | Deskripsi |
|---|---|
| `python -m pytest tests/` | Menjalankan **24 unit test otomatis** untuk memastikan logika garis dan antrean 100% valid. |
| `python simulate.py` | Mengisi [data.db](data.db) dengan data simulasi realistis 4 minggu (28.656 kunjungan, 2.257 alert). |
| `python -m http.server 3000` | Menjalankan web server lokal untuk membuka **Web Dashboard Modern** di [http://localhost:3000](http://localhost:3000). |
| `streamlit run dashboard.py` | Menjalankan **Dashboard Streamlit** di [http://localhost:8501](http://localhost:8501). |
| `python monitor.py` | Menjalankan sistem deteksi video/CCTV real-time (tekan tombol **`q`** pada jendela video untuk keluar). |
| `python -m py_compile *.py` | Memeriksa integritas sintaks seluruh skrip Python. |

---

## ⚙️ Panduan Konfigurasi (`config.json`)

Semua parameter operasional diatur melalui file [config.json](config.json):

```json
{
    "source": "samples/contoh.mp4",

    "line": {
        "pt1": [300, 400],
        "pt2": [900, 400],
        "in_direction": "down"
    },

    "queue_zone": [
        [100, 300],
        [500, 300],
        [500, 600],
        [100, 600]
    ],

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

* **`source`**: Path file video lokal (misal `"samples/test.mp4"`) atau URL RTSP kamera BARDI (misal `"rtsp://admin:pass@192.168.1.100:554/live/ch0"`).
* **`line`**: Titik koordinat awal (`pt1`) dan akhir (`pt2`) garis virtual pintu masuk serta arah masuk (`down`/`positive` atau `up`/`negative`).
* **`queue_zone`**: Daftar titik poligon yang membentuk zona antrean kasir.
* **`queue_max_people`**: Ambang batas jumlah orang untuk memicu `ALERT_ANTREAN_PANJANG`.
* **`queue_max_wait_sec`**: Ambang batas waktu tunggu terlama (detik) untuk memicu `ALERT_TUNGGU_LAMA`.

---

## 🧪 Pengujian Unit (*Unit Testing*)

Proyek ini menerapkan prinsip **arsitektur logika murni** ([line_counter.py](line_counter.py) dan [queue_monitor.py](queue_monitor.py) tidak mengimpor OpenCV/YOLO), sehingga dapat diuji secara cepat dan independen tanpa kamera.

Jalankan pengujian:
```bash
python -m pytest tests/ -v
```

Hasil pengujian mencakup 24 kasus uji:
* **LineCounter (10 test)**: Lintasan masuk, lintasan keluar, bergoyang di garis dalam cooldown, tetap di satu sisi, tepat di atas garis, dua orang bersamaan, bolak-balik melintas, pembersihan ID lama (*cleanup*).
* **QueueMonitor (14 test)**: Antrean di bawah ambang, orang di luar zona, zona kosong, alert antrean panjang, alert waktu tunggu lama, verifikasi cooldown alert, toleransi ID hilang sesaat (*lost grace period*), status saat ini.

---

## 🔒 Privasi & Keamanan Data

* **Anonim & Tanpa Pengenalan Wajah**: Sistem ini hanya mendeteksi keberadaan objek kelas orang secara anonim. **Tidak ada fitur pengenalan wajah (*face recognition*)**, identifikasi personal, estimasi usia, atau gender. ID pelacak bersifat sementara dan tidak disimpan ke database.
* **Kredensial Aman**: Password kamera RTSP, token bot Telegram, dan Chat ID tidak ditanam di kode program, melainkan melalui variabel lingkungan yang tidak di-commit ke Git repository.
* **Area Publik Saja**: Sistem dirancang khusus untuk area umum (pintu masuk restoran, lobi hotel, zona kasir). Tidak boleh digunakan di area privat.

---

## 📄 Lisensi
Proyek ini dibuat untuk keperluan magang/edukasi prototipe pemantauan Computer Vision. Silakan gunakan dan kembangkan sesuai kebutuhan internal.

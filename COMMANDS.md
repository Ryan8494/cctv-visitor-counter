# COMMANDS.md — Panduan Perintah Terminal Proyek VisionCCTV

Dokumen ini merupakan panduan referensi cepat (*cheatsheet*) untuk seluruh perintah terminal yang dapat digunakan dalam proyek ini, lengkap dengan fungsi, opsi tambahan, dan contoh penggunaannya.

---

## ⚡ Ringkasan Cepat Perintah (Cheatsheet)

| Kategori | Perintah Terminal | Keterangan |
|---|---|---|
| **Setup** | `pip install -r requirements.txt` | Instal seluruh paket/library yang dibutuhkan |
| **Testing** | `python -m pytest tests/` | Jalankan 24 unit test otomatis |
| **Testing** | `python -m pytest tests/ -v` | Jalankan unit test dengan rincian per kasus uji |
| **Sintaks** | `python -m py_compile *.py` | Periksa error sintaks pada semua file Python |
| **Web Dashboard** | `python -m http.server 3000` | Jalankan Web Dashboard di [http://localhost:3000](http://localhost:3000) |
| **Streamlit** | `streamlit run dashboard.py` | Jalankan Streamlit Dashboard di [http://localhost:8501](http://localhost:8501) |
| **Simulasi Data** | `python simulate.py` | Isi database `data.db` dengan simulasi 4 minggu |
| **Deteksi CCTV** | `python monitor.py` | Jalankan deteksi orang YOLOv8 + ByteTrack (tekan `q` untuk keluar) |
| **Menu Interaktif**| `python menu.py` | Buka menu konsol interaktif untuk memilih perintah |

---

## 📦 1. Instalasi & Dependensi

Jalankan perintah ini sebelum memulai proyek atau saat berpindah ke komputer baru:

```bash
# Instal seluruh pustaka dependensi (Ultralytics, OpenCV, Streamlit, Pandas, Plotly, Pytest, dll.)
pip install -r requirements.txt

# Memastikan versi Python yang digunakan (disarankan Python 3.10+)
python --version

# Memeriksa daftar paket yang terinstal
pip list
```

---

## 🧪 2. Pengujian Logika & Validasi (Testing)

Proyek ini menerapkan arsitektur logika murni pada `line_counter.py` dan `queue_monitor.py` sehingga dapat diuji tanpa kamera atau model AI.

```bash
# Jalankan seluruh unit test
python -m pytest tests/

# Jalankan test dengan output detail (verbose)
python -m pytest tests/ -v

# Jalankan test khusus modul Penghitung Garis (LineCounter - 10 test)
python -m pytest tests/test_line_counter.py -v

# Jalankan test khusus modul Pemantau Antrean (QueueMonitor - 14 test)
python -m pytest tests/test_queue_monitor.py -v

# Periksa integritas sintaks seluruh file Python sekaligus
python -m py_compile *.py
```

---

## 📊 3. Menjalankan Dashboard Manajer

Tersedia dua opsi antarmuka dashboard:

### Opsi A: Modern Web Dashboard (HTML5, CSS3, JS) — *Rekomendasi*
Menampilkan 4 KPI, simulasi kamera BARDI PTZ, grafik per jam, analisis jam sibuk akhir pekan dengan slider persentil, dan rekomendasi penambahan staf:

```bash
# Jalankan web server lokal di port 3000
python -m http.server 3000
```
> **Akses di browser:** Buka alamat **[http://localhost:3000](http://localhost:3000)**  
> *(Atau klik ganda file `flowtask-dashboard/index.html` langsung dari File Explorer tanpa server).*

### Opsi B: Dashboard Streamlit (Python)
Menampilkan grafik Plotly dan pembacaan langsung dari database SQLite:

```bash
# Jalankan aplikasi Streamlit
streamlit run dashboard.py
```
> **Akses di browser:** Otomatis terbuka di **[http://localhost:8501](http://localhost:8501)**  
> *(Tekan `Ctrl + C` di terminal untuk menghentikan server Streamlit).*

---

## 🎲 4. Pembuat Data Simulasi (`simulate.py`)

Gunakan perintah ini untuk mengisi database `data.db` dengan pola kunjungan realistis (ramai saat jam makan siang dan makan malam serta lonjakan di akhir pekan):

```bash
# Isi data simulasi default (4 minggu ke belakang)
python simulate.py
```

Jika ingin membuat jumlah minggu tertentu secara kustom:
```bash
# Contoh membuat 2 minggu data simulasi
python -c "import simulate; simulate.simulate(num_weeks=2)"

# Contoh membuat 6 minggu data simulasi
python -c "import simulate; simulate.simulate(num_weeks=6)"
```

---

## 🎥 5. Menjalankan Deteksi CCTV & Pelacakan (`monitor.py`)

Program utama yang membaca video/RTSP, mendeteksi objek orang menggunakan **YOLOv8**, melacak pergerakan ID dengan **ByteTrack**, serta menghitung garis pintu dan zona antrean:

```bash
# Jalankan program deteksi utama
python monitor.py
```

> **Kontrol Jendela Video:**
> * Klik pada jendela video yang muncul (*"Monitor Pengunjung"*).
> * Tekan tombol **`q`** pada keyboard untuk menghentikan program dengan aman.
> * Sumber video/RTSP, garis virtual, dan zona diatur di file `config.json`.

---

## 🔍 6. Pemeriksaan Cepat Database SQLite

Perintah praktis sekali jalan (*one-liner*) untuk memeriksa data yang tersimpan di `data.db` tanpa aplikasi pihak ketiga:

```bash
# Periksa jumlah baris pada tabel visits, queue_samples, dan events
python -c "import sqlite3; conn = sqlite3.connect('data.db'); cur = conn.cursor(); print('Visits:', cur.execute('SELECT COUNT(*) FROM visits').fetchone()[0]); print('Queue Samples:', cur.execute('SELECT COUNT(*) FROM queue_samples').fetchone()[0]); print('Events:', cur.execute('SELECT COUNT(*) FROM events').fetchone()[0]); conn.close()"

# Lihat 5 event/alert terbaru
python -c "import sqlite3; conn = sqlite3.connect('data.db'); cur = conn.cursor(); [print(r) for r in cur.execute('SELECT ts, event, detail FROM events ORDER BY ts DESC LIMIT 5').fetchall()]; conn.close()"
```

---

## 📱 7. Pengaturan Variabel Lingkungan Telegram Bot

Untuk mengaktifkan pengiriman alert otomatis ke Telegram tanpa menulis token di dalam kode:

### Di PowerShell (Windows):
```powershell
# Set token bot dan chat ID untuk sesi terminal saat ini
$env:TELEGRAM_TOKEN="123456789:ABCdefGHIjklMNOpqrSTUvwxYZ"
$env:TELEGRAM_CHAT_ID="987654321"

# Verifikasi apakah variabel sudah terpasang
echo $env:TELEGRAM_TOKEN
echo $env:TELEGRAM_CHAT_ID
```

### Di Command Prompt (CMD Windows):
```cmd
set TELEGRAM_TOKEN=123456789:ABCdefGHIjklMNOpqrSTUvwxYZ
set TELEGRAM_CHAT_ID=987654321
```

---

## 🛠️ 8. Tips Troubleshooting

| Masalah | Penyebab Umum | Solusi Perintah |
|---|---|---|
| `No module named pytest` | Pytest belum terpasang | `pip install pytest` |
| `Port 3000 already in use` | Port 3000 sedang dipakai proses lain | Gunakan port lain: `python -m http.server 3001` |
| Video tidak muncul saat `monitor.py` | Path file salah di `config.json` | Pastikan file video ada di folder `samples/` dan path sesuai |
| Error `__pycache__ access denied` | Hak akses direktori terkunci | Normal pada sandbox, tidak mempengaruhi fungsionalitas kode |

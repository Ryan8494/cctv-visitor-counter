# COMMANDS.md — Panduan Perintah Terminal Proyek VisionCCTV

Dokumen ini merupakan panduan referensi cepat (*cheatsheet*) untuk seluruh perintah terminal yang dapat digunakan dalam proyek ini, lengkap dengan fungsi, opsi tambahan, dan contoh penggunaannya.

---

## ⚡ Ringkasan Cepat Perintah (Cheatsheet)

| Kategori | Perintah Terminal | Keterangan |
|---|---|---|
| **Setup** | `pip install -r requirements.txt` | Instal seluruh pustaka dependensi yang dibutuhkan |
| **Testing** | `python -m pytest tests/` | Jalankan **35 unit test otomatis** (Garis, Antrean, Meja, Ringkasan) |
| **Testing** | `python -m pytest tests/ -v` | Jalankan unit test dengan rincian per kasus uji |
| **Sintaks** | `python -m py_compile *.py` | Periksa integritas sintaks pada semua berkas Python |
| **Kalibrasi Zona** | `python tools/draw_zones.py samples/contoh.mp4` | Gambar garis pintu, zona kasir, dan meja ke `config.json` |
| **Uji Stream RTSP** | `python tools/test_stream.py [rtsp_url]` | Uji koneksi stream kamera BARDI (resolusi, FPS, codec) |
| **Simulasi Data** | `python simulate.py` | Isi database `data.db` dengan simulasi realistis 4 minggu |
| **Deteksi CCTV** | `python monitor.py` | Jalankan deteksi orang YOLOv8 + pelacakan 3 zona (tekan `q` untuk keluar) |
| **Streamlit** | `streamlit run dashboard.py` | Buka Dashboard Manajer Python di [http://localhost:8501](http://localhost:8501) |
| **Web Dashboard** | `python server.py` (atau `menu.py` opsi 3) | Buka Modern Web Dashboard di [http://localhost:3000](http://localhost:3000) |
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

## 🎨 2. Alat Kalibrasi Zona & Uji Kamera (Tools)

### A. Menggambar Zona Pintu, Kasir & Meja (`tools/draw_zones.py`)
Gunakan alat visual interaktif ini untuk menentukan letak koordinat zona pada video atau kamera:

```bash
# Buka video untuk kalibrasi zona
python tools/draw_zones.py samples/contoh.mp4
```

> **Tombol Navigasi Alat Gambar Zona:**
> * **`1`** : Mode Garis Pintu Masuk (Klik 2 titik untuk membuat garis virtual).
> * **`2`** : Mode Zona Kasir (Klik titik-titik poligon antrean, tekan **`c`** untuk menutup poligon).
> * **`3`** : Mode Poligon Meja Pengunjung (Klik 4 titik sudut per meja: Meja 1, Meja 2, dst.).
> * **`SPASI`** : Pause / Resume video pada posisi frame yang jelas.
> * **`s`** : **Simpan seluruh koordinat langsung ke `config.json`**.
> * **`d`** / **`Backspace`** : **Hapus / Undo** (membatalkan 1 titik terakhir yang diklik, atau menghapus garis/zona/meja aktif).
> * **`r`** : **Reset mode aktif** (menghapus seluruh elemen pada mode yang sedang dipilih).
> * **`q`** : Keluar dari alat kalibrasi.

### B. Pengujian Koneksi RTSP Kamera BARDI (`tools/test_stream.py`)
Mengecek apakah URL RTSP kamera terbaca lancar, memeriksa resolusi, FPS, codec, dan kestabilan 30 frame pertama:

```bash
# Uji stream dari URL RTSP kamera BARDI
python tools/test_stream.py rtsp://admin:password@192.168.1.50:554/live/ch0

# Atau uji stream dari sumber default yang tercatat di config.json
python tools/test_stream.py
```

---

## 🧪 3. Pengujian Logika & Validasi (Testing)

Proyek ini menerapkan arsitektur **logika murni (*pure logic*)** pada seluruh modul inti ([line_counter.py](line_counter.py), [queue_monitor.py](queue_monitor.py), [table_tracker.py](table_tracker.py), dan [summary.py](summary.py)), sehingga dapat diuji tanpa kamera atau model AI dalam hitungan milidetik:

```bash
# Jalankan seluruh 35 unit test otomatis
python -m pytest tests/

# Jalankan test dengan output detail (verbose)
python -m pytest tests/ -v

# Jalankan test khusus modul Penghitung Pintu Masuk (LineCounter - 10 test)
python -m pytest tests/test_line_counter.py -v

# Jalankan test khusus modul Pemantau Antrean Kasir (QueueMonitor - 16 test)
python -m pytest tests/test_queue_monitor.py -v

# Jalankan test khusus modul Okupansi Meja & Durasi Duduk (TableTracker - 5 test)
python -m pytest tests/test_table_tracker.py -v

# Jalankan test khusus modul Ringkasan Harian & Saran Staf (Summary - 4 test)
python -m pytest tests/test_summary.py -v

# Periksa integritas sintaks seluruh file Python sekaligus (harus exit code 0)
python -m py_compile *.py
```

---

## 🎥 4. Menjalankan Deteksi CCTV & Pelacakan (`monitor.py`)

Program utama yang memproses video/RTSP, mendeteksi orang dengan **YOLOv8**, melacak ID dengan **ByteTrack**, serta mengintegrasikan **tiga zona sekaligus**:
1. Garis pintu masuk (`LineCounter` $\to$ tabel `visits`)
2. Poligon antrean kasir (`QueueMonitor` $\to$ tabel `queue_samples` dan `queue_visits`)
3. Poligon meja pengunjung (`TableTracker` $\to$ tabel `table_sessions` dan `occupancy_samples`)

```bash
# Jalankan program deteksi utama
python monitor.py
```

> **Kontrol Jendela Video:**
> * Klik pada jendela video yang muncul (*"Monitor Restoran & Pengunjung"*).
> * Tekan tombol **`q`** pada keyboard untuk menghentikan program dengan aman.
> * Garis pintu ditandai warna hijau, zona kasir oranye, meja kosong berwarna hijau, dan meja terisi berwarna oranye.

---

## 📊 5. Menjalankan Dashboard Manajer

Tersedia dua opsi antarmuka dashboard:

### Opsi A: Dashboard Streamlit (Python)
Menampilkan metrik utama 3 zona, grafik persebaran pengunjung per jam, tren antrean kasir, grafik okupansi meja, serta **rekomendasi cerdas jadwal staf dari [summary.py](summary.py)**:

```bash
# Jalankan aplikasi Streamlit
streamlit run dashboard.py
```
> **Akses di browser:** Otomatis terbuka di **[http://localhost:8501](http://localhost:8501)**  
> *(Tekan `Ctrl + C` di terminal untuk menghentikan server Streamlit).*

### Opsi B: Modern Web Dashboard (HTML5, CSS3, JS)
Menampilkan desain *soft SaaS*, simulasi CCTV interaktif, KPI pengunjung, slider persentil jam sibuk, dan saran staf:

```bash
# Jalankan web server resmi VisionCCTV (port 3000)
python server.py
```
> **Akses di browser:** Otomatis membuka alamat **[http://localhost:3000](http://localhost:3000)**  
> *(Atau pilih opsi [3] di `python menu.py`, atau klik ganda `flowtask-dashboard/index.html` langsung dari File Explorer).*

---

## 🎲 6. Pembuat Data Simulasi (`simulate.py`)

Gunakan perintah ini untuk mengisi database `data.db` dengan pola kunjungan realistis (ramai saat jam makan siang dan makan malam serta lonjakan di akhir pekan) untuk **seluruh 6 tabel SQLite**:

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

## 🔍 7. Pemeriksaan Cepat Database SQLite

Perintah praktis sekali jalan (*one-liner*) untuk memeriksa data yang tersimpan di `data.db` tanpa aplikasi eksternal:

```bash
# Periksa jumlah baris pada seluruh 6 tabel sistem
python -c "import sqlite3; conn = sqlite3.connect('data.db'); cur = conn.cursor(); print('Visits Pintu      :', cur.execute('SELECT COUNT(*) FROM visits').fetchone()[0]); print('Sesi Meja         :', cur.execute('SELECT COUNT(*) FROM table_sessions').fetchone()[0]); print('Sampel Okupansi   :', cur.execute('SELECT COUNT(*) FROM occupancy_samples').fetchone()[0]); print('Sampel Antrean    :', cur.execute('SELECT COUNT(*) FROM queue_samples').fetchone()[0]); print('Kunjungan Kasir   :', cur.execute('SELECT COUNT(*) FROM queue_visits').fetchone()[0]); print('Total Alert       :', cur.execute('SELECT COUNT(*) FROM events').fetchone()[0]); conn.close()"

# Lihat 5 sesi duduk meja terbaru
python -c "import sqlite3; conn = sqlite3.connect('data.db'); cur = conn.cursor(); [print(r) for r in cur.execute('SELECT table_name, start_ts, end_ts, duration_sec FROM table_sessions ORDER BY start_ts DESC LIMIT 5').fetchall()]; conn.close()"

# Lihat 5 event/alert terbaru
python -c "import sqlite3; conn = sqlite3.connect('data.db'); cur = conn.cursor(); [print(r) for r in cur.execute('SELECT ts, event, detail FROM events ORDER BY ts DESC LIMIT 5').fetchall()]; conn.close()"
```

---

## 📱 8. Pengaturan Variabel Lingkungan Telegram Bot

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

## 🛠️ 9. Tips Troubleshooting

| Masalah | Penyebab Umum | Solusi Perintah |
|---|---|---|
| `No module named pytest` | Pytest belum terpasang | `pip install pytest` |
| `Port 3000 already in use` | Port 3000 sedang dipakai proses lain | Gunakan port lain: `python -m http.server 3001` |
| Video tidak muncul saat `monitor.py` | Path file salah di `config.json` | Pastikan file video ada di folder `samples/` dan path sesuai |
| Koordinat zona meleset | Resolusi kamera/video berubah | Jalankan ulang kalibrasi: `python tools/draw_zones.py` |
| Alert Telegram tidak masuk | Variabel lingkungan belum di-set | Cek dengan `echo $env:TELEGRAM_TOKEN` |

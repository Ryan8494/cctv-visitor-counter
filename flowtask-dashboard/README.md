# VisionCCTV Resto — Dashboard Pemantauan 3 Zona Berbasis CCTV

Website dashboard modern untuk sistem pemantauan restoran berbasis computer vision (1 kamera CCTV BARDI PTZ), mengadopsi sistem desain *modern SaaS* pada [DESIGN.md](../DESIGN.md) dan seluruh spesifikasi 3 zona fungsional pada [AGENTS.md](../AGENTS.md).

---

## 🎯 3 Zona Restoran yang Dipantau

1. **Pintu Masuk (Virtual Line Counter)**:
   - Menghitung orang masuk (IN) dan keluar (OUT) melintasi garis dua titik.
   - Histeresis posisi & cooldown ID untuk mencegah overcounting.
2. **Meja Pengunjung (Dining Table Tracker)**:
   - Poligon per meja (`Meja 1` & `Meja 2`).
   - Ambang durasi minimum duduk (`table_min_dwell_sec: 30s`) agar orang yang sekadar lewat tidak dicatat.
   - Toleransi deteksi hilang/oklusi (`leave_grace_sec: 20s`).
   - Pencatatan sesi duduk ke `table_sessions` dan rasio okupansi ke `occupancy_samples`.
3. **Antrean Kasir (Cashier Queue Monitor)**:
   - Poligon area antrean kasir.
   - Estimasi jumlah orang, waktu tunggu per orang, filter dwell (`queue_min_dwell_sec: 5s`), dan grace hilang (`lost_grace_sec: 3s`).
   - Alert otomatis: `ALERT_ANTREAN_PANJANG` (≥ 5 orang) dan `ALERT_TUNGGU_LAMA` (≥ 120 detik) dengan cooldown 60 detik.

---

## 📊 Fitur & Tampilan Dashboard Web

### 1. 5 Kartu KPI Utama (Data Riil SQLite)
- **Pengunjung Masuk (IN)**: 29.588 orang.
- **Pengunjung Keluar (OUT)**: 27.929 orang.
- **Okupansi Meja Resto**: 60.2% rata-rata terisi (10.509 sesi selesai • rata-rata 54.4 menit).
- **Rata-rata Antrean Kasir**: 3.4 orang (puncak 12 orang).
- **Total Alert Antrean**: 4.551 peringatan terkirim ke Telegram.

### 2. Live CCTV Feed & Virtual Zone Viewport (BARDI PTZ)
- Simulasi kamera BARDI Smart Indoor PTZ (ONVIF RTSP, 25 FPS, H.264).
- **3 Zona Tanpa Tumpang Tindih**:
  - Garis Pintu Masuk di sisi bawah.
  - Zona Antrean Kasir di sisi kiri atas dengan deteksi bounding box antrean (ID 104, 108, dsb).
  - Zona Meja Restoran (Meja 1 & Meja 2) di sisi kanan dengan status realtime (TERISI) dan pelacakan pengunjung duduk.
- HUD Watermark: Status ONVIF RTSP, FPS, Bitrate, dan Jam Live.
- Tombol **Simulasi Gerak** ByteTrack ID.

### 3. Distribusi & Funnel Alur Kunjungan (Donut Chart)
- Donut chart IN (51.4%) vs OUT (48.6%) mulai dari posisi 12 o'clock yang rapi.
- Ringkasan funnel 3 zona: Pintu Masuk (29.5k) → Sesi Meja (10.5k) → Kunjungan Kasir (9.9k) → Keluar (27.9k).

### 4. Status Antrean Kasir Real-time
- Gauge kapasitas zona kasir (4/5 orang - Status Waspada).
- Waktu tunggu terlama (85 detik dari ambang 120 detik).
- Toleransi ID hilang (`lost_grace_sec`: 3 detik) & cooldown alert (60 detik).
- Status Telegram Notifier tersambung.

### 5. Pemantauan Okupansi Meja Restoran (Section Baru)
- Kartu unit visual Meja 1 dan Meja 2: status keterisian, durasi duduk saat ini, total sesi tersimpan, dan rata-rata durasi pengunjung.
- Informasi aturan logika murni meja sesuai `AGENTS.md`.

### 6. Grafik Trafik Pengunjung per Jam (IN vs OUT)
- Dual bar chart membandingkan orang masuk (hijau) dan keluar (biru) per jam (08:00 – 21:00).
- Filter interaktif: Semua Hari, Akhir Pekan, dan Hari Kerja.

### 7. Tren Antrean & Waktu Tunggu (Perbaikan Bug Bar Tunggu)
- Dual bar chart lengkap: Bar oranye untuk Panjang Antrean (orang) dan Bar ungu untuk Waktu Tunggu (detik) berdampingan dengan tooltip presisi.

### 8. Analisis Jam Sibuk Akhir Pekan & Rekomendasi Staf
- Slider ambang persentil interaktif (P50 – P95, default rekomendasi P75).
- Menampilkan grafik jam sibuk dengan garis ambang persentil dinamis.
- Daftar rekomendasi penjadwalan staf otomatis (contoh: tambah 2–3 pegawai kasir/pelayan pada jam puncak 19:00–20:00).

### 9. Log Event & Alert Terkini
- Tabel riwayat 30 alert terkini dari database SQLite (`events`).
- Filter pencarian teks instan (live search).
- Badge status jenis event dan notifikasi Telegram.

### 10. Modal Konfigurasi Parameter (config.json)
- Menampilkan dan menyetel parameter Garis Pintu, Zona Kasir, Zona Meja, Ambang Alert, Cooldown, dan Model YOLOv8n / ByteTrack.

---

## 🛠️ Perbaikan Bug yang Dilakukan

1. **Bug Bar Waktu Tunggu**: Menambahkan elemen bar waktu tunggu (`.bar-wait`) berwarna ungu berdampingan dengan bar antrean oranye pada grafik tren kasir sehingga sesuai dengan legendanya.
2. **Bug Navigasi Anchor Sidebar**: Menghubungkan seluruh item navigasi sidebar (`#cctv-section`, `#visitors-section`, `#tables-section`, `#queue-section`, `#busy-hours-section`, `#alerts-section`) agar dapat melakukan *smooth scroll* ke posisinya secara presisi.
3. **Bug Filter Hari Statis**: Mengaktifkan dropdown filter hari agar memperbarui seluruh KPI, grafik, dan tabel secara dinamis antara "Semua Hari", "Akhir Pekan", dan "Hari Kerja".
4. **Bug Zona Tumpang-Tindih di CCTV Overlay**: Menata ulang posisi overlay sehingga garis pintu masuk berada di bawah dan tidak memotong zona antrean kasir, serta menambahkan zona meja restoran.
5. **Penambahan Fitur Meja**: Mengintegrasikan zona meja (okupansi dan durasi sesi) ke dalam KPI, denah visual CCTV, kartu status meja, dan konfigurasi sistem.
6. **Sinkronisasi Data SQLite**: Mengisi `cctv_data.js` dengan data riil lengkap 4 minggu dari `data.db` (57.517 kunjungan, 10.509 sesi meja, 4.551 alert).

---

## 🚀 Cara Menjalankan

### Cara 1: Menggunakan Launcher Interaktif menu.py (Disarankan)
```bash
python menu.py
# Pilih opsi [3] untuk menjalankan Web Dashboard (Port 3000)
```

### Cara 2: Menjalankan Local Web Server Manual
```bash
python -m http.server -d flowtask-dashboard 3000
```
Buka browser di: **http://localhost:3000**

### Cara 3: Buka Langsung File HTML di Browser
Buka file [index.html](file:///C:/Users/ryan/.vscode/Project_CCTV_Deteksi_Orang/flowtask-dashboard/index.html) langsung di peramban web (Google Chrome, Microsoft Edge, dll).

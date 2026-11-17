# VisionCCTV — Dashboard Pemantauan Pintu Masuk & Antrean

Website dashboard modern untuk sistem pemantauan pintu masuk dan antrean restoran/hotel berbasis computer vision, mengadopsi sistem desain *soft SaaS* pada [DESIGN.md](../DESIGN.md) dan seluruh fitur fungsional pada [AGENTS.md](../AGENTS.md).

---

## 🎯 Fitur yang Disesuaikan dengan Proyek

### 1. 4 Kartu KPI Utama (Data Riil SQLite)
- **Pengunjung Masuk (IN)**: 14.684 orang (melintasi garis virtual pintu masuk).
- **Pengunjung Keluar (OUT)**: 13.972 orang (melintasi garis virtual ke arah luar).
- **Okupansi Saat Ini**: +712 orang diperkirakan berada di dalam restoran.
- **Rata-rata Antrean Kasir**: 3.4 orang (puncak 12 orang, ambang batas 5 orang).
- **Total Alert Antrean**: 2.257 peringatan (`ALERT_ANTREAN_PANJANG` & `ALERT_TUNGGU_LAMA`) terkirim ke Telegram.

### 2. Live CCTV Feed & Virtual Zone Viewport (BARDI PTZ)
- Simulasi kamera BARDI Smart Indoor PTZ (ONVIF RTSP, 25 FPS, H.264).
- Garis virtual pintu masuk (`pt1: [300, 400]` ke `pt2: [900, 400]`) dengan penanda arah IN (bawah) dan OUT (atas).
- Poligon zona antrean kasir (`[100, 300]` s.d. `[500, 600]`) dengan bounding box deteksi orang dan ID pelacak ByteTrack.
- Tombol simulasi gerak pelacakan ID objek.

### 3. Distribusi Kunjungan (Donut Chart)
- Perbandingan persentase Pengunjung Masuk (51.2%) vs Pengunjung Keluar (48.8%).
- Total 28.656 lintasan terdata.

### 4. Status Antrean Kasir Real-time
- Kapasitas zona antrean saat ini (4/5 orang - Status Waspada).
- Waktu tunggu terlama (85 detik dari ambang 120 detik).
- Toleransi ID hilang (`lost_grace_sec`: 3 detik) & cooldown alert (60 detik).
- Integrasi notifikasi Telegram aktif.

### 5. Trafik Pengunjung per Jam (IN vs OUT)
- Dual bar chart membandingkan orang masuk dan keluar per jam (08:00 – 21:00).
- Memperlihatkan lonjakan jam makan siang (11:00–14:00) dan jam makan malam (18:00–21:00).

### 6. Tren Antrean & Rata-rata Waktu Tunggu
- Grafik rata-rata orang di antrean kasir per jam.
- Waktu tunggu maksimum per jam.

### 7. Analisis Jam Sibuk Akhir Pekan & Rekomendasi Penjadwalan Pegawai
- Sesuai logika resmi di `AGENTS.md` & `dashboard.py`:
  - Fokus 8 hari akhir pekan (Sabtu & Minggu).
  - Jam dianggap sibuk jika rata-rata pengunjung ≥ persentil (default P75) ATAU ada ≥ 2 alert antrean.
  - Slider persentil ambang interaktif (P50 – P95).
  - **Saran Penambahan Pegawai Otomatis**:
    - *Pukul 12:00–13:00*: rata-rata 74 pengunjung, 148 alert → Tambah 2 pegawai kasir.
    - *Pukul 13:00–14:00*: rata-rata 69 pengunjung, 136 alert → Tambah 1–2 pegawai.
    - *Pukul 18:00–19:00*: rata-rata 69 pengunjung, 104 alert → Tambah 1–2 pegawai.
    - *Pukul 19:00–20:00*: rata-rata 99 pengunjung, 167 alert → Puncak Tertinggi: Tambah 2–3 pegawai kasir/pelayan.
    - *Pukul 20:00–21:00*: rata-rata 76 pengunjung, 146 alert → Tambah 2 pegawai.

### 8. Log Event & Alert Terkini
- Tabel riwayat 30 alert terkini dari database SQLite (`events`).
- Menampilkan waktu, badge tipe event (`ALERT_ANTREAN_PANJANG` / `ALERT_TUNGGU_LAMA`), detail kejadian, dan status terkirim ke Telegram.
- Pencarian teks instan (live search).

### 9. Modal Konfigurasi Parameter (config.json)
- Menampilkan parameter garis virtual, zona antrean, ambang orang, ambang waktu tunggu, cooldown, model YOLO, dan pelacak ByteTrack.

---

## 🚫 Fitur yang Telah Dihapus (Tidak Relevan dengan CCTV)
1. ❌ **Kanban Board Proyek** — dihapus karena tidak berhubungan dengan pemantauan kamera & pengunjung.
2. ❌ **Kartu Upgrade to Pro** — dihapus karena ini prototipe internal/magang.
3. ❌ **Menu Proyek PM** (*Tasks, Time Tracking, Clients, Documents, Sprint Planning*).
4. ❌ **Task Card Mockups** (*Redesign user onboarding, API specification, etc.*).

---

## 🚀 Cara Menjalankan

### Cara 1: Buka Langsung File HTML di Browser
Buka file [index.html](file:///C:/Users/ryan/.vscode/Project_CCTV_Deteksi_Orang/flowtask-dashboard/index.html) langsung di browser Anda (Google Chrome, Microsoft Edge, dll).

### Cara 2: Menjalankan Local Web Server
```bash
python -m http.server 3000
```
Buka browser di: **http://localhost:3000**

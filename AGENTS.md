# AGENTS.md

Panduan untuk AI agent yang bekerja di repositori ini. Baca seluruhnya sebelum mengubah kode, lalu lihat `TODO.md` untuk urutan kerja.

## Ringkasan proyek

**Asisten manajer restoran berbasis CCTV.** Proyek magang (prototipe/demo, bukan produksi). Sistem **membantu** keputusan manajer dengan data dan peringatan; sistem **tidak menggantikan** manajer.

Satu kamera mengarah ke area yang mencakup tiga jenis zona:

1. **Pintu masuk**: garis virtual untuk menghitung orang masuk/keluar.
2. **Meja pengunjung**: poligon per meja untuk okupansi dan durasi duduk.
3. **Kasir**: poligon untuk antrean dan waktu tunggu.

Keluaran utama: jam sibuk (terutama akhir pekan), okupansi meja, antrean kasir, alert, dan **ringkasan harian untuk manajer** berisi saran penjadwalan pegawai.

## Prioritas fitur

| Prioritas | Fitur | Zona | Status wajib |
|---|---|---|---|
| 1 | Penghitung pengunjung dan jam sibuk | Garis pintu | Inti |
| 2 | Okupansi meja dan durasi duduk | Poligon meja | Inti |
| 3 | Antrean kasir (jumlah orang, waktu tunggu, alert) | Poligon kasir | Inti |
| 4 | Ringkasan harian + saran staf | Semua data | Inti |
| 5 | Funnel (masuk, duduk, sampai kasir) | Gabungan | Tambahan |
| 6 | Meja belum dilayani / meja kotor | Poligon meja + pembeda pelayan | Tambahan (rapuh) |

Kerjakan sesuai urutan. Jangan mulai fitur 5 dan 6 sebelum fitur 1 sampai 4 berjalan dan teruji.

## Batasan perangkat (WAJIB dipatuhi)

- Kamera: **BARDI Smart Indoor PTZ IP Camera** (WiFi 2.4GHz, indoor). Pengguna menyatakan kamera **mendukung ONVIF**.
- **Kamera tidak boleh diganti** dan jangan menyarankan penggantian sebagai syarat agar proyek berjalan. Hanya **satu kamera**.
- URL RTSP didapat lewat ONVIF (`GetStreamUri`) atau ONVIF Device Manager. **Jangan menebak URL RTSP.** Akun ONVIF bisa berbeda dari akun aplikasi. Simpan di `config.json` (tidak di-commit).
- Yang masih harus dicek pada kamera nyata: codec (H.264 lebih aman dari H.265 untuk OpenCV), resolusi/fps sub-stream, kestabilan WiFi.
- PTZ harus **dikunci** pada satu posisi dan fitur patroli otomatis dimatikan, kalau tidak semua zona meleset.
- Pengembangan awal memakai **file video uji**. Pindah ke stream kamera setelah URL terverifikasi.

## Struktur berkas (rencana)

| Berkas | Fungsi |
|---|---|
| `monitor.py` | Program utama: baca video, deteksi + pelacakan orang, panggil modul logika, simpan data |
| `line_counter.py` | Logika murni garis masuk/keluar |
| `queue_monitor.py` | Logika murni antrean kasir (jangan beri nama `queue.py`, bentrok dengan modul bawaan Python) |
| `table_tracker.py` | Logika murni okupansi meja dan sesi duduk |
| `summary.py` | Logika murni pembuat ringkasan harian dan saran staf |
| `db.py` | Akses SQLite |
| `notifier.py` | Notifikasi Telegram |
| `dashboard.py` | Dashboard Streamlit (hanya membaca database) |
| `simulate.py` | Pembuat data simulasi |
| `tools/test_stream.py` | Uji URL RTSP/ONVIF (frame terbaca, codec, resolusi, fps) |
| `tools/draw_zones.py` | Gambar garis dan zona dari screenshot, simpan ke `config.json` |
| `tools/frames_to_video.py` | Ubah folder frame (mis. MOT17) jadi MP4 |
| `config.example.json` | Contoh konfigurasi tanpa rahasia |
| `tests/` | Uji logika murni |
| `samples/` | Video uji (tidak di-commit) + `SOURCES.md` |
| `docs/` | `evaluasi.md`, `arsitektur.md`, `privasi.md` |

Dokumen ini ditulis sebelum kode ada. Jika kode berbeda dari dokumen, **kode adalah sumber kebenaran**: perbarui dokumen ini.

## Perintah

```bash
pip install -r requirements.txt
python -m pytest tests/             # uji logika murni
python tools/test_stream.py         # cek stream kamera
python monitor.py                   # jalankan deteksi
streamlit run dashboard.py          # jalankan dashboard
python simulate.py                  # isi database dengan data simulasi
python -m py_compile *.py           # cek sintaks
```

## Arsitektur

```
video/RTSP -> YOLO (person) + pelacak (ByteTrack/BoT-SORT, ID konsisten)
           -> LineCounter   (pintu)   -> visits
           -> TableTracker  (meja)    -> table_sessions, occupancy_samples
           -> QueueMonitor  (kasir)   -> queue_samples, queue_entries, alert
           -> SQLite -> dashboard + summary.py -> ringkasan harian (Telegram)
```

Pelacakan memakai fitur tracking Ultralytics (`model.track(..., persist=True)`). Cek dokumentasi versi terpasang untuk parameter terbaru.

### Aturan modul logika

- `line_counter.py`, `queue_monitor.py`, `table_tracker.py`, `summary.py` **murni logika**: dilarang mengimpor cv2, ultralytics, atau mengakses kamera/jaringan/database. Input berupa ID, posisi, waktu; output berupa event atau angka.
- Waktu diteruskan sebagai argumen `now` (detik). Jangan memanggil `time.time()` di modul logika. Untuk file video, `now = frame_idx / fps`.
- Impor berat dilakukan di dalam fungsi di `monitor.py`.
- Setiap alert punya **cooldown** agar tidak berulang tiap frame.

### Pintu (`line_counter.py`)

- Garis dua titik di konfigurasi. Arah dari tanda perkalian silang posisi sebelum dan sesudah.
- Satu ID dihitung sekali per lintasan. Gunakan histeresis/cooldown agar orang yang bergoyang di garis tidak terhitung berulang.
- Arah "masuk" ditentukan di konfigurasi, bukan di kode.

### Meja (`table_tracker.py`)

- Poligon per meja. Status dasar: `KOSONG` dan `TERISI`.
- **Aturan sesi duduk**:
  1. Orang terdeteksi di dalam poligon meja.
  2. **Ambang minimum durasi (`min_dwell_sec`, mis. 30–60 detik)**: Orang yang hanya lewat dekat meja atau berhenti sebentar tidak dicatat sebagai sesi duduk. Status meja berubah ke `TERISI` dan sesi dicatat hanya jika orang berada di meja $\ge min\_dwell\_sec$.
  3. **Toleransi deteksi hilang (`leave_grace_sec`, mis. 20–30 detik)**: Jika orang terhalang sesaat oleh pelayan/pengunjung lain, status tetap `TERISI` dan sesi tidak terputus.
  4. **Pencatatan sesi (`table_sessions`)**: Saat orang benar-benar pergi (hilang $> leave\_grace\_sec$), sesi duduk disimpan ke `table_sessions(table_name, start_ts, end_ts, duration_sec)`.
- Fitur tambahan (prioritas 6): status `KOTOR`, alert belum dilayani, alert belum dibersihkan, dengan pembeda pelayan lewat warna seragam atau model klasifikasi. Rapuh; jangan dijadikan syarat fitur inti.

### Kasir (`queue_monitor.py`)

- Poligon kasir.
- **Aturan 1–4 pemantauan antrean**:
  1. **Masuk zona**: Saat ID terdeteksi di dalam poligon kasir pertama kali, catat `waktu_masuk_zona`. Waktu tunggu per ID = `now - waktu_masuk_zona`.
  2. **Ambang minimum durasi (`min_dwell_sec`, mis. 5–10 detik)**: Orang yang hanya melintas cepat di zona kasir ($< min\_dwell\_sec$) tidak dihitung sebagai pengantre dan tidak disimpan ke `queue_visits`.
  3. **Toleransi hilang (`lost_grace_sec`, mis. 3 detik)**: Jika ID hilang sesaat ($< lost\_grace\_sec$), orang tetap dianggap di zona dan waktu tunggu berlanjut. Jika hilang $> lost\_grace\_sec$, orang dianggap selesai mengantre/pergi.
  4. **Pencatatan kunjungan antrean (`queue_visits`)**: Saat orang meninggalkan zona antrean (setelah melewati `lost_grace_sec`), jika total waktu tunggu $\ge min\_dwell\_sec$, simpan sesi ke `queue_visits(start_ts, end_ts, wait_sec)`.
- Alert: `ALERT_ANTREAN_PANJANG` (orang ≥ `queue_max_people`) dan `ALERT_TUNGGU_LAMA` (tunggu ≥ `queue_max_wait_sec`). Setiap alert memiliki cooldown agar tidak berulang tiap frame.

### Zona tidak boleh saling menimpa

Gambar zona pintu, kasir, dan meja agar tidak tumpang tindih. Jika orang berada di dua zona, tentukan aturan prioritas di konfigurasi dan uji.

### Funnel (tambahan)

Funnel = perbandingan **jumlah per zona**: masuk di pintu, sesi duduk di meja, kunjungan ke kasir. **Jangan** melacak satu orang lintas zona (rapuh dan menambah risiko privasi).

### Data (SQLite)

- `visits(ts, direction)`
- `table_sessions(table_name, start_ts, end_ts, duration_sec)`
- `occupancy_samples(ts, occupied, total)`
- `queue_samples(ts, people_in_zone, max_wait_sec)`
- `queue_visits(start_ts, end_ts, wait_sec)`
- `events(ts, event, detail)`

Format `ts`: `YYYY-MM-DD HH:MM:SS` (waktu lokal). ID pelacak bersifat sementara dan **tidak disimpan**. Jangan ubah nama tabel/kolom tanpa memperbarui `db.py`, `dashboard.py`, `simulate.py`, `summary.py`, dan tes.

### Ringkasan harian dan saran staf (`summary.py`)

- Input: angka agregat satu hari (pengunjung per jam, okupansi, antrean, jumlah alert). Output: teks Bahasa Indonesia.
- Dasar saran adalah **aturan berbasis angka** yang bisa diuji. Contoh: jam dengan pengunjung ≥ persentil 75 atau ≥ 2 alert antrean ditandai sibuk, lalu disarankan penambahan pegawai.
- Contoh keluaran: "Puncak pukul 12:00-13:00 (48 tamu), antrean terpanjang 6 orang pukul 19:10, rata-rata meja terisi 62%. Saran: tambah satu pelayan pukul 18:30-20:30."
- LLM boleh dipakai **opsional** untuk memperhalus bahasa, dengan syarat: hanya angka agregat yang dikirim (tidak ada video, gambar, atau data individu), pengguna menyetujui, dan angka tetap menjadi dasar. Tanpa persetujuan, gunakan templat teks.
- Tampilkan peringatan "data masih sedikit" bila kurang dari beberapa hari/akhir pekan.

## Metrik: tim dan proses, bukan individu

- Hitung dan laporkan metrik **tim/proses** (rata-rata waktu tunggu, okupansi, jam sibuk).
- **Dilarang** membuat skor atau peringkat per pelayan/karyawan. Itu berisiko tidak adil dan melanggar prinsip privasi proyek.
- Sistem adalah alat bantu keputusan. Teks ringkasan tidak boleh menyalahkan individu.

## Sumber video uji

- Dataset riset (periksa lisensi dan tautan terbaru): MOT17/MOT20 (CC BY-NC-SA 3.0, berupa frame JPEG, ubah ke MP4 dengan ffmpeg), Mall dataset (frame JPEG, frame rate di bawah 2 Hz sehingga kurang cocok untuk garis hitung). Keduanya hanya untuk riset non-komersial.
- Klip stok bebas royalti (Pexels, Pixabay): kata kunci "queue line", "checkout line", "hotel reception", "cafe counter", "lobby". Periksa lisensi tiap klip.
- Rekaman sendiri dengan persetujuan peserta (skenario terkontrol: tamu masuk, duduk, mengantre, pergi). Ini sumber terbaik untuk antrean dan meja.
- Simpan di `samples/` (masuk `.gitignore`). Catat sumber, lisensi, dan tanggal unduh di `samples/SOURCES.md`.
- Video dataset publik dipakai untuk uji garis dan pelacakan; video antrean/meja kemungkinan besar harus rekaman sendiri.

## Konvensi kode

- Python 3.10+, PEP 8.
- Semua parameter yang bisa disetel (zona, ambang, token, sumber video) ada di `config.json`. Tidak ada angka ajaib di kode.
- Komentar, nama event, dan teks antarmuka dalam **Bahasa Indonesia**.
- Perubahan kecil dan terfokus. Jangan merombak struktur tanpa diminta.

## Keamanan dan privasi

- **Jangan menaruh kredensial di kode atau di-commit**: kata sandi RTSP/ONVIF, token Telegram, chat ID. Gunakan variabel lingkungan atau berkas lokal di `.gitignore`.
- Jangan commit `*.db`, video, atau screenshot yang memuat wajah.
- Hanya area umum restoran. Jangan menambah fitur untuk area privat (toilet, ruang ganti).
- **Dilarang** menambah pengenalan wajah, atribut demografis (usia, gender), atau identifikasi individu.
- Jangan mengirim video atau gambar ke layanan cloud eksternal.
- Pasang pemberitahuan CCTV dan catat kebijakan penyimpanan di `docs/privasi.md` (UU PDP, persetujuan peserta uji).

## Pengujian

- `tests/test_line_counter.py`: melintas masuk, melintas keluar, berdiri dekat garis, dua orang bersamaan, ID bolak-balik.
- `tests/test_table_tracker.py`: sesi duduk normal, orang lewat dekat meja (< min_dwell_sec) tidak dicatat, deteksi hilang sesaat, pergi dan datang lagi, durasi benar.
- `tests/test_queue_monitor.py`: di bawah ambang, melewati ambang (alert sekali), waktu tunggu lama, cooldown, ID hilang sesaat, orang melintas (< min_dwell_sec) tidak dicatat ke queue_visits, sesi antrean lengkap disimpan ke queue_visits (start_ts, end_ts, wait_sec).
- `tests/test_summary.py`: jam sibuk terdeteksi, saran muncul, data sedikit memunculkan peringatan.
- Deteksi YOLO dan dashboard diverifikasi manual dengan video. Jangan menyatakan "berfungsi" sebelum dijalankan pada video nyata.
- Evaluasi akurasi: bandingkan hitungan manual dengan sistem pada tiap video uji, catat di `docs/evaluasi.md`.

## Batasan yang diketahui

1. Orang kecil di area meja jauh bisa kurang terdeteksi pada 1080p.
2. Orang yang terhalang (tiang, orang lain) bisa hilang.
3. **Tukar-ID (ID switch/swap)**: Saat orang berpapasan, berdiri sangat rapat dalam antrean kasir, atau saling menutupi (oklusi), pelacak dapat menukar ID antar orang atau memberikan ID baru. Akibatnya, durasi tunggu antrean atau sesi duduk meja bisa terpecah menjadi beberapa sesi lebih pendek, atau waktu tunggu tertukar antar individu.
4. Sudut dari samping menyulitkan garis hitung; sudut atas-miring paling baik.
5. Zona harus dikalibrasi ulang jika kamera bergeser.
6. Mode malam (infrared) menurunkan akurasi.
7. Hasil pada video publik tidak otomatis berlaku pada kamera BARDI.
8. Saran jam sibuk butuh data beberapa hari/akhir pekan agar bermakna.

## Yang harus dilakukan agent

- Kerjakan sesuai urutan `TODO.md`; centang item yang selesai dan catat yang tertunda.
- Jalankan uji dan `py_compile` sebelum menyatakan selesai.
- Jelaskan bagian yang belum bisa diuji (butuh video nyata/kamera); jangan mengklaim sudah berfungsi.
- Pertahankan konsistensi nama tabel dan event antar modul.
- Perbarui dokumen ini bila struktur atau perilaku berubah.
- Jika ragu soal kamera BARDI, lisensi video, atau privasi, tanyakan ke pengguna.

## Yang tidak boleh dilakukan agent

- Mengganti kamera atau menambah kamera sebagai syarat.
- Membuat skor/peringkat per individu.
- Menambah pengenalan wajah, atribut demografis, atau identifikasi individu.
- Mengirim video/gambar ke layanan eksternal, atau menambah dependensi berbayar tanpa persetujuan.
- Memakai video tanpa memeriksa lisensi, atau meng-commit video/database/kredensial.

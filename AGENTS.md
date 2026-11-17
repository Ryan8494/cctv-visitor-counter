# AGENTS.md

Panduan untuk AI agent yang bekerja di repositori ini. Baca seluruhnya sebelum mengubah kode.

## Ringkasan proyek

Sistem pemantauan pintu masuk dan antrean berbasis computer vision untuk restoran/hotel. Proyek magang (prototipe/demo, bukan produksi). Fitur:

1. **Penghitung pengunjung**: menghitung orang masuk dan keluar lewat garis virtual di pintu.
2. **Manajemen antrean**: memantau zona antrean (kasir/check-in). Peringatan jika jumlah orang atau waktu tunggu melewati batas.
3. **Dashboard manajer**: pengunjung per jam, tren antrean, jam sibuk akhir pekan, dan saran kapan menambah pegawai.

Proyek ini menggantikan ide sebelumnya (deteksi meja), yang diganti karena video uji yang sesuai sulit ditemukan. Ide ini dipilih karena video uji (orang berjalan, antre, lobi) mudah diperoleh.

## Status

Dokumen ini ditulis **sebelum kode dibuat**. Struktur berkas di bawah adalah rencana. Jika berkas belum ada, buat sesuai rencana. Jika kode di repositori berbeda dari dokumen ini, **kode adalah sumber kebenaran**: perbarui dokumen ini agar sesuai.

## Batasan perangkat (WAJIB dipatuhi)

- Kamera target: **BARDI Smart Indoor PTZ IP Camera** (WiFi 2.4GHz, indoor).
- **Kamera tidak boleh diganti** dengan merek/model lain. Jangan menyarankan penggantian kamera sebagai solusi utama.
- Pengguna menyatakan kamera ini **mendukung ONVIF**. URL RTSP didapat lewat ONVIF (`GetStreamUri`) atau alat seperti ONVIF Device Manager. **Jangan menebak URL RTSP**: alamat, port, jalur stream, dan akun ONVIF dapat berbeda dari akun aplikasi. Simpan hasilnya di `config.json` (`source`) dan jangan di-commit.
- `source` bisa berupa URL RTSP atau path file video. Pengembangan awal boleh memakai file video uji, lalu dipindah ke stream kamera setelah URL terverifikasi.
- Hal yang belum terkonfirmasi dan harus dicek pada kamera nyata: codec (H.264 lebih aman daripada H.265 untuk OpenCV), resolusi dan fps sub-stream, kestabilan WiFi 2.4GHz, serta akun ONVIF terpisah.
- Gunakan sub-stream resolusi rendah untuk deteksi bila tersedia agar beban komputasi ringan.
- PTZ harus dikunci pada satu posisi agar garis hitung dan zona tidak bergeser.

## Struktur berkas (rencana)

| Berkas | Fungsi |
|---|---|
| `monitor.py` | Program utama: baca video, deteksi + pelacakan orang, panggil modul logika, simpan data |
| `line_counter.py` | Logika murni penghitung garis masuk/keluar |
| `queue_monitor.py` | Logika murni zona antrean dan waktu tunggu (jangan beri nama `queue.py`, bentrok dengan modul bawaan Python) |
| `db.py` | Akses SQLite (skema dan fungsi simpan/baca) |
| `notifier.py` | Kirim notifikasi (Telegram) |
| `dashboard.py` | Dashboard Streamlit (hanya membaca database) |
| `simulate.py` | Pembuat data simulasi untuk mengisi dashboard |
| `config.json` | Parameter: sumber video, garis, zona, ambang, token |
| `tests/` | Uji logika tanpa kamera atau model |
| `requirements.txt` | Dependensi Python |

## Perintah

```bash
pip install -r requirements.txt
python -m pytest tests/             # uji logika murni
python monitor.py                   # jalankan deteksi
streamlit run dashboard.py          # jalankan dashboard
python simulate.py                  # isi database dengan data simulasi
python -m py_compile *.py           # cek sintaks
```

Jalankan uji setiap kali mengubah `line_counter.py` atau `queue_monitor.py`.

## Arsitektur

### Alur data

```
video -> YOLO (kelas person) + pelacak (ByteTrack/BoT-SORT, ID konsisten)
      -> LineCounter  -> event masuk/keluar
      -> QueueMonitor -> jumlah orang di zona, waktu tunggu tiap ID, alert
      -> SQLite       -> dashboard
```

Pelacakan memakai fitur tracking Ultralytics (`model.track(..., persist=True)`) agar tiap orang punya ID. Tanpa ID yang konsisten, penghitung dan waktu tunggu tidak valid. Periksa dokumentasi Ultralytics versi terpasang untuk parameter terbaru. Modul `solutions` bawaan Ultralytics boleh dipakai untuk prototipe cepat, tetapi logika yang perlu diuji tetap ditulis sendiri di modul murni.

### Penghitung garis (`line_counter.py`)

- Garis virtual didefinisikan dua titik `(x1, y1)-(x2, y2)` di konfigurasi.
- Arah ditentukan dari tanda perkalian silang posisi titik pusat orang sebelum dan sesudah frame. Satu ID dihitung **sekali per lintasan**; simpan posisi terakhir per ID.
- Beri tahu arah mana yang dihitung "masuk" lewat konfigurasi, jangan ditanam di kode.
- Orang yang berdiri dekat garis dan bergoyang tidak boleh terhitung berulang (gunakan histeresis atau cooldown per ID).

### Monitor antrean (`queue_monitor.py`)

- Zona antrean adalah poligon di konfigurasi.
- Tiap ID di dalam zona dicatat waktu masuknya, sehingga waktu tunggu = `now - waktu_masuk`.
- Toleransi deteksi hilang sesaat (`lost_grace_sec`) agar ID yang hilang beberapa frame tidak dianggap pergi.
- Alert:
  - `ALERT_ANTREAN_PANJANG`: jumlah orang di zona ≥ `queue_max_people`.
  - `ALERT_TUNGGU_LAMA`: ada orang menunggu ≥ `queue_max_wait_sec`.
- Setiap alert punya **cooldown** (`alert_cooldown_sec`) agar tidak mengirim notifikasi berulang tiap frame.

### Aturan untuk modul logika

- `line_counter.py` dan `queue_monitor.py` **murni logika**: tidak boleh mengimpor cv2, ultralytics, atau mengakses kamera/jaringan/database. Input berupa ID, posisi, dan waktu; output berupa event.
- Waktu diteruskan sebagai argumen `now` (detik). Jangan memanggil `time.time()` di dalam modul logika. Untuk file video, `now` dihitung dari `frame_idx / fps` agar uji pada video akurat.
- Impor berat (`cv2`, `ultralytics`) dilakukan di dalam fungsi di `monitor.py`.

### Data (SQLite)

- `visits(ts, direction)`: satu baris per orang masuk/keluar (`IN`/`OUT`).
- `queue_samples(ts, people_in_zone, max_wait_sec)`: sampel per menit (atau per N detik).
- `events(ts, event, detail)`: alert dan kejadian penting.

Format `ts`: `YYYY-MM-DD HH:MM:SS` (waktu lokal). Jangan ubah nama tabel/kolom tanpa memperbarui `db.py`, `dashboard.py`, `simulate.py`, dan tes.

### Analisis jam sibuk (`dashboard.py`)

- Fokus akhir pekan (Sabtu dan Minggu, `dayofweek >= 5`), dengan opsi memilih satu hari.
- Per jam: jumlah pengunjung masuk, rata-rata panjang antrean, dan jumlah alert antrean.
- Jam dianggap sibuk jika pengunjung per jam ≥ persentil yang dipilih (default persentil 75) **atau** ada ≥ 2 alert antrean pada jam itu. Ambang bisa digeser di UI.
- Teks saran dalam Bahasa Indonesia, contoh: "Pukul 19:00-20:00: rata-rata 62 pengunjung, 3 alert antrean. Tambah pegawai."
- Jangan menyimpulkan tren dari data yang kurang dari beberapa akhir pekan. Tampilkan peringatan "data masih sedikit" bila perlu.

## Sumber video uji

- Klip stok bebas royalti (misalnya Pexels, Pixabay): cari kata kunci seperti "people walking entrance", "queue line", "hotel lobby", "checkout line". **Periksa lisensi sebelum memakai.**
- Dataset riset pelacakan/penghitungan orang (misalnya MOT17/MOT20, Mall dataset): **periksa lisensi dan tautan terbaru**, biasanya hanya untuk riset/pendidikan.
- Rekaman sendiri dengan persetujuan peserta.
- Simpan video uji di `samples/` (masuk `.gitignore`). Catat sumber dan lisensi tiap klip di `samples/SOURCES.md`.
- Untuk evaluasi akurasi, hitung manual jumlah orang masuk/keluar pada klip uji lalu bandingkan dengan keluaran sistem. Simpan hasilnya di `docs/evaluasi.md`.

## Konvensi kode

- Python 3.10+, ikuti PEP 8.
- Semua parameter yang bisa disetel ada di `config.json`. Jangan menanam angka ajaib (ambang, koordinat, token) di kode.
- Komentar, nama event, dan teks antarmuka memakai **Bahasa Indonesia**. Nama variabel/fungsi konsisten dengan kode sekitarnya.
- Perubahan kecil dan terfokus. Jangan merombak struktur berkas tanpa diminta.

## Aturan keamanan dan privasi

- **Jangan menaruh kredensial di kode atau di-commit**: kata sandi RTSP, token Telegram, chat ID. Gunakan variabel lingkungan atau berkas lokal yang masuk `.gitignore`.
- Jangan commit `*.db`, video, atau screenshot yang memuat wajah orang.
- Sistem hanya menghitung dan melacak keberadaan orang secara anonim. **Jangan menambahkan pengenalan wajah atau identifikasi individu.** ID pelacak bersifat sementara dan tidak disimpan ke database.
- Hanya area umum (pintu masuk, lobi, kasir). Jangan menambahkan fitur untuk area privat (kamar, toilet, ruang ganti).
- Jika memakai rekaman sendiri, pastikan peserta memberi persetujuan dan jangan unggah ke repositori publik.

## Pengujian

Uji yang harus ada di `tests/`:

- `LineCounter`: orang melintas masuk, melintas keluar, berdiri dekat garis tanpa melintas, dua orang bersamaan, ID yang sama melintas bolak-balik.
- `QueueMonitor`: antrean di bawah ambang (tanpa alert), jumlah orang melewati ambang (alert sekali), waktu tunggu melewati batas, cooldown alert, ID hilang sesaat kurang dari `lost_grace_sec`.
- Bagian deteksi YOLO dan dashboard diverifikasi manual dengan video uji.
- Jangan menyatakan deteksi "berfungsi" sebelum dijalankan pada video nyata.

## Batasan yang diketahui

1. Orang yang berdempetan atau saling menutupi bisa terhitung kurang; ID bisa tertukar antar orang.
2. Sudut kamera dari samping menyulitkan penghitungan. Sudut dari atas dan miring ke arah pintu paling akurat.
3. Garis dan zona harus dikalibrasi ulang jika kamera bergeser.
4. Kamera indoor dengan resolusi 1080p dan lensa terbatas mencakup area kecil.
5. Mode malam (infrared) menurunkan akurasi deteksi.
6. Saran jam sibuk butuh data beberapa akhir pekan agar bermakna.
7. Video stok dan dataset bukan rekaman dari kamera BARDI; hasil pada video uji tidak otomatis berlaku pada kamera sungguhan.

## Ide pengembangan (backlog)

- Alat bantu menggambar garis dan zona dari screenshot (klik titik, simpan ke `config.json`).
- Heatmap area ramai.
- Okupansi area (jumlah orang di ruang makan saat ini).
- Ekspor laporan harian/mingguan (CSV/PDF).
- Dukungan lebih dari satu kamera.

## Yang harus dilakukan agent

- Jalankan uji dan `py_compile` sebelum menyatakan pekerjaan selesai.
- Jelaskan bagian yang belum bisa diuji (butuh video nyata atau kamera) dan jangan mengklaim sudah berfungsi.
- Pertahankan konsistensi nama tabel dan nama event antar modul.
- Perbarui dokumen ini bila struktur atau perilaku berubah.
- Jika ragu soal batasan kamera BARDI, lisensi video, atau privasi, tanyakan ke pengguna sebelum melanjutkan.

## Yang tidak boleh dilakukan agent

- Mengganti kamera atau menyarankan perangkat keras lain sebagai syarat agar proyek berjalan.
- Menambahkan pengenalan wajah, atribut demografis (usia, gender), atau identifikasi individu.
- Mengirim video atau data pengunjung ke layanan cloud eksternal.
- Menambahkan dependensi berbayar tanpa persetujuan.
- Memakai video tanpa memeriksa lisensi, atau meng-commit video ke repositori.

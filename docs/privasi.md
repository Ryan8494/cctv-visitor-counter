# Kebijakan Privasi & Etika Pemantauan CCTV (VisionCCTV)

Dokumen ini menjelaskan kepatuhan etika dan hukum perlindungan data pribadi (UU No. 27 Tahun 2022 tentang Pelindungan Data Pribadi / UU PDP) yang diterapkan dalam sistem **VisionCCTV**.

---

## 1. Prinsip Utama: *Privacy by Design*

Sistem ini dirancang semata-mata sebagai **alat bantu operasional dan efisiensi manajemen restoran**, bukan sebagai instrumen pengawasan individu (*individual surveillance*).

1. **Tanpa Pengenalan Wajah (*No Face Recognition*)**:
   - Sistem menggunakan model pendeteksi objek umum (YOLOv8 kelas `person`) yang hanya mendeteksi siluet tubuh manusia.
   - Sistem **tidak memindai, menyimpan, atau mengekstrak fitur biometrik wajah**.
2. **Tanpa Atribut Demografis Sensitif**:
   - Sistem tidak melakukan estimasi umur, jenis kelamin (*gender*), ras, atau ekspresi emosi.
3. **ID Pelacak Bersifat Sementara (*Volatile Tracking ID*)**:
   - ID pelacak (`track_id` dari ByteTrack) hanya hidup sementara di memori RAM selama objek berada dalam *frame* kamera.
   - **ID pelacak tidak pernah disimpan ke dalam database SQLite**.
4. **Fokus pada Metrik Proses, Bukan Penilaian Karyawan**:
   - Sistem mengukur performa proses (waktu tunggu antrean, okupansi meja, jam sibuk).
   - Dilarang keras membuat peringkat skor individu pegawai/pelayan.

---

## 2. Data yang Dikumpulkan & Disimpan

Sistem hanya mencatat data telemetri agregat ke dalam database lokal `data.db`:

| Tabel | Data yang Dicatat | Sifat Data |
|---|---|---|
| `visits` | Waktu (`ts`) dan arah pergerakan (`IN` / `OUT`) | Angka agregat anonim |
| `table_sessions` | Nama meja (`table_name`), waktu mulai, waktu selesai, durasi (detik) | Durasi pemakaian fasilitas |
| `occupancy_samples` | Waktu (`ts`), jumlah meja terisi, total meja | Rasio okupansi periodik |
| `queue_samples` | Waktu (`ts`), jumlah orang di antrean, waktu tunggu maksimum | Angka antrean periodik |
| `queue_visits` | Waktu mulai antre, waktu selesai antre, durasi tunggu (detik) | Durasi layanan kasir |
| `events` | Waktu (`ts`), jenis peringatan (misal `ALERT_ANTREAN_PANJANG`), pesan detail | Log sistem internal |

> **Catatan:** Rekaman video mentah (*raw footage*) atau tangkapan layar berwajah pengunjung **tidak disimpan** di database dan diabaikan dari repositori melalui berkas `.gitignore`.

---

## 3. Batasan Lokasi & Area Perekaman

- Kamera CCTV **hanya boleh dipasang di area umum restoran** (pintu masuk utama, meja makan pengunjung, dan area kasir).
- **Dilarang keras** mengarahkan kamera ke area privat seperti toilet, ruang ganti karyawan, musala, atau area istirahat pribadi.

---

## 4. Pemberitahuan kepada Pengunjung (*Transparency Notice*)

Sesuai ketentuan UU PDP, pengelola restoran wajib memasang tanda pemberitahuan visual di area pintu masuk:
> *"Area ini dipantau oleh kamera CCTV cerdas untuk kenyamanan, keselamatan, dan peningkatan kualitas pelayanan restoran."*

# DESIGN.md — FlowTask Project Dashboard

Dokumen ini mendeskripsikan sistem desain dan struktur UI dari dashboard manajemen proyek **FlowTask** (tagline: *"Plan. Track. Collaborate. Get Things Done."*). Nilai warna dan ukuran adalah estimasi dari gambar referensi dan dapat disesuaikan.

---

## 1. Ringkasan Desain

| Aspek | Deskripsi |
|---|---|
| Produk | FlowTask — aplikasi manajemen proyek & kolaborasi tim |
| Tipe layar | Dashboard web (desktop, sidebar kiri + konten utama) |
| Gaya visual | Modern, bersih, "soft SaaS" — kartu putih, sudut membulat, bayangan halus |
| Karakter | Ramah, profesional, ringan, banyak ruang kosong |
| Warna dominan | Biru (primer) dengan aksen hijau, oranye, ungu, merah |
| Mood | Produktif, tenang, terorganisir |

**Prinsip desain**
1. **Kejelasan data** — angka besar, label kecil, satu fokus per kartu.
2. **Kelembutan** — radius besar, shadow tipis, warna pastel untuk latar.
3. **Konsistensi** — satu keluarga warna biru; warna lain hanya untuk status/kategori.
4. **Skimmable** — ikon berwarna di dalam lingkaran/kotak untuk pengenalan cepat.

---

## 2. Design Tokens

### 2.1 Warna

**Brand & Netral**

| Token | Hex (estimasi) | Penggunaan |
|---|---|---|
| `--color-primary` | `#2563EB` | Judul aksen, tombol, item menu aktif, progress utama |
| `--color-primary-600` | `#1D4ED8` | Hover/pressed, bar "Completed" |
| `--color-primary-400` | `#6EA0F5` | Bar "In Progress", donut segmen kedua |
| `--color-primary-200` | `#C9D8F8` | Bar "Created", donut segmen "To Do" |
| `--color-primary-50` | `#EAF1FE` | Latar item menu aktif, kolom "In Progress" |
| `--color-text-strong` | `#0F1B3D` | Heading, angka KPI |
| `--color-text` | `#1F2A44` | Teks utama |
| `--color-text-muted` | `#6B7490` | Label sekunder, subjudul, caption |
| `--color-border` | `#E6EAF4` | Garis tipis, divider, border kartu |
| `--color-bg-app` | `#F5F7FD` | Latar halaman |
| `--color-surface` | `#FFFFFF` | Kartu, sidebar, header |

**Semantik / Status**

| Token | Hex | Penggunaan |
|---|---|---|
| `--color-success` | `#22C58B` | Tasks Completed, status Online, kolom Done, prioritas Low |
| `--color-warning` | `#F5A524` | Pending Tasks, prioritas Medium, status "In a meeting", Marketing Campaign |
| `--color-danger` | `#EF4444` | Prioritas High, tren negatif, notifikasi |
| `--color-info-purple` | `#7C5CE0` | Team Members, Mobile App Development |
| `--color-away` | `#8A93A8` | Status Away |

**Tint latar status (pastel)**

| Token | Hex | Penggunaan |
|---|---|---|
| `--tint-success` | `#E7F8F0` | Badge Online, kolom Done |
| `--tint-warning` | `#FEF4DC` | Badge Medium/In a meeting, kolom Review |
| `--tint-danger` | `#FDE8E8` | Badge High |
| `--tint-neutral` | `#EEF1F7` | Badge Away, kolom To Do |

**Gradient**
- Latar dekoratif: blob lavender-biru lembut (`#DCE6FF → #EFE9FF`) di pojok kiri-atas dan kanan-bawah, opasitas rendah.
- Kartu "Upgrade to Pro": `linear-gradient(135deg, #4F7CF3 0%, #3B5BE0 100%)`.

### 2.2 Tipografi

- **Font family:** sans-serif geometris modern (disarankan `Inter` atau `Plus Jakarta Sans`; fallback `system-ui, -apple-system, "Segoe UI", sans-serif`).
- **Heading hero:** ekstra bold, dua warna ("Project" navy, "Dashboard" biru).

| Token | Ukuran / Berat | Penggunaan |
|---|---|---|
| `display` | 48–56px / 800 | Judul hero "Project Dashboard" |
| `eyebrow` | 11–12px / 500, letter-spacing 0.3em, uppercase | "WORK SMARTER TOGETHER" |
| `h1` | 20–22px / 700 | "Good morning, Sarah!" |
| `h2` (card title) | 14px / 600 | Judul kartu (Project Progress, Tasks Overview, dll.) |
| `kpi` | 28–30px / 700 | Angka KPI (12, 186, 48, 8) |
| `kpi-center` | 28px / 700 | Total di tengah donut (248) |
| `body` | 13px / 400–500 | Isi daftar, nama item |
| `caption` | 11–12px / 400 | Label sekunder, jabatan, "vs last month" |
| `link` | 11–12px / 600, warna primer | "View All →", "View Calendar →" |
| `badge` | 10–11px / 500 | Prioritas, status |

### 2.3 Spacing (basis 4px)

`4 · 8 · 12 · 16 · 20 · 24 · 32`
- Padding kartu: **16–20px**
- Gap antar kartu: **16px**
- Gap dalam daftar (baris): **12–16px**

### 2.4 Radius

| Token | Nilai | Penggunaan |
|---|---|---|
| `--radius-sm` | 6px | Badge kecil |
| `--radius-md` | 10px | Input, item menu, kartu task kanban |
| `--radius-lg` | 16px | Kartu utama |
| `--radius-xl` | 24px | Container dashboard terluar |
| `--radius-full` | 999px | Avatar, ikon KPI, badge status, tombol pill |

### 2.5 Shadow

```css
--shadow-card: 0 2px 12px rgba(30, 50, 110, 0.06);
--shadow-float: 0 12px 32px rgba(30, 50, 110, 0.10);
```

---

## 3. Layout

```
┌──────────────────────────────────────────────────────────┐
│  Hero: eyebrow + judul + tagline (di luar app frame)     │
├───────────┬──────────────────────────────────────────────┤
│           │  Topbar: Search ........ 🔔  Avatar + Nama   │
│  Sidebar  ├──────────────────────────────────────────────┤
│  (~160px) │  Greeting + Date range picker                │
│           │  [KPI][KPI][KPI][KPI]                        │
│  - Menu   │  [Project Progress][Tasks Overview][This Week]│
│  - Upgrade│  [Team Members][Tasks Activity (chart)]      │
│    card   │  [Kanban Board — 4 kolom]                    │
└───────────┴──────────────────────────────────────────────┘
```

- **Grid konten:** 12 kolom, gap 16px.
- **Baris KPI:** 4 kartu sama lebar (3 kolom masing-masing).
- **Baris 2:** 3 kartu — Project Progress (±4 kol), Tasks Overview (±4 kol), This Week (±4 kol).
- **Baris 3:** Team Members (±5 kol) + Tasks Activity (±7 kol).
- **Baris 4:** Kanban Board lebar penuh, 4 kolom sama lebar.
- Frame aplikasi: kartu putih besar dengan radius XL dan shadow lembut di atas latar gradient.

---

## 4. Komponen

### 4.1 Sidebar
- Logo **FlowTask**: ikon kotak biru rounded dengan simbol "S", teks bold.
- Menu (ikon outline 18px + label 13px): Dashboard, Projects, Tasks, Kanban, Calendar, Time Tracking, Reports, Team, Clients, Documents, Settings.
- **Aktif:** latar `primary-50`, teks & ikon `primary`, font 600, radius md.
- **Default:** teks `text-muted`/`text`, tanpa latar. **Hover:** latar `#F3F6FD`.
- **Kartu Upgrade to Pro** (di bawah): gradient biru, ikon mahkota putih, judul putih bold, deskripsi kecil putih 80%, tombol pill putih "Upgrade Now →" dengan teks biru.

### 4.2 Topbar
- **Search bar:** latar `#F1F4FB`, radius lg, ikon search, placeholder "Search projects, tasks, or people...".
- **Notifikasi:** ikon lonceng dengan titik merah.
- **Profil:** avatar bulat 36px, nama (600) dan jabatan (caption) — "Sarah Miller / Product Manager", chevron dropdown.

### 4.3 Greeting & Date Picker
- Greeting "Good morning, Sarah! 👋" (h1) + subteks muted "Here's what's happening with your projects today."
- Date range picker kanan: tombol outline radius md, ikon kalender, "May 1, 2025 – May 31, 2025", chevron.

### 4.4 KPI Card
Struktur: ikon lingkaran berwarna (kiri) + label, angka besar, indikator tren + "vs last month".

| KPI | Nilai | Warna ikon | Tren |
|---|---|---|---|
| Active Projects | 12 | Biru (folder) | ↑ 25% hijau |
| Tasks Completed | 186 | Hijau (centang) | ↑ 18% hijau |
| Pending Tasks | 48 | Oranye (jam) | ↓ 12% merah |
| Team Members | 8 | Ungu (grup) | ↑ 0% netral (“Active this month”) |

- Ikon: lingkaran ±44px, latar solid penuh, ikon putih.
- Tren: panah + persen, 11px, hijau/merah sesuai arah.

### 4.5 Project Progress
- Header: judul + link "View All →".
- Baris per proyek: ikon kotak rounded berwarna pastel (±32px), nama proyek, progress bar tipis (tinggi 6px, radius full, track `#EDF0F7`), persentase di kanan.

| Proyek | Progress | Warna bar |
|---|---|---|
| Website Redesign | 78% | Biru |
| Mobile App Development | 62% | Ungu |
| CRM Integration | 45% | Hijau |
| Marketing Campaign | 90% | Oranye |

### 4.6 Tasks Overview (Donut Chart)
- Donut ketebalan ±22px, tiga segmen: Completed (biru tua), In Progress (biru sedang), To Do (biru pucat).
- Tengah: **248** (besar) + "Total Tasks" (caption).
- Legenda di bawah: titik warna + label + angka rata kanan → Completed 186, In Progress 48, To Do 14.

### 4.7 This Week (Mini Calendar + Agenda)
- Strip 7 hari (Mon–Sun, tanggal 12–18); hari ini (14, Wed) ditandai lingkaran biru solid dengan teks putih; titik kecil berwarna di bawah tanggal yang punya event.
- Daftar agenda: titik warna (merah/oranye/dll.), judul event, rentang waktu (muted), tumpukan avatar peserta (+N bila lebih).
  - Design Review — 10:00 AM – 11:00 AM
  - Sprint Planning — 1:00 PM – 2:00 PM
  - Client Feedback — 3:00 PM – 4:00 PM (+2)
- Link "View Calendar →".

### 4.8 Team Members
- Baris: avatar bulat 36px, nama (600), jabatan (muted), **badge status** di kanan.
- Badge status (pill, 10–11px, titik indikator): 
  - **Online** — `tint-success` + teks/titik hijau
  - **In a meeting** — `tint-warning` + oranye
  - **Away** — `tint-neutral` + abu
- Anggota: Sarah Miller (Product Manager), James Wilson (UI/UX Designer), Emily Davis (Frontend Developer), Michael Chen (Backend Developer), Olivia Brown (QA Engineer).

### 4.9 Tasks Activity (Stacked Bar Chart)
- Header: judul + dropdown "Last 7 days".
- Bar bertumpuk per hari (Mon–Sun), sudut atas rounded: Completed (biru tua, bawah), In Progress (biru sedang), Created (biru pucat, atas).
- Sumbu Y: 0–40, garis grid horizontal tipis putus-putus/solid `#EEF1F8`; label sumbu 11px muted.
- Legenda horizontal di bawah dengan titik warna.

### 4.10 Kanban Board
- Header: ikon board biru + "Kanban Board" + link "View Full Board →".
- 4 kolom dengan latar pastel berbeda dan counter pill di judul:

| Kolom | Jumlah | Latar |
|---|---|---|
| To Do | 4 | Abu-biru muda |
| In Progress | 3 | Biru muda |
| Review | 2 | Kuning muda |
| Done | 3 | Hijau muda |

- **Task card:** latar putih, radius md, shadow tipis, padding 12px. Isi: judul (13px/600), badge prioritas (High merah / Medium oranye / Low hijau), ikon kalender + tanggal (muted), avatar assignee di kanan-bawah.
- **Done card:** ikon centang hijau bulat di kiri judul, tanggal di bawah, tanpa badge prioritas.
- **Add Task:** tombol penuh lebar di dasar kolom, "+ Add Task", latar putih semi-transparan, teks biru.

---

## 5. Ikonografi & Gambar

- **Ikon:** gaya outline (stroke ±1.5px), sudut membulat, ukuran 16–20px (menu), 20–24px (dalam lingkaran KPI). Disarankan Lucide / Phosphor / Heroicons Outline.
- **Avatar:** foto bulat, 28–36px; tumpukan avatar dengan overlap −8px dan border putih 2px.
- **Dekorasi:** blob organik gradient di sudut dan pola titik-titik (dot grid) kecil di kanan atas hero.

---

## 6. Interaksi & State

| Elemen | Hover | Active / Focus |
|---|---|---|
| Menu sidebar | Latar `#F3F6FD` | Latar `primary-50`, teks biru |
| Tombol primer | `primary-600` | Ring biru 3px opasitas 25% |
| Kartu task | Naik 1–2px + shadow-float | Outline biru tipis saat di-drag |
| Link "View All" | Garis bawah | — |
| Input search | Border `primary-200` | Border `primary` + ring |
| Bar/segmen chart | Tooltip (nilai & label) | — |

- Transisi: `150–200ms ease-out`.
- Kanban mendukung **drag & drop** antar kolom.

---

## 7. Responsivitas

| Breakpoint | Perilaku |
|---|---|
| ≥ 1280px | Layout penuh seperti referensi |
| 1024–1279px | KPI tetap 4 kolom; baris 2 menjadi 2+1; sidebar dipersempit |
| 768–1023px | Sidebar menjadi ikon-saja/drawer; KPI 2×2; kartu 1–2 kolom |
| < 768px | Satu kolom; sidebar jadi menu hamburger; Kanban scroll horizontal |

---

## 8. Aksesibilitas

- Kontras teks utama terhadap latar ≥ **4.5:1**; periksa teks muted (`#6B7490` di atas putih ≈ 4.7:1).
- Status tidak hanya dibedakan warna: sertakan label teks (Online/Away) dan ikon/titik.
- Chart wajib punya legenda teks dan `aria-label`/tabel alternatif.
- Fokus keyboard terlihat jelas (ring biru) pada semua elemen interaktif.
- Target sentuh minimal 40×40px untuk tombol & ikon.

---

## 9. Contoh CSS Variables

```css
:root {
  /* Color */
  --color-primary: #2563EB;
  --color-primary-600: #1D4ED8;
  --color-primary-400: #6EA0F5;
  --color-primary-200: #C9D8F8;
  --color-primary-50: #EAF1FE;
  --color-text-strong: #0F1B3D;
  --color-text: #1F2A44;
  --color-text-muted: #6B7490;
  --color-border: #E6EAF4;
  --color-bg-app: #F5F7FD;
  --color-surface: #FFFFFF;
  --color-success: #22C58B;
  --color-warning: #F5A524;
  --color-danger: #EF4444;
  --color-purple: #7C5CE0;

  /* Radius */
  --radius-md: 10px;
  --radius-lg: 16px;
  --radius-xl: 24px;

  /* Shadow */
  --shadow-card: 0 2px 12px rgba(30, 50, 110, 0.06);

  /* Font */
  --font-sans: "Inter", "Plus Jakarta Sans", system-ui, sans-serif;
}

.card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
  padding: 20px;
}
```

---

## 10. Catatan Implementasi

- **Stack yang disarankan:** React/Next.js + Tailwind CSS; chart dengan Recharts atau Chart.js; drag & drop Kanban dengan dnd-kit.
- Gunakan data dummy sesuai gambar agar tampilan awal identik dengan referensi.
- Pisahkan komponen: `Sidebar`, `Topbar`, `KpiCard`, `ProjectProgress`, `TasksDonut`, `WeekAgenda`, `TeamList`, `ActivityChart`, `KanbanBoard`, `TaskCard`, `StatusBadge`, `PriorityBadge`.
- Tanggal pada referensi: **1–31 Mei 2025**, hari ini **Rabu, 14 Mei**.

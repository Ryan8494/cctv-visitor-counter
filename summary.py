"""
summary.py — Logika murni pembuatan ringkasan harian dan saran staf.

Modul ini TIDAK mengimpor cv2, ultralytics, atau mengakses database/jaringan.
Input berupa angka agregat satu hari/rentang hari;
output berupa ringkasan terstruktur dan teks rekomendasi Bahasa Indonesia.

Aturan berbasis angka (sesuai AGENTS.md):
- Jam dengan pengunjung >= persentil tertentu (default: P75) atau alert >= 2 ditandai 'sibuk'.
- Rekomendasi penambahan staf diberikan spesifik pada rentang jam sibuk tersebut.
- Memberikan peringatan 'data masih sedikit' bila sampel kurang dari 4 hari/akhir pekan.
"""

from __future__ import annotations


def calculate_percentile(values: list[float | int], percentile: float) -> float:
    """Hitung nilai persentil dari list angka (metode interpolasi linear)."""
    if not values:
        return 0.0
    sorted_v = sorted(values)
    k = (len(sorted_v) - 1) * (percentile / 100.0)
    f = int(k)
    c = f + 1
    if c < len(sorted_v):
        d0 = sorted_v[f] * (c - k)
        d1 = sorted_v[c] * (k - f)
        return d0 + d1
    return float(sorted_v[f])


def generate_daily_summary(
    hourly_visitors: dict[int, int],
    hourly_occupancy_ratio: dict[int, float],
    hourly_queue_avg: dict[int, float],
    hourly_alerts: dict[int, int],
    num_days_sample: int = 7,
    percentile: float = 75.0,
) -> dict:
    """Buat ringkasan operasional harian dan rekomendasi jadwal staf.

    Args:
        hourly_visitors: dict {jam: jumlah_pengunjung_masuk} untuk 0..23
        hourly_occupancy_ratio: dict {jam: rasio_meja_terisi (0.0 - 1.0)}
        hourly_queue_avg: dict {jam: rata_rata_orang_antre}
        hourly_alerts: dict {jam: total_alert}
        num_days_sample: jumlah hari yang dijadikan dasar sampel
        percentile: ambang persentil untuk menetapkan jam sibuk

    Returns:
        dict ringkasan terstruktur dan teks rekomendasi.
    """
    warning = None
    if num_days_sample < 4:
        warning = (
            f"Data masih sedikit ({num_days_sample} hari sampel). "
            "Saran jam sibuk mungkin belum sepenuhnya stabil."
        )

    # 1. Puncak Pengunjung
    visitor_values = [hourly_visitors.get(h, 0) for h in range(24)]
    max_visitors = max(visitor_values) if visitor_values else 0
    peak_visitor_hour = max(range(24), key=lambda h: hourly_visitors.get(h, 0)) if max_visitors > 0 else 0

    # 2. Rata-rata Okupansi Meja Keseluruhan (jam operasional siang-malam mis. 10:00 - 22:00)
    op_hours = [h for h in range(10, 22) if h in hourly_occupancy_ratio]
    if op_hours:
        avg_occupancy = sum(hourly_occupancy_ratio[h] for h in op_hours) / len(op_hours)
    else:
        avg_occupancy = 0.0

    # 3. Puncak Antrean Kasir
    queue_values = [hourly_queue_avg.get(h, 0.0) for h in range(24)]
    max_queue = max(queue_values) if queue_values else 0.0
    peak_queue_hour = max(range(24), key=lambda h: hourly_queue_avg.get(h, 0.0)) if max_queue > 0 else 0

    # 4. Tentukan Jam Sibuk Berbasis Angka
    # Ambang persentil dari jam operasional (10-21)
    op_visitors = [hourly_visitors.get(h, 0) for h in range(10, 22)]
    threshold = calculate_percentile(op_visitors, percentile)

    busy_hours = []
    for h in range(24):
        visitors = hourly_visitors.get(h, 0)
        alerts = hourly_alerts.get(h, 0)
        q_avg = hourly_queue_avg.get(h, 0.0)
        occ = hourly_occupancy_ratio.get(h, 0.0)

        is_busy_vis = visitors >= threshold and visitors > 0
        is_busy_alert = alerts >= 2

        if is_busy_vis or is_busy_alert:
            reasons = []
            if is_busy_vis:
                reasons.append(f"kunjungan tinggi (≥ P{int(percentile)})")
            if is_busy_alert:
                reasons.append(f"{alerts} alert antrean/layanan")

            busy_hours.append({
                "hour": h,
                "visitors": visitors,
                "occupancy_ratio": occ,
                "queue_avg": q_avg,
                "alerts": alerts,
                "reasons": reasons,
            })

    # 5. Susun Teks Rekomendasi
    recs = []
    if busy_hours:
        # Kelompokkan jam-jam sibuk yang berurutan jika memungkinkan
        for bh in busy_hours:
            h = bh["hour"]
            reason_str = ", ".join(bh["reasons"])
            recs.append(
                f"Pukul {h:02d}:00–{h + 1:02d}:00: "
                f"rata-rata {bh['visitors']} tamu, antrean {bh['queue_avg']:.1f} orang ({reason_str}). "
                f"Saran: tambah 1 staf pelayanan/kasir."
            )
        recommendation_text = " ".join(recs)
    else:
        recommendation_text = "Operasional berjalan stabil, belum ada jam yang melewati ambang batas sibuk."

    summary_text = (
        f"Puncak keramaian pukul {peak_visitor_hour:02d}:00–{peak_visitor_hour + 1:02d}:00 ({max_visitors} tamu). "
        f"Antrean terpanjang rata-rata {max_queue:.1f} orang pukul {peak_queue_hour:02d}:00. "
        f"Rata-rata okupansi meja {avg_occupancy:.0%}. "
        f"Saran: {recommendation_text}"
    )

    return {
        "peak_hour": peak_visitor_hour,
        "peak_visitors": max_visitors,
        "avg_occupancy_ratio": avg_occupancy,
        "max_queue_people": max_queue,
        "peak_queue_hour": peak_queue_hour,
        "busy_hours": busy_hours,
        "summary_text": summary_text,
        "warning": warning,
    }


def format_telegram_summary(summary: dict) -> str:
    """Format hasil ringkasan ke dalam pesan Telegram Markdown."""
    lines = [
        "📋 *RINGKASAN OPERASIONAL & SARAN STAF*",
        "",
        f"👥 *Puncak Kunjungan*: Pukul {summary['peak_hour']:02d}:00–{summary['peak_hour'] + 1:02d}:00 ({summary['peak_visitors']} tamu)",
        f"🧍 *Puncak Antrean*: Pukul {summary['peak_queue_hour']:02d}:00 ({summary['max_queue_people']:.1f} orang)",
        f"🪑 *Okupansi Meja*: Rata-rata {summary['avg_occupancy_ratio']:.0%}",
        "",
    ]

    if summary["warning"]:
        lines.append(f"⚠️ _{summary['warning']}_\n")

    lines.append("*Saran Penjadwalan Staf:*")
    if summary["busy_hours"]:
        for bh in summary["busy_hours"]:
            h = bh["hour"]
            lines.append(
                f"• *{h:02d}:00–{h + 1:02d}:00*: {bh['visitors']} tamu, {bh['alerts']} alert. Tambah 1 staf."
            )
    else:
        lines.append("• Beban kerja normal. Tidak diperlukan penambahan pegawai.")

    return "\n".join(lines)

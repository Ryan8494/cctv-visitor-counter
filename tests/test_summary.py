"""
tests/test_summary.py — Uji logika pembuat ringkasan harian dan saran staf.

Kasus uji sesuai AGENTS.md & TODO.md Fase 7:
- Jam sibuk terdeteksi berbasis persentil dan alert
- Saran penambahan pegawai muncul pada jam sibuk
- Peringatan 'data masih sedikit' muncul bila sampel < 4 hari
- Format pesan Telegram rapi dan valid
"""

import pytest
from summary import generate_daily_summary, format_telegram_summary, calculate_percentile


def test_calculate_percentile():
    """Uji perhitungan persentil."""
    data = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    p50 = calculate_percentile(data, 50)
    p75 = calculate_percentile(data, 75)
    assert p50 == pytest.approx(55.0, abs=1.0)
    assert p75 == pytest.approx(77.5, abs=1.0)


def test_jam_sibuk_terdeteksi_dan_saran_muncul():
    """Jam dengan pengunjung tinggi atau banyak alert ditandai sibuk dan diberi saran."""
    # Jam 12 dan 19 dibuat ramai
    visitors = {h: 15 for h in range(24)}
    visitors[12] = 55
    visitors[19] = 60

    occ_ratio = {h: 0.4 for h in range(24)}
    occ_ratio[12] = 0.85
    occ_ratio[19] = 0.90

    queue_avg = {h: 1.0 for h in range(24)}
    queue_avg[12] = 4.5
    queue_avg[19] = 5.0

    # Jam 13 memiliki 3 alert meskipun pengunjung sedang
    alerts = {h: 0 for h in range(24)}
    alerts[13] = 3

    res = generate_daily_summary(
        hourly_visitors=visitors,
        hourly_occupancy_ratio=occ_ratio,
        hourly_queue_avg=queue_avg,
        hourly_alerts=alerts,
        num_days_sample=7,
        percentile=75.0,
    )

    busy_hours = [b["hour"] for b in res["busy_hours"]]
    assert 12 in busy_hours, "Jam 12 harus terdeteksi sibuk"
    assert 19 in busy_hours, "Jam 19 harus terdeteksi sibuk"
    assert 13 in busy_hours, "Jam 13 harus terdeteksi sibuk karena >= 2 alert"

    assert res["peak_hour"] == 19
    assert res["peak_visitors"] == 60
    assert "tambah 1 staf" in res["summary_text"].lower()
    assert res["warning"] is None  # Karena sampel 7 hari


def test_peringatan_data_sedikit():
    """Jika data sampel < 4 hari, peringatan harus muncul."""
    visitors = {h: 10 for h in range(24)}
    res = generate_daily_summary(
        hourly_visitors=visitors,
        hourly_occupancy_ratio={},
        hourly_queue_avg={},
        hourly_alerts={},
        num_days_sample=2,  # Hanya 2 hari
    )

    assert res["warning"] is not None
    assert "data masih sedikit" in res["warning"].lower()


def test_format_telegram():
    """Uji format pesan Telegram Markdown."""
    summary_data = {
        "peak_hour": 13,
        "peak_visitors": 45,
        "avg_occupancy_ratio": 0.65,
        "max_queue_people": 4.0,
        "peak_queue_hour": 13,
        "busy_hours": [
            {"hour": 13, "visitors": 45, "alerts": 2}
        ],
        "warning": None,
    }

    msg = format_telegram_summary(summary_data)
    assert "*RINGKASAN OPERASIONAL & SARAN STAF*" in msg
    assert "Pukul 13:00–14:00" in msg
    assert "Tambah 1 staf" in msg

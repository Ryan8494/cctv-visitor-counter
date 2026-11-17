"""
simulate.py — Pembuat data simulasi untuk mengisi database.

Menghasilkan data kunjungan, sampel antrean, dan event realistis
selama beberapa akhir pekan untuk menguji dashboard.
"""

from __future__ import annotations

import json
import os
import random
from datetime import datetime, timedelta

from db import init_db, save_visit, save_queue_sample, save_event


def load_config(path: str = "config.json") -> dict:
    """Muat konfigurasi."""
    config_path = os.path.join(os.path.dirname(__file__), path)
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def simulate(
    num_weeks: int = 4,
    db_path: str | None = None,
    seed: int = 42,
):
    """Buat data simulasi realistis.

    Args:
        num_weeks: jumlah minggu data yang dibuat
        db_path: path database (default dari config.json)
        seed: seed random untuk reprodusibilitas
    """
    random.seed(seed)

    config = load_config()
    if db_path is None:
        db_path = config.get("db_path", "data.db")

    max_people = config.get("queue_max_people", 5)
    max_wait = config.get("queue_max_wait_sec", 120)

    conn = init_db(db_path)

    # Mulai dari num_weeks minggu lalu, hari Senin
    base = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    base -= timedelta(days=base.weekday())  # mundur ke Senin
    base -= timedelta(weeks=num_weeks)

    print(f"Membuat data simulasi {num_weeks} minggu mulai {base.strftime('%Y-%m-%d')}...")

    total_visits = 0
    total_samples = 0
    total_events = 0

    for week in range(num_weeks):
        week_start = base + timedelta(weeks=week)

        for day_offset in range(7):
            current_day = week_start + timedelta(days=day_offset)
            day_of_week = current_day.weekday()  # 0=Senin, 6=Minggu
            is_weekend = day_of_week >= 5

            # Jam operasional: 08:00 - 22:00
            for hour in range(8, 22):
                # Pola pengunjung per jam (lebih ramai di jam makan dan akhir pekan)
                base_rate = _hourly_rate(hour, is_weekend)

                # Simulasi kunjungan per jam
                num_visitors = max(0, int(random.gauss(base_rate, base_rate * 0.3)))

                for _ in range(num_visitors):
                    minute = random.randint(0, 59)
                    second = random.randint(0, 59)
                    ts = current_day.replace(hour=hour, minute=minute, second=second)
                    ts_str = ts.strftime("%Y-%m-%d %H:%M:%S")

                    # Kebanyakan orang masuk lalu keluar
                    save_visit(conn, "IN", ts_str)
                    total_visits += 1

                    # Orang keluar setelah beberapa menit
                    stay_minutes = random.randint(5, 90)
                    exit_ts = ts + timedelta(minutes=stay_minutes)
                    if exit_ts.hour < 22:
                        exit_ts_str = exit_ts.strftime("%Y-%m-%d %H:%M:%S")
                        save_visit(conn, "OUT", exit_ts_str)
                        total_visits += 1

                # Simulasi sampel antrean (tiap 5 menit)
                for minute in range(0, 60, 5):
                    ts = current_day.replace(hour=hour, minute=minute, second=0)
                    ts_str = ts.strftime("%Y-%m-%d %H:%M:%S")

                    # Jumlah orang di antrean berkorelasi dengan keramaian
                    queue_people = max(0, int(random.gauss(
                        base_rate / 10, 2
                    )))
                    wait_sec = max(0, random.gauss(
                        queue_people * 20, 15
                    ))

                    save_queue_sample(conn, queue_people, wait_sec, ts_str)
                    total_samples += 1

                    # Simulasi alert jika antrean penuh
                    if queue_people >= max_people:
                        save_event(
                            conn,
                            "ALERT_ANTREAN_PANJANG",
                            f"{queue_people} orang di zona antrean (batas: {max_people})",
                            ts_str,
                        )
                        total_events += 1

                    if wait_sec >= max_wait:
                        save_event(
                            conn,
                            "ALERT_TUNGGU_LAMA",
                            f"Waktu tunggu terlama: {wait_sec:.0f}s (batas: {max_wait:.0f}s)",
                            ts_str,
                        )
                        total_events += 1

    conn.close()
    print(f"Simulasi selesai:")
    print(f"  - {total_visits} kunjungan")
    print(f"  - {total_samples} sampel antrean")
    print(f"  - {total_events} event/alert")
    print(f"Database: {db_path}")


def _hourly_rate(hour: int, is_weekend: bool) -> float:
    """Pola tingkat pengunjung per jam (lebih ramai jam makan & akhir pekan).

    Returns:
        rata-rata jumlah pengunjung per jam
    """
    # Pola dasar jam makan
    patterns = {
        8: 10, 9: 15, 10: 20, 11: 35, 12: 55, 13: 50,
        14: 30, 15: 25, 16: 20, 17: 30, 18: 45, 19: 60,
        20: 50, 21: 25,
    }
    rate = patterns.get(hour, 15)

    # Akhir pekan lebih ramai ~40%
    if is_weekend:
        rate = int(rate * 1.4)

    return rate


if __name__ == "__main__":
    simulate()

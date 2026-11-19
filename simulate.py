"""
simulate.py — Pembuat data simulasi untuk mengisi database SQLite.

Menghasilkan data kunjungan pintu, sesi duduk meja, sampel okupansi,
sampel antrean kasir, riwayat kunjungan antrean, dan event alert realistis
selama beberapa minggu untuk menguji dan mendemonstrasikan dashboard.
"""

from __future__ import annotations

import json
import os
import random
from datetime import datetime, timedelta

from db import (
    init_db,
    save_visit,
    save_queue_sample,
    save_queue_visit,
    save_table_session,
    save_occupancy_sample,
    save_event,
)


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
    """Buat data simulasi realistis untuk seluruh tabel.

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
    tables_list = list(config.get("tables", {"Meja 1": [], "Meja 2": []}).keys())
    total_tables = max(1, len(tables_list))

    conn = init_db(db_path)

    # Mulai dari num_weeks minggu lalu, hari Senin
    base = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    base -= timedelta(days=base.weekday())  # mundur ke Senin
    base -= timedelta(weeks=num_weeks)

    print(f"Membuat data simulasi {num_weeks} minggu mulai {base.strftime('%Y-%m-%d')}...")

    total_visits = 0
    total_queue_samples = 0
    total_queue_visits = 0
    total_table_sessions = 0
    total_occupancy_samples = 0
    total_events = 0

    for week in range(num_weeks):
        week_start = base + timedelta(weeks=week)

        for day_offset in range(7):
            current_day = week_start + timedelta(days=day_offset)
            day_of_week = current_day.weekday()  # 0=Senin, 6=Minggu
            is_weekend = day_of_week >= 5

            # Jam operasional: 08:00 - 22:00
            for hour in range(8, 22):
                base_rate = _hourly_rate(hour, is_weekend)

                # 1. Simulasi kunjungan pintu masuk & keluar
                num_visitors = max(0, int(random.gauss(base_rate, base_rate * 0.3)))

                for _ in range(num_visitors):
                    minute = random.randint(0, 59)
                    second = random.randint(0, 59)
                    ts = current_day.replace(hour=hour, minute=minute, second=second)
                    ts_str = ts.strftime("%Y-%m-%d %H:%M:%S")

                    save_visit(conn, "IN", ts_str)
                    total_visits += 1

                    # Sebagian besar pengunjung duduk di meja
                    if random.random() < 0.75:
                        table_name = random.choice(tables_list)
                        sit_duration_min = random.randint(20, 90)
                        sit_duration_sec = float(sit_duration_min * 60)
                        end_sit = ts + timedelta(minutes=sit_duration_min)
                        if end_sit.hour < 22:
                            save_table_session(
                                conn,
                                table_name=table_name,
                                start_ts=ts_str,
                                end_ts=end_sit.strftime("%Y-%m-%d %H:%M:%S"),
                                duration_sec=sit_duration_sec,
                            )
                            total_table_sessions += 1

                    # Kunjungan antrean kasir (bayar sebelum keluar)
                    if random.random() < 0.70:
                        wait_sec = max(5.0, random.gauss(45.0, 20.0))
                        q_start = ts + timedelta(minutes=random.randint(15, 80))
                        q_end = q_start + timedelta(seconds=int(wait_sec))
                        if q_end.hour < 22:
                            save_queue_visit(
                                conn,
                                start_ts=q_start.strftime("%Y-%m-%d %H:%M:%S"),
                                end_ts=q_end.strftime("%Y-%m-%d %H:%M:%S"),
                                wait_sec=wait_sec,
                            )
                            total_queue_visits += 1

                    # Orang keluar restoran
                    stay_minutes = random.randint(20, 100)
                    exit_ts = ts + timedelta(minutes=stay_minutes)
                    if exit_ts.hour < 22:
                        exit_ts_str = exit_ts.strftime("%Y-%m-%d %H:%M:%S")
                        save_visit(conn, "OUT", exit_ts_str)
                        total_visits += 1

                # 2. Simulasi sampel antrean & okupansi (tiap 5 menit)
                for minute in range(0, 60, 5):
                    ts = current_day.replace(hour=hour, minute=minute, second=0)
                    ts_str = ts.strftime("%Y-%m-%d %H:%M:%S")

                    # Antrean kasir
                    queue_people = max(0, int(random.gauss(base_rate / 10, 2)))
                    wait_sec = max(0.0, random.gauss(queue_people * 20, 15))

                    save_queue_sample(conn, queue_people, wait_sec, ts_str)
                    total_queue_samples += 1

                    # Okupansi meja
                    ratio = min(1.0, max(0.0, random.gauss(base_rate / 60.0, 0.15)))
                    occupied_tables = min(total_tables, int(round(ratio * total_tables)))
                    save_occupancy_sample(conn, occupied_tables, total_tables, ts_str)
                    total_occupancy_samples += 1

                    # Alert antrean panjang
                    if queue_people >= max_people:
                        save_event(
                            conn,
                            "ALERT_ANTREAN_PANJANG",
                            f"{queue_people} orang di zona antrean (batas: {max_people})",
                            ts_str,
                        )
                        total_events += 1

                    # Alert waktu tunggu lama
                    if wait_sec >= max_wait:
                        save_event(
                            conn,
                            "ALERT_TUNGGU_LAMA",
                            f"Waktu tunggu terlama: {wait_sec:.0f}s (batas: {max_wait:.0f}s)",
                            ts_str,
                        )
                        total_events += 1

    conn.close()
    print("Simulasi selesai:")
    print(f"  - {total_visits:,} kunjungan pintu (IN/OUT)")
    print(f"  - {total_table_sessions:,} sesi duduk meja (table_sessions)")
    print(f"  - {total_occupancy_samples:,} sampel okupansi meja")
    print(f"  - {total_queue_samples:,} sampel antrean kasir")
    print(f"  - {total_queue_visits:,} riwayat kunjungan antrean (queue_visits)")
    print(f"  - {total_events:,} alert & kejadian")
    print(f"Database: {db_path}")


def _hourly_rate(hour: int, is_weekend: bool) -> float:
    """Pola tingkat pengunjung per jam."""
    patterns = {
        8: 10, 9: 15, 10: 20, 11: 35, 12: 55, 13: 50,
        14: 30, 15: 25, 16: 20, 17: 30, 18: 45, 19: 60,
        20: 50, 21: 25,
    }
    rate = patterns.get(hour, 15)
    if is_weekend:
        rate = int(rate * 1.4)
    return rate


if __name__ == "__main__":
    simulate()

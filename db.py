"""
db.py — Akses database SQLite untuk sistem pemantauan restoran/pengunjung.

Skema tabel (sesuai AGENTS.md):
- visits(ts, direction)                             : satu baris per orang masuk/keluar (IN/OUT)
- table_sessions(table_name, start_ts, end_ts, duration_sec) : sesi duduk di meja
- occupancy_samples(ts, occupied, total)            : sampel okupansi meja berkala
- queue_samples(ts, people_in_zone, max_wait_sec)   : sampel antrean berkala
- queue_visits(start_ts, end_ts, wait_sec)          : sesi kunjungan antrean kasir
- events(ts, event, detail)                         : alert dan kejadian penting
"""

from __future__ import annotations

import sqlite3
from datetime import datetime


def _now_str() -> str:
    """Waktu lokal dalam format YYYY-MM-DD HH:MM:SS."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def init_db(db_path: str) -> sqlite3.Connection:
    """Buat koneksi dan pastikan seluruh tabel sudah ada."""
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS visits (
            ts TEXT NOT NULL,
            direction TEXT NOT NULL CHECK(direction IN ('IN', 'OUT'))
        );

        CREATE TABLE IF NOT EXISTS table_sessions (
            table_name TEXT NOT NULL,
            start_ts TEXT NOT NULL,
            end_ts TEXT NOT NULL,
            duration_sec REAL NOT NULL
        );

        CREATE TABLE IF NOT EXISTS occupancy_samples (
            ts TEXT NOT NULL,
            occupied INTEGER NOT NULL,
            total INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS queue_samples (
            ts TEXT NOT NULL,
            people_in_zone INTEGER NOT NULL,
            max_wait_sec REAL NOT NULL
        );

        CREATE TABLE IF NOT EXISTS queue_visits (
            start_ts TEXT NOT NULL,
            end_ts TEXT NOT NULL,
            wait_sec REAL NOT NULL
        );

        CREATE TABLE IF NOT EXISTS events (
            ts TEXT NOT NULL,
            event TEXT NOT NULL,
            detail TEXT
        );
    """)
    conn.commit()
    return conn


# ── Fungsi Simpan (Write) ──────────────────────────────────────

def save_visit(conn: sqlite3.Connection, direction: str, ts: str | None = None):
    """Simpan satu kunjungan pintu masuk/keluar (IN/OUT)."""
    ts = ts or _now_str()
    conn.execute("INSERT INTO visits (ts, direction) VALUES (?, ?)", (ts, direction))
    conn.commit()


def save_table_session(
    conn: sqlite3.Connection,
    table_name: str,
    start_ts: str,
    end_ts: str,
    duration_sec: float,
):
    """Simpan satu sesi duduk meja yang selesai."""
    conn.execute(
        "INSERT INTO table_sessions (table_name, start_ts, end_ts, duration_sec) VALUES (?, ?, ?, ?)",
        (table_name, start_ts, end_ts, duration_sec),
    )
    conn.commit()


def save_occupancy_sample(
    conn: sqlite3.Connection,
    occupied: int,
    total: int,
    ts: str | None = None,
):
    """Simpan sampel okupansi meja periodik."""
    ts = ts or _now_str()
    conn.execute(
        "INSERT INTO occupancy_samples (ts, occupied, total) VALUES (?, ?, ?)",
        (ts, occupied, total),
    )
    conn.commit()


def save_queue_sample(
    conn: sqlite3.Connection,
    people_in_zone: int,
    max_wait_sec: float,
    ts: str | None = None,
):
    """Simpan sampel antrean kasir periodik."""
    ts = ts or _now_str()
    conn.execute(
        "INSERT INTO queue_samples (ts, people_in_zone, max_wait_sec) VALUES (?, ?, ?)",
        (ts, people_in_zone, max_wait_sec),
    )
    conn.commit()


def save_queue_visit(
    conn: sqlite3.Connection,
    start_ts: str,
    end_ts: str,
    wait_sec: float,
):
    """Simpan satu kunjungan/antrean kasir yang selesai."""
    conn.execute(
        "INSERT INTO queue_visits (start_ts, end_ts, wait_sec) VALUES (?, ?, ?)",
        (start_ts, end_ts, wait_sec),
    )
    conn.commit()


def save_event(
    conn: sqlite3.Connection,
    event: str,
    detail: str = "",
    ts: str | None = None,
):
    """Simpan event/alert."""
    ts = ts or _now_str()
    conn.execute(
        "INSERT INTO events (ts, event, detail) VALUES (?, ?, ?)",
        (ts, event, detail),
    )
    conn.commit()


# ── Fungsi Baca (Read) ─────────────────────────────────────────

def read_visits(conn: sqlite3.Connection) -> list[tuple]:
    """Baca semua data kunjungan. Mengembalikan list (ts, direction)."""
    cur = conn.execute("SELECT ts, direction FROM visits ORDER BY ts")
    return cur.fetchall()


def read_table_sessions(conn: sqlite3.Connection) -> list[tuple]:
    """Baca sesi meja. Mengembalikan list (table_name, start_ts, end_ts, duration_sec)."""
    cur = conn.execute("SELECT table_name, start_ts, end_ts, duration_sec FROM table_sessions ORDER BY start_ts")
    return cur.fetchall()


def read_occupancy_samples(conn: sqlite3.Connection) -> list[tuple]:
    """Baca sampel okupansi meja. Mengembalikan list (ts, occupied, total)."""
    cur = conn.execute("SELECT ts, occupied, total FROM occupancy_samples ORDER BY ts")
    return cur.fetchall()


def read_queue_samples(conn: sqlite3.Connection) -> list[tuple]:
    """Baca sampel antrean. Mengembalikan list (ts, people_in_zone, max_wait_sec)."""
    cur = conn.execute("SELECT ts, people_in_zone, max_wait_sec FROM queue_samples ORDER BY ts")
    return cur.fetchall()


def read_queue_visits(conn: sqlite3.Connection) -> list[tuple]:
    """Baca riwayat kunjungan antrean. Mengembalikan list (start_ts, end_ts, wait_sec)."""
    cur = conn.execute("SELECT start_ts, end_ts, wait_sec FROM queue_visits ORDER BY start_ts")
    return cur.fetchall()


def read_events(conn: sqlite3.Connection) -> list[tuple]:
    """Baca semua event. Mengembalikan list (ts, event, detail)."""
    cur = conn.execute("SELECT ts, event, detail FROM events ORDER BY ts")
    return cur.fetchall()

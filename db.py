"""
db.py — Akses database SQLite untuk sistem pemantauan pengunjung dan antrean.

Skema tabel:
- visits(ts, direction)          : satu baris per orang masuk/keluar (IN/OUT)
- queue_samples(ts, people_in_zone, max_wait_sec) : sampel antrean periodik
- events(ts, event, detail)      : alert dan kejadian penting
"""

import sqlite3
from datetime import datetime


def _now_str():
    """Waktu lokal dalam format YYYY-MM-DD HH:MM:SS."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def init_db(db_path: str) -> sqlite3.Connection:
    """Buat koneksi dan pastikan tabel sudah ada."""
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS visits (
            ts TEXT NOT NULL,
            direction TEXT NOT NULL CHECK(direction IN ('IN', 'OUT'))
        );

        CREATE TABLE IF NOT EXISTS queue_samples (
            ts TEXT NOT NULL,
            people_in_zone INTEGER NOT NULL,
            max_wait_sec REAL NOT NULL
        );

        CREATE TABLE IF NOT EXISTS events (
            ts TEXT NOT NULL,
            event TEXT NOT NULL,
            detail TEXT
        );
    """)
    conn.commit()
    return conn


# ── Fungsi simpan ──────────────────────────────────────────────

def save_visit(conn: sqlite3.Connection, direction: str, ts: str | None = None):
    """Simpan satu kunjungan masuk/keluar.

    Args:
        conn: koneksi database
        direction: 'IN' atau 'OUT'
        ts: timestamp opsional (default: waktu sekarang)
    """
    ts = ts or _now_str()
    conn.execute("INSERT INTO visits (ts, direction) VALUES (?, ?)", (ts, direction))
    conn.commit()


def save_queue_sample(conn: sqlite3.Connection, people_in_zone: int,
                      max_wait_sec: float, ts: str | None = None):
    """Simpan sampel antrean.

    Args:
        conn: koneksi database
        people_in_zone: jumlah orang di zona antrean saat ini
        max_wait_sec: waktu tunggu terlama (detik)
        ts: timestamp opsional
    """
    ts = ts or _now_str()
    conn.execute(
        "INSERT INTO queue_samples (ts, people_in_zone, max_wait_sec) VALUES (?, ?, ?)",
        (ts, people_in_zone, max_wait_sec),
    )
    conn.commit()


def save_event(conn: sqlite3.Connection, event: str, detail: str = "",
               ts: str | None = None):
    """Simpan event (alert, kejadian penting).

    Args:
        conn: koneksi database
        event: nama event (misal ALERT_ANTREAN_PANJANG)
        detail: informasi tambahan
        ts: timestamp opsional
    """
    ts = ts or _now_str()
    conn.execute(
        "INSERT INTO events (ts, event, detail) VALUES (?, ?, ?)",
        (ts, event, detail),
    )
    conn.commit()


# ── Fungsi baca (untuk dashboard) ─────────────────────────────

def read_visits(conn: sqlite3.Connection) -> list[tuple]:
    """Baca semua data kunjungan. Mengembalikan list (ts, direction)."""
    cur = conn.execute("SELECT ts, direction FROM visits ORDER BY ts")
    return cur.fetchall()


def read_queue_samples(conn: sqlite3.Connection) -> list[tuple]:
    """Baca semua sampel antrean. Mengembalikan list (ts, people_in_zone, max_wait_sec)."""
    cur = conn.execute("SELECT ts, people_in_zone, max_wait_sec FROM queue_samples ORDER BY ts")
    return cur.fetchall()


def read_events(conn: sqlite3.Connection) -> list[tuple]:
    """Baca semua event. Mengembalikan list (ts, event, detail)."""
    cur = conn.execute("SELECT ts, event, detail FROM events ORDER BY ts")
    return cur.fetchall()

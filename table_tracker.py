"""
table_tracker.py — Logika murni pelacakan okupansi meja dan durasi duduk.

Modul ini TIDAK mengimpor cv2, ultralytics, atau modul berat lainnya.
Input berupa ID, posisi titik pusat (cx, cy), dan waktu (now dalam detik);
output berupa sesi duduk yang selesai dan status okupansi meja.

Aturan Sesi Duduk (sesuai AGENTS.md):
1. Orang terdeteksi di dalam poligon meja.
2. min_dwell_sec (mis. 30 detik): orang yang hanya lewat atau berdiri sebentar
   tidak dicatat sebagai sesi duduk (status tetap KOSONG).
3. leave_grace_sec (mis. 20 detik): toleransi orang terhalang sesaat agar
   sesi tidak terputus prematur.
4. Pencatatan sesi: saat orang benar-benar pergi (> leave_grace_sec), sesi duduk
   disimpan dengan start_time, end_time, dan duration_sec.
"""

from __future__ import annotations

# ── Status Meja ─────────────────────────────────────────────────
KOSONG = "KOSONG"
TERISI = "TERISI"


def _point_in_polygon(
    point: tuple[int | float, int | float],
    polygon: list[tuple[int | float, int | float]],
) -> bool:
    """Cek apakah titik berada di dalam poligon (ray casting algorithm)."""
    x, y = point
    n = len(polygon)
    inside = False

    j = n - 1
    for i in range(n):
        xi, yi = polygon[i]
        xj, yj = polygon[j]

        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
            inside = not inside
        j = i

    return inside


class Table:
    """Pelacak status dan sesi untuk satu meja spesifik."""

    def __init__(
        self,
        name: str,
        polygon: list[tuple[int | float, int | float]],
        min_dwell_sec: float = 30.0,
        leave_grace_sec: float = 20.0,
    ):
        self.name = name
        self.polygon = polygon
        self.min_dwell_sec = min_dwell_sec
        self.leave_grace_sec = leave_grace_sec

        self.state = KOSONG

        # Timestamp tracking
        self.first_seen: float | None = None      # Waktu pertama orang terdeteksi
        self.last_seen: float | None = None       # Waktu terakhir orang terdeteksi
        self.session_start: float | None = None   # Waktu mulai resmi sesi duduk

    def update(
        self,
        detections: list[tuple[int, tuple[int | float, int | float]]],
        now: float,
    ) -> dict | None:
        """Perbarui status meja berdasarkan deteksi frame saat ini.

        Args:
            detections: list (track_id, (cx, cy)) orang terdeteksi
            now: waktu saat ini (detik)

        Returns:
            dict sesi duduk jika orang baru saja selesai duduk/pergi:
            {"table_name": str, "start_time": float, "end_time": float, "duration_sec": float}
            None jika tidak ada sesi yang selesai.
        """
        # Cek apakah ada orang di area meja
        person_present = any(_point_in_polygon(center, self.polygon) for _, center in detections)

        completed_session = None

        if person_present:
            self.last_seen = now
            if self.first_seen is None:
                self.first_seen = now

            # Jika masih KOSONG, cek apakah durasi keberadaan sudah >= min_dwell_sec
            if self.state == KOSONG:
                if (now - self.first_seen) >= self.min_dwell_sec:
                    self.state = TERISI
                    self.session_start = self.first_seen

        else:
            # Tidak ada orang terdeteksi di meja pada frame ini
            if self.state == TERISI:
                # Cek apakah sudah melebihi toleransi deteksi hilang (leave_grace_sec)
                if self.last_seen is not None and (now - self.last_seen) > self.leave_grace_sec:
                    # Sesi selesai resmi
                    duration = self.last_seen - self.session_start
                    completed_session = {
                        "table_name": self.name,
                        "start_time": self.session_start,
                        "end_time": self.last_seen,
                        "duration_sec": duration,
                    }
                    # Reset status ke KOSONG
                    self.state = KOSONG
                    self.first_seen = None
                    self.last_seen = None
                    self.session_start = None

            elif self.state == KOSONG and self.first_seen is not None:
                # Orang sempat terdeteksi sebentar (< min_dwell_sec) lalu pergi
                if self.last_seen is not None and (now - self.last_seen) > self.leave_grace_sec:
                    # Reset tanpa mencatat sesi (false positive / orang hanya lewat)
                    self.first_seen = None
                    self.last_seen = None

        return completed_session


class TableTracker:
    """Pengelola pelacakan okupansi seluruh meja di restoran.

    Args:
        tables_cfg: dict nama meja dan koordinat poligon:
                    {"Meja 1": [(x1,y1), (x2,y2), ...], "Meja 2": [...]}
        min_dwell_sec: ambang minimum duduk untuk mencatat sesi resmi (detik)
        leave_grace_sec: toleransi deteksi hilang sesaat (detik)
    """

    def __init__(
        self,
        tables_cfg: dict[str, list[tuple[int | float, int | float]]],
        min_dwell_sec: float = 30.0,
        leave_grace_sec: float = 20.0,
    ):
        self.tables: dict[str, Table] = {
            name: Table(
                name=name,
                polygon=polygon,
                min_dwell_sec=min_dwell_sec,
                leave_grace_sec=leave_grace_sec,
            )
            for name, polygon in tables_cfg.items()
        }

    def update(
        self,
        detections: list[tuple[int, tuple[int | float, int | float]]],
        now: float,
    ) -> list[dict]:
        """Perbarui status seluruh meja.

        Returns:
            list sesi duduk yang selesai pada frame ini:
            [{"table_name": str, "start_time": float, "end_time": float, "duration_sec": float}, ...]
        """
        finished_sessions = []
        for table in self.tables.values():
            session = table.update(detections, now)
            if session:
                finished_sessions.append(session)
        return finished_sessions

    def get_status(self) -> dict:
        """Kembalikan ringkasan okupansi saat ini.

        Returns:
            dict: {
                "occupied": int,
                "total": int,
                "tables": {table_name: "KOSONG"|"TERISI", ...}
            }
        """
        table_states = {name: t.state for name, t in self.tables.items()}
        occupied_count = sum(1 for state in table_states.values() if state == TERISI)
        return {
            "occupied": occupied_count,
            "total": len(self.tables),
            "tables": table_states,
        }

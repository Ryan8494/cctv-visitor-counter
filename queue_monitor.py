"""
queue_monitor.py — Logika murni monitor zona antrean dan waktu tunggu.

Modul ini TIDAK mengimpor cv2, ultralytics, atau modul berat lainnya.
Input berupa ID, posisi titik pusat, dan waktu; output berupa event alert.

Zona antrean didefinisikan sebagai poligon. Tiap ID di dalam zona dicatat
waktu masuknya. Alert dikirim saat jumlah orang atau waktu tunggu melewati
batas, dengan cooldown agar tidak berulang tiap frame.
"""

from __future__ import annotations


# ── Nama event alert ───────────────────────────────────────────

ALERT_ANTREAN_PANJANG = "ALERT_ANTREAN_PANJANG"
ALERT_TUNGGU_LAMA = "ALERT_TUNGGU_LAMA"


def _point_in_polygon(
    point: tuple[int | float, int | float],
    polygon: list[tuple[int | float, int | float]],
) -> bool:
    """Cek apakah titik berada di dalam poligon (ray casting algorithm).

    Args:
        point: (x, y)
        polygon: list titik poligon [(x1,y1), (x2,y2), ...]

    Returns:
        True jika titik di dalam poligon
    """
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


class QueueMonitor:
    """Monitor antrean di zona tertentu.

    Args:
        zone_polygon: poligon zona antrean [(x1,y1), (x2,y2), ...]
        max_people: ambang jumlah orang untuk alert ALERT_ANTREAN_PANJANG
        max_wait_sec: ambang waktu tunggu (detik) untuk alert ALERT_TUNGGU_LAMA
        alert_cooldown_sec: cooldown antar alert sejenis (detik)
        lost_grace_sec: toleransi hilangnya deteksi sebelum ID dianggap pergi
    """

    def __init__(
        self,
        zone_polygon: list[tuple[int | float, int | float]],
        max_people: int = 5,
        max_wait_sec: float = 120.0,
        alert_cooldown_sec: float = 60.0,
        lost_grace_sec: float = 3.0,
    ):
        self.zone_polygon = zone_polygon
        self.max_people = max_people
        self.max_wait_sec = max_wait_sec
        self.alert_cooldown_sec = alert_cooldown_sec
        self.lost_grace_sec = lost_grace_sec

        # Waktu masuk zona per ID
        self._enter_time: dict[int, float] = {}
        # Waktu terakhir terlihat di zona per ID
        self._last_seen: dict[int, float] = {}
        # Waktu alert terakhir per jenis alert
        self._last_alert_time: dict[str, float] = {}

    def update(
        self,
        detections: list[tuple[int, tuple[int | float, int | float]]],
        now: float,
    ) -> list[dict]:
        """Perbarui status antrean berdasarkan deteksi frame saat ini.

        Args:
            detections: list (track_id, (cx, cy)) untuk semua orang terdeteksi
            now: waktu saat ini dalam detik

        Returns:
            List alert yang dipicu, tiap alert berupa dict:
            {"event": str, "detail": str, "people": int, "max_wait": float}
        """
        alerts = []

        # Tentukan siapa yang ada di zona saat ini
        ids_in_zone = set()
        for track_id, center in detections:
            if _point_in_polygon(center, self.zone_polygon):
                ids_in_zone.add(track_id)
                self._last_seen[track_id] = now

                # Catat waktu masuk jika baru
                if track_id not in self._enter_time:
                    self._enter_time[track_id] = now

        # Hapus ID yang sudah lama tidak terlihat (melebihi grace period)
        stale_ids = []
        for track_id, last_t in self._last_seen.items():
            if track_id not in ids_in_zone and (now - last_t) > self.lost_grace_sec:
                stale_ids.append(track_id)

        for track_id in stale_ids:
            self._enter_time.pop(track_id, None)
            self._last_seen.pop(track_id, None)

        # Hitung jumlah orang di zona (termasuk yang dalam grace period)
        people_count = len(self._enter_time)

        # Hitung waktu tunggu terlama
        max_wait = 0.0
        if self._enter_time:
            max_wait = max(now - t for t in self._enter_time.values())

        # Cek alert antrean panjang
        if people_count >= self.max_people:
            if self._can_alert(ALERT_ANTREAN_PANJANG, now):
                self._last_alert_time[ALERT_ANTREAN_PANJANG] = now
                alerts.append({
                    "event": ALERT_ANTREAN_PANJANG,
                    "detail": f"{people_count} orang di zona antrean (batas: {self.max_people})",
                    "people": people_count,
                    "max_wait": max_wait,
                })

        # Cek alert waktu tunggu lama
        if max_wait >= self.max_wait_sec:
            if self._can_alert(ALERT_TUNGGU_LAMA, now):
                self._last_alert_time[ALERT_TUNGGU_LAMA] = now
                alerts.append({
                    "event": ALERT_TUNGGU_LAMA,
                    "detail": f"Waktu tunggu terlama: {max_wait:.0f}s (batas: {self.max_wait_sec:.0f}s)",
                    "people": people_count,
                    "max_wait": max_wait,
                })

        return alerts

    def _can_alert(self, event_name: str, now: float) -> bool:
        """Cek apakah alert boleh dikirim (sudah lewat cooldown)."""
        last = self._last_alert_time.get(event_name)
        if last is None:
            return True
        return (now - last) >= self.alert_cooldown_sec

    def get_status(self, now: float) -> dict:
        """Kembalikan status antrean saat ini.

        Returns:
            dict dengan 'people_count' dan 'max_wait_sec'
        """
        people_count = len(self._enter_time)
        max_wait = 0.0
        if self._enter_time:
            max_wait = max(now - t for t in self._enter_time.values())
        return {
            "people_count": people_count,
            "max_wait_sec": max_wait,
        }

    def get_wait_times(self, now: float) -> dict[int, float]:
        """Kembalikan waktu tunggu tiap ID yang ada di zona.

        Returns:
            dict {track_id: waktu_tunggu_detik}
        """
        return {tid: now - t for tid, t in self._enter_time.items()}

    def cleanup_old(self, now: float, max_age: float = 300.0):
        """Bersihkan data alert lama."""
        stale = [
            k for k, t in self._last_alert_time.items()
            if (now - t) > max_age
        ]
        for k in stale:
            self._last_alert_time.pop(k, None)

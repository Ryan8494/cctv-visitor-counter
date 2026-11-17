"""
line_counter.py — Logika murni penghitung garis masuk/keluar.

Modul ini TIDAK mengimpor cv2, ultralytics, atau modul berat lainnya.
Input berupa ID, posisi titik pusat, dan waktu; output berupa event.

Arah ditentukan dari tanda perkalian silang (cross product) posisi
titik pusat orang relatif terhadap garis virtual, sebelum dan sesudah
frame. Satu ID dihitung sekali per lintasan; cooldown mencegah
penghitungan berulang saat orang bergoyang di dekat garis.
"""

from __future__ import annotations


# ── Tipe event ─────────────────────────────────────────────────

EVENT_MASUK = "IN"
EVENT_KELUAR = "OUT"

# Cooldown default agar orang yang bergoyang di garis tidak terhitung berulang
DEFAULT_COOLDOWN_SEC = 2.0


class LineCounter:
    """Penghitung orang yang melintas garis virtual.

    Args:
        pt1: titik awal garis (x1, y1)
        pt2: titik akhir garis (x2, y2)
        in_direction: arah yang dihitung sebagai 'masuk'.
            'positive' — perkalian silang berubah dari negatif ke positif.
            'negative' — sebaliknya.
            Alias: 'down' = 'positive', 'up' = 'negative' (untuk garis
            horizontal, orang bergerak ke bawah biasanya positif).
        cooldown_sec: waktu minimum antar penghitungan untuk ID yang sama
    """

    def __init__(
        self,
        pt1: tuple[int, int],
        pt2: tuple[int, int],
        in_direction: str = "positive",
        cooldown_sec: float = DEFAULT_COOLDOWN_SEC,
    ):
        self.pt1 = pt1
        self.pt2 = pt2
        self.cooldown_sec = cooldown_sec

        # Normalisasi alias arah
        direction_map = {
            "positive": "positive",
            "negative": "negative",
            "down": "positive",
            "up": "negative",
        }
        self.in_direction = direction_map.get(in_direction, "positive")

        # Simpan posisi dan waktu terakhir per ID
        # _prev_side[track_id] = tanda cross product terakhir (+1 / -1)
        self._prev_side: dict[int, int] = {}
        # _last_cross_time[track_id] = waktu terakhir ID ini dihitung
        self._last_cross_time: dict[int, float] = {}

        # Penghitung total
        self.count_in = 0
        self.count_out = 0

    def _cross_sign(self, point: tuple[int | float, int | float]) -> int:
        """Hitung tanda perkalian silang titik terhadap garis.

        Perkalian silang 2D: (pt2 - pt1) × (point - pt1)
        Positif = titik di sisi kiri garis (atau bawah untuk garis horizontal LR).
        Negatif = sisi kanan (atau atas).
        Nol = tepat di garis.

        Returns:
            +1, -1, atau 0
        """
        dx_line = self.pt2[0] - self.pt1[0]
        dy_line = self.pt2[1] - self.pt1[1]
        dx_point = point[0] - self.pt1[0]
        dy_point = point[1] - self.pt1[1]

        cross = dx_line * dy_point - dy_line * dx_point

        if cross > 0:
            return 1
        elif cross < 0:
            return -1
        return 0

    def update(
        self,
        track_id: int,
        center: tuple[int | float, int | float],
        now: float,
    ) -> str | None:
        """Perbarui posisi satu orang dan cek apakah melintas garis.

        Args:
            track_id: ID pelacak unik untuk orang ini
            center: titik pusat bounding box (cx, cy)
            now: waktu saat ini dalam detik

        Returns:
            EVENT_MASUK ('IN') jika orang masuk,
            EVENT_KELUAR ('OUT') jika keluar,
            None jika tidak melintas.
        """
        current_side = self._cross_sign(center)

        # Abaikan jika tepat di garis
        if current_side == 0:
            return None

        prev_side = self._prev_side.get(track_id)
        self._prev_side[track_id] = current_side

        # Belum ada data sebelumnya, simpan saja
        if prev_side is None:
            return None

        # Tidak ada perubahan sisi — tidak melintas
        if prev_side == current_side:
            return None

        # Ada perubahan sisi — cek cooldown
        last_time = self._last_cross_time.get(track_id, -999)
        if (now - last_time) < self.cooldown_sec:
            return None

        # Tentukan arah lintasan
        # negatif -> positif = "positive" crossing
        # positif -> negatif = "negative" crossing
        if prev_side == -1 and current_side == 1:
            crossing = "positive"
        else:
            crossing = "negative"

        # Catat waktu lintasan
        self._last_cross_time[track_id] = now

        if crossing == self.in_direction:
            self.count_in += 1
            return EVENT_MASUK
        else:
            self.count_out += 1
            return EVENT_KELUAR

    def cleanup_old(self, now: float, max_age: float = 30.0):
        """Bersihkan data ID yang sudah lama tidak terlihat.

        Args:
            now: waktu saat ini
            max_age: usia maksimum data sebelum dihapus (detik)
        """
        stale_ids = [
            tid for tid, t in self._last_cross_time.items()
            if (now - t) > max_age
        ]
        for tid in stale_ids:
            self._prev_side.pop(tid, None)
            self._last_cross_time.pop(tid, None)

        # Bersihkan juga ID di prev_side yang belum pernah melintas
        # tapi sudah ada > max_age tanpa update
        all_tracked = set(self._prev_side.keys())
        counted = set(self._last_cross_time.keys())
        orphans = all_tracked - counted
        # Orphan tidak punya timestamp, bersihkan jika terlalu banyak
        if len(orphans) > 100:
            for tid in orphans:
                self._prev_side.pop(tid, None)

    def get_counts(self) -> dict[str, int]:
        """Kembalikan jumlah orang masuk dan keluar."""
        return {"in": self.count_in, "out": self.count_out}

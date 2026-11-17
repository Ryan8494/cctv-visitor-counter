"""
tests/test_line_counter.py — Uji logika penghitung garis.

Kasus uji sesuai AGENTS.md:
- Orang melintas masuk
- Orang melintas keluar
- Berdiri dekat garis tanpa melintas
- Dua orang bersamaan
- ID yang sama melintas bolak-balik
"""

import pytest
from line_counter import LineCounter, EVENT_MASUK, EVENT_KELUAR


@pytest.fixture
def counter():
    """Penghitung garis horizontal di y=400, dari x=0 ke x=1000.

    Dengan in_direction='down' (alias 'positive'), orang bergerak
    dari atas (y<400) ke bawah (y>400) dihitung sebagai MASUK.
    """
    return LineCounter(
        pt1=(0, 400),
        pt2=(1000, 400),
        in_direction="down",
        cooldown_sec=1.0,
    )


class TestMelintasMasuk:
    """Orang melintas dari atas ke bawah = MASUK."""

    def test_satu_orang_masuk(self, counter):
        # Frame 0: orang di atas garis
        result = counter.update(1, (500, 350), now=0.0)
        assert result is None  # belum ada data sebelumnya

        # Frame 1: orang sudah di bawah garis
        result = counter.update(1, (500, 450), now=1.0)
        assert result == EVENT_MASUK

        counts = counter.get_counts()
        assert counts["in"] == 1
        assert counts["out"] == 0


class TestMelintasKeluar:
    """Orang melintas dari bawah ke atas = KELUAR."""

    def test_satu_orang_keluar(self, counter):
        # Frame 0: orang di bawah garis
        result = counter.update(1, (500, 450), now=0.0)
        assert result is None

        # Frame 1: orang sudah di atas garis
        result = counter.update(1, (500, 350), now=1.0)
        assert result == EVENT_KELUAR

        counts = counter.get_counts()
        assert counts["in"] == 0
        assert counts["out"] == 1


class TestBerdiriDekatGaris:
    """Orang bergoyang di dekat garis tanpa benar-benar melintas
    (atau melintas tapi dalam cooldown)."""

    def test_goyang_dalam_cooldown(self, counter):
        """Orang melintas lalu kembali dalam cooldown — tidak dihitung dua kali."""
        counter.update(1, (500, 350), now=0.0)
        result1 = counter.update(1, (500, 450), now=0.5)
        assert result1 == EVENT_MASUK

        # Kembali ke atas dalam cooldown (< 1.0 detik)
        result2 = counter.update(1, (500, 350), now=0.8)
        assert result2 is None  # cooldown aktif

        counts = counter.get_counts()
        assert counts["in"] == 1
        assert counts["out"] == 0

    def test_tetap_di_satu_sisi(self, counter):
        """Orang tetap di satu sisi garis — tidak dihitung."""
        counter.update(1, (500, 350), now=0.0)
        result = counter.update(1, (500, 360), now=1.0)
        assert result is None

        result = counter.update(1, (500, 370), now=2.0)
        assert result is None

        counts = counter.get_counts()
        assert counts["in"] == 0
        assert counts["out"] == 0

    def test_tepat_di_garis(self, counter):
        """Orang tepat di garis (cross product = 0) — diabaikan."""
        counter.update(1, (500, 350), now=0.0)
        result = counter.update(1, (500, 400), now=1.0)  # tepat di garis
        assert result is None


class TestDuaOrangBersamaan:
    """Dua orang melintas di waktu bersamaan."""

    def test_dua_orang_masuk(self, counter):
        # Orang A dan B mulai di atas
        counter.update(1, (300, 350), now=0.0)
        counter.update(2, (700, 350), now=0.0)

        # Keduanya melintas ke bawah
        result_a = counter.update(1, (300, 450), now=1.0)
        result_b = counter.update(2, (700, 450), now=1.0)

        assert result_a == EVENT_MASUK
        assert result_b == EVENT_MASUK

        counts = counter.get_counts()
        assert counts["in"] == 2
        assert counts["out"] == 0

    def test_satu_masuk_satu_keluar(self, counter):
        # Orang A di atas, orang B di bawah
        counter.update(1, (300, 350), now=0.0)
        counter.update(2, (700, 450), now=0.0)

        # A turun (masuk), B naik (keluar)
        result_a = counter.update(1, (300, 450), now=1.0)
        result_b = counter.update(2, (700, 350), now=1.0)

        assert result_a == EVENT_MASUK
        assert result_b == EVENT_KELUAR

        counts = counter.get_counts()
        assert counts["in"] == 1
        assert counts["out"] == 1


class TestBolakBalik:
    """ID yang sama melintas bolak-balik (setelah cooldown)."""

    def test_masuk_lalu_keluar(self, counter):
        # Masuk
        counter.update(1, (500, 350), now=0.0)
        result1 = counter.update(1, (500, 450), now=1.0)
        assert result1 == EVENT_MASUK

        # Keluar (setelah cooldown)
        result2 = counter.update(1, (500, 350), now=3.0)
        assert result2 == EVENT_KELUAR

        counts = counter.get_counts()
        assert counts["in"] == 1
        assert counts["out"] == 1

    def test_tiga_kali_melintas(self, counter):
        # Masuk
        counter.update(1, (500, 350), now=0.0)
        r1 = counter.update(1, (500, 450), now=1.0)
        assert r1 == EVENT_MASUK

        # Keluar
        r2 = counter.update(1, (500, 350), now=3.0)
        assert r2 == EVENT_KELUAR

        # Masuk lagi
        r3 = counter.update(1, (500, 450), now=5.0)
        assert r3 == EVENT_MASUK

        counts = counter.get_counts()
        assert counts["in"] == 2
        assert counts["out"] == 1


class TestCleanup:
    """Pembersihan data lama."""

    def test_cleanup_old_ids(self, counter):
        counter.update(1, (500, 350), now=0.0)
        counter.update(1, (500, 450), now=1.0)  # melintas

        counter.cleanup_old(now=100.0, max_age=30.0)

        # Data ID 1 sudah dibersihkan, update berikutnya seperti baru
        result = counter.update(1, (500, 350), now=100.0)
        assert result is None  # belum ada data sebelumnya (sudah dibersihkan)

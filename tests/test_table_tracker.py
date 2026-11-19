"""
tests/test_table_tracker.py — Uji logika pelacak okupansi meja dan durasi duduk.

Kasus uji sesuai AGENTS.md & TODO.md Fase 4:
- Sesi duduk normal dan pencatatan durasi
- Orang lewat dekat meja (< min_dwell_sec) tidak dicatat sebagai sesi duduk
- Deteksi hilang sesaat (< leave_grace_sec) tidak memutus sesi
- Pergi dan datang lagi (dua sesi terpisah)
- Pelacakan beberapa meja bersamaan (okupansi total)
"""

import pytest
from table_tracker import Table, TableTracker, KOSONG, TERISI


@pytest.fixture
def single_table():
    """Meja tunggal 100x100 dengan min_dwell=30s dan leave_grace=20s."""
    return Table(
        name="Meja 1",
        polygon=[(100, 100), (200, 100), (200, 200), (100, 200)],
        min_dwell_sec=30.0,
        leave_grace_sec=20.0,
    )


class TestSesiDudukNormal:
    """Orang duduk melebihi min_dwell_sec, lalu pergi."""

    def test_sesi_duduk_lengkap(self, single_table):
        # 1. Mulai duduk di t=0
        res = single_table.update([(1, (150, 150))], now=0.0)
        assert res is None
        assert single_table.state == KOSONG  # Belum >= min_dwell_sec

        # 2. Masih duduk di t=20 (< 30s)
        res = single_table.update([(1, (150, 150))], now=20.0)
        assert res is None
        assert single_table.state == KOSONG

        # 3. Masih duduk di t=30 (>= min_dwell_sec 30s) -> Status TERISI
        res = single_table.update([(1, (150, 150))], now=30.0)
        assert res is None
        assert single_table.state == TERISI

        # 4. Duduk sampai t=120
        res = single_table.update([(1, (150, 150))], now=120.0)
        assert res is None
        assert single_table.state == TERISI

        # 5. Orang pergi di t=120. Pada t=130 (< grace 20s), belum dianggap selesai
        res = single_table.update([], now=130.0)
        assert res is None
        assert single_table.state == TERISI

        # 6. Pada t=141 (> grace 20s sejak 120s), sesi selesai dicatat!
        res = single_table.update([], now=141.0)
        assert res is not None
        assert res["table_name"] == "Meja 1"
        assert res["start_time"] == 0.0
        assert res["end_time"] == 120.0
        assert res["duration_sec"] == 120.0
        assert single_table.state == KOSONG


class TestOrangHanyaLewat:
    """Orang lewat di poligon meja < min_dwell_sec tidak dicatat sebagai sesi duduk."""

    def test_orang_lewat_sebentar(self, single_table):
        # Orang terdeteksi di meja pada t=0
        single_table.update([(1, (150, 150))], now=0.0)
        # Masih di meja pada t=10
        single_table.update([(1, (150, 150))], now=10.0)

        # Orang sudah lewat/keluar meja pada t=15 (< 30s)
        single_table.update([], now=15.0)

        # Setelah grace period berlalu di t=40
        res = single_table.update([], now=40.0)
        assert res is None  # Tidak ada sesi yang dicatat
        assert single_table.state == KOSONG

        # Orang baru duduk nantinya mulai bersih dari t=100
        single_table.update([(2, (150, 150))], now=100.0)
        assert single_table.first_seen == 100.0


class TestDeteksiHilangSesaat:
    """Orang hilang sesaat (< leave_grace_sec) tidak memutuskan sesi duduk."""

    def test_flicker_oklusi(self, single_table):
        # Duduk sampai status TERISI
        single_table.update([(1, (150, 150))], now=0.0)
        single_table.update([(1, (150, 150))], now=35.0)
        assert single_table.state == TERISI

        # Hilang selama 10 detik (misal terhalang pelayan lewat)
        res = single_table.update([], now=45.0)
        assert res is None
        assert single_table.state == TERISI

        # Muncul kembali di t=50 (< 20s grace period)
        res = single_table.update([(1, (150, 150))], now=50.0)
        assert res is None
        assert single_table.state == TERISI

        # Duduk berlanjut sampai t=100
        single_table.update([(1, (150, 150))], now=100.0)

        # Pergi di t=100, selesai di t=125 (> grace 20s)
        res = single_table.update([], now=125.0)
        assert res is not None
        assert res["duration_sec"] == 100.0  # Durasi dari 0 sampai 100


class TestPergiDanDatangLagi:
    """Dua sesi terpisah pada meja yang sama."""

    def test_dua_sesi_terpisah(self, single_table):
        # Sesi 1: t=0 s.d. t=60
        single_table.update([(1, (150, 150))], now=0.0)
        single_table.update([(1, (150, 150))], now=60.0)
        sesi1 = single_table.update([], now=85.0)  # Selesai
        assert sesi1 is not None
        assert sesi1["duration_sec"] == 60.0

        # Meja kosong sebentar
        single_table.update([], now=100.0)

        # Sesi 2: t=150 s.d. t=250
        single_table.update([(2, (150, 150))], now=150.0)
        single_table.update([(2, (150, 150))], now=185.0)  # TERISI
        assert single_table.state == TERISI
        single_table.update([(2, (150, 150))], now=250.0)
        sesi2 = single_table.update([], now=275.0)  # Selesai
        assert sesi2 is not None
        assert sesi2["start_time"] == 150.0
        assert sesi2["end_time"] == 250.0
        assert sesi2["duration_sec"] == 100.0


class TestMultiTableTracker:
    """Pengujian TableTracker dengan beberapa meja sekaligus."""

    def test_multi_table_occupancy(self):
        cfg = {
            "Meja A": [(0, 0), (50, 0), (50, 50), (0, 50)],
            "Meja B": [(100, 100), (150, 100), (150, 150), (100, 150)],
        }
        tracker = TableTracker(cfg, min_dwell_sec=10.0, leave_grace_sec=5.0)

        status_awal = tracker.get_status()
        assert status_awal["total"] == 2
        assert status_awal["occupied"] == 0

        # Orang duduk di Meja A
        tracker.update([(1, (25, 25))], now=0.0)
        tracker.update([(1, (25, 25))], now=15.0)

        status_setelah_duduk = tracker.get_status()
        assert status_setelah_duduk["occupied"] == 1
        assert status_setelah_duduk["tables"]["Meja A"] == TERISI
        assert status_setelah_duduk["tables"]["Meja B"] == KOSONG

        # Orang duduk juga di Meja B
        tracker.update([(1, (25, 25)), (2, (125, 125))], now=20.0)
        tracker.update([(1, (25, 25)), (2, (125, 125))], now=35.0)

        status_penuh = tracker.get_status()
        assert status_penuh["occupied"] == 2
        assert status_penuh["tables"]["Meja A"] == TERISI
        assert status_penuh["tables"]["Meja B"] == TERISI

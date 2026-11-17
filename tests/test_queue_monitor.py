"""
tests/test_queue_monitor.py — Uji logika monitor antrean.

Kasus uji sesuai AGENTS.md:
- Antrean di bawah ambang (tanpa alert)
- Jumlah orang melewati ambang (alert sekali)
- Waktu tunggu melewati batas
- Cooldown alert
- ID hilang sesaat kurang dari lost_grace_sec
"""

import pytest
from queue_monitor import QueueMonitor, ALERT_ANTREAN_PANJANG, ALERT_TUNGGU_LAMA


@pytest.fixture
def monitor():
    """Monitor antrean dengan zona persegi 100x100 dan ambang rendah untuk uji."""
    return QueueMonitor(
        zone_polygon=[(0, 0), (100, 0), (100, 100), (0, 100)],
        max_people=3,
        max_wait_sec=10.0,
        alert_cooldown_sec=5.0,
        lost_grace_sec=2.0,
    )


class TestDiBawahAmbang:
    """Antrean di bawah ambang — tidak ada alert."""

    def test_satu_orang_tanpa_alert(self, monitor):
        detections = [(1, (50, 50))]
        alerts = monitor.update(detections, now=0.0)
        assert alerts == []

    def test_dua_orang_tanpa_alert(self, monitor):
        detections = [(1, (30, 30)), (2, (70, 70))]
        alerts = monitor.update(detections, now=0.0)
        assert alerts == []

    def test_orang_di_luar_zona(self, monitor):
        """Orang di luar zona tidak dihitung."""
        detections = [(1, (200, 200)), (2, (300, 300))]
        alerts = monitor.update(detections, now=0.0)
        assert alerts == []

        status = monitor.get_status(now=0.0)
        assert status["people_count"] == 0

    def test_kosong(self, monitor):
        alerts = monitor.update([], now=0.0)
        assert alerts == []


class TestAlertAntreanPanjang:
    """Alert saat jumlah orang ≥ max_people."""

    def test_alert_saat_penuh(self, monitor):
        """3 orang (= max_people) → alert sekali."""
        detections = [(1, (10, 10)), (2, (50, 50)), (3, (90, 90))]
        alerts = monitor.update(detections, now=0.0)

        assert len(alerts) == 1
        assert alerts[0]["event"] == ALERT_ANTREAN_PANJANG
        assert alerts[0]["people"] == 3

    def test_alert_lebih_dari_ambang(self, monitor):
        """4 orang (> max_people) → alert."""
        detections = [
            (1, (10, 10)), (2, (30, 30)),
            (3, (50, 50)), (4, (70, 70)),
        ]
        alerts = monitor.update(detections, now=0.0)

        assert len(alerts) == 1
        assert alerts[0]["event"] == ALERT_ANTREAN_PANJANG
        assert alerts[0]["people"] == 4


class TestAlertWaktuTunggu:
    """Alert saat waktu tunggu ≥ max_wait_sec."""

    def test_tunggu_lama(self, monitor):
        # Orang masuk zona
        monitor.update([(1, (50, 50))], now=0.0)

        # Waktu berlalu kurang dari ambang — belum alert
        alerts = monitor.update([(1, (50, 50))], now=5.0)
        assert not any(a["event"] == ALERT_TUNGGU_LAMA for a in alerts)

        # Waktu berlalu = ambang (10 detik) — alert
        alerts = monitor.update([(1, (50, 50))], now=10.0)
        assert any(a["event"] == ALERT_TUNGGU_LAMA for a in alerts)


class TestCooldownAlert:
    """Alert punya cooldown — tidak berulang tiap frame."""

    def test_alert_tidak_berulang(self, monitor):
        detections = [(1, (10, 10)), (2, (50, 50)), (3, (90, 90))]

        # Alert pertama
        alerts1 = monitor.update(detections, now=0.0)
        assert len(alerts1) == 1

        # Frame berikutnya masih penuh — tidak alert (cooldown)
        alerts2 = monitor.update(detections, now=1.0)
        assert not any(a["event"] == ALERT_ANTREAN_PANJANG for a in alerts2)

        # Masih dalam cooldown (< 5 detik)
        alerts3 = monitor.update(detections, now=4.0)
        assert not any(a["event"] == ALERT_ANTREAN_PANJANG for a in alerts3)

    def test_alert_setelah_cooldown(self, monitor):
        detections = [(1, (10, 10)), (2, (50, 50)), (3, (90, 90))]

        # Alert pertama
        alerts1 = monitor.update(detections, now=0.0)
        assert len(alerts1) == 1

        # Setelah cooldown (≥ 5 detik) — alert lagi
        alerts2 = monitor.update(detections, now=5.0)
        assert any(a["event"] == ALERT_ANTREAN_PANJANG for a in alerts2)


class TestLostGrace:
    """ID hilang sesaat (< lost_grace_sec) tetap dianggap ada."""

    def test_hilang_sesaat_masih_dihitung(self, monitor):
        """Orang hilang < 2 detik masih dianggap di zona."""
        # Orang masuk zona
        monitor.update([(1, (50, 50))], now=0.0)

        # Orang hilang dari deteksi selama 1 detik (< grace 2 detik)
        monitor.update([], now=1.0)

        status = monitor.get_status(now=1.0)
        assert status["people_count"] == 1  # masih dihitung

    def test_hilang_lama_dihapus(self, monitor):
        """Orang hilang > lost_grace_sec dianggap pergi."""
        monitor.update([(1, (50, 50))], now=0.0)

        # Hilang lebih dari 2 detik grace period
        monitor.update([], now=3.0)

        status = monitor.get_status(now=3.0)
        assert status["people_count"] == 0

    def test_kembali_sebelum_grace_habis(self, monitor):
        """Orang kembali sebelum grace habis — waktu tunggu berlanjut."""
        monitor.update([(1, (50, 50))], now=0.0)
        monitor.update([], now=1.0)  # hilang

        # Kembali sebelum grace habis
        monitor.update([(1, (50, 50))], now=1.5)

        # Waktu tunggu berlanjut dari waktu masuk awal (0.0)
        wait_times = monitor.get_wait_times(now=5.0)
        assert 1 in wait_times
        assert wait_times[1] == pytest.approx(5.0, abs=0.1)


class TestGetStatus:
    """Fungsi get_status."""

    def test_status_kosong(self, monitor):
        status = monitor.get_status(now=0.0)
        assert status["people_count"] == 0
        assert status["max_wait_sec"] == 0.0

    def test_status_dengan_orang(self, monitor):
        monitor.update([(1, (50, 50))], now=0.0)
        monitor.update([(1, (50, 50)), (2, (70, 70))], now=5.0)

        status = monitor.get_status(now=10.0)
        assert status["people_count"] == 2
        assert status["max_wait_sec"] == pytest.approx(10.0, abs=0.1)

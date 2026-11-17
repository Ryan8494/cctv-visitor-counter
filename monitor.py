"""
monitor.py — Program utama: baca video, deteksi + pelacakan orang,
panggil modul logika penghitung garis dan monitor antrean, simpan ke database.

Impor berat (cv2, ultralytics) dilakukan di dalam fungsi agar modul logika
tetap bisa diuji tanpa dependensi berat.
"""

from __future__ import annotations

import json
import os
import sys
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def load_config(path: str = "config.json") -> dict:
    """Muat konfigurasi dari file JSON."""
    config_path = os.path.join(os.path.dirname(__file__), path)
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def run():
    """Fungsi utama: baca video, deteksi, lacak, hitung, dan simpan."""
    # Impor berat di dalam fungsi
    import cv2
    from ultralytics import YOLO

    from line_counter import LineCounter
    from queue_monitor import QueueMonitor
    from db import init_db, save_visit, save_queue_sample, save_event
    from notifier import send_alert

    # Muat konfigurasi
    config = load_config()

    source = config["source"]
    line_cfg = config["line"]
    zone_polygon = [tuple(p) for p in config["queue_zone"]]
    db_path = config.get("db_path", "data.db")
    yolo_model = config.get("yolo_model", "yolov8n.pt")
    confidence = config.get("confidence", 0.4)
    tracker_cfg = config.get("tracker", "bytetrack.yaml")
    sample_interval = config.get("queue_sample_interval_sec", 30)

    # Inisialisasi database
    conn = init_db(db_path)

    # Inisialisasi model YOLO
    logger.info(f"Memuat model YOLO: {yolo_model}")
    model = YOLO(yolo_model)

    # Inisialisasi penghitung garis
    counter = LineCounter(
        pt1=tuple(line_cfg["pt1"]),
        pt2=tuple(line_cfg["pt2"]),
        in_direction=line_cfg.get("in_direction", "down"),
    )

    # Inisialisasi monitor antrean
    queue_mon = QueueMonitor(
        zone_polygon=zone_polygon,
        max_people=config.get("queue_max_people", 5),
        max_wait_sec=config.get("queue_max_wait_sec", 120),
        alert_cooldown_sec=config.get("alert_cooldown_sec", 60),
        lost_grace_sec=config.get("lost_grace_sec", 3),
    )

    # Buka sumber video
    logger.info(f"Membuka sumber video: {source}")
    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        logger.error(f"Gagal membuka sumber video: {source}")
        sys.exit(1)

    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    logger.info(f"FPS video: {fps}")

    frame_idx = 0
    last_sample_time = -999.0

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                logger.info("Video selesai atau stream terputus.")
                break

            # Hitung waktu berdasarkan frame index / fps (untuk video file)
            now = frame_idx / fps

            # Deteksi dan pelacakan dengan YOLO
            results = model.track(
                frame,
                persist=True,
                conf=confidence,
                classes=[0],  # kelas 0 = person di COCO
                tracker=tracker_cfg,
                verbose=False,
            )

            # Proses hasil deteksi
            detections = []  # untuk queue_monitor: list (track_id, (cx, cy))

            if results and results[0].boxes is not None and results[0].boxes.id is not None:
                boxes = results[0].boxes
                for i in range(len(boxes)):
                    track_id = int(boxes.id[i])
                    x1, y1, x2, y2 = boxes.xyxy[i].tolist()
                    cx = (x1 + x2) / 2
                    cy = (y1 + y2) / 2

                    # Perbarui penghitung garis
                    event = counter.update(track_id, (cx, cy), now)
                    if event:
                        ts_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        save_visit(conn, event, ts_str)
                        logger.info(f"Lintasan terdeteksi: ID={track_id} arah={event}")

                    detections.append((track_id, (cx, cy)))

            # Perbarui monitor antrean
            alerts = queue_mon.update(detections, now)
            for alert in alerts:
                ts_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                save_event(conn, alert["event"], alert["detail"], ts_str)
                send_alert(alert["event"], alert["detail"])
                logger.warning(f"ALERT: {alert['event']} — {alert['detail']}")

            # Simpan sampel antrean secara periodik
            if (now - last_sample_time) >= sample_interval:
                status = queue_mon.get_status(now)
                ts_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                save_queue_sample(
                    conn,
                    status["people_count"],
                    status["max_wait_sec"],
                    ts_str,
                )
                last_sample_time = now

            # Visualisasi (opsional, tampilkan jika ada display)
            annotated = _draw_overlay(frame, counter, queue_mon, now,
                                      line_cfg, zone_polygon, results)
            cv2.imshow("Monitor Pengunjung", annotated)

            # Tekan 'q' untuk keluar
            if cv2.waitKey(1) & 0xFF == ord('q'):
                logger.info("Dihentikan oleh pengguna (tombol 'q').")
                break

            # Bersihkan data lama secara periodik
            if frame_idx % (int(fps) * 30) == 0:
                counter.cleanup_old(now)
                queue_mon.cleanup_old(now)

            frame_idx += 1

    except KeyboardInterrupt:
        logger.info("Dihentikan oleh pengguna (Ctrl+C).")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        conn.close()
        counts = counter.get_counts()
        logger.info(f"Total — Masuk: {counts['in']}, Keluar: {counts['out']}")


def _draw_overlay(frame, counter, queue_mon, now, line_cfg, zone_polygon, results):
    """Gambar overlay visualisasi di frame.

    Menggambar garis virtual, zona antrean, penghitung, dan bounding box.
    """
    import cv2
    import numpy as np

    annotated = frame.copy()

    # Gambar garis virtual (hijau)
    pt1 = tuple(line_cfg["pt1"])
    pt2 = tuple(line_cfg["pt2"])
    cv2.line(annotated, pt1, pt2, (0, 255, 0), 2)

    # Gambar zona antrean (biru, transparan)
    zone_pts = np.array(zone_polygon, dtype=np.int32)
    overlay = annotated.copy()
    cv2.fillPoly(overlay, [zone_pts], (255, 150, 0))
    cv2.addWeighted(overlay, 0.3, annotated, 0.7, 0, annotated)
    cv2.polylines(annotated, [zone_pts], True, (255, 150, 0), 2)

    # Gambar bounding box dan ID
    if results and results[0].boxes is not None and results[0].boxes.id is not None:
        boxes = results[0].boxes
        for i in range(len(boxes)):
            track_id = int(boxes.id[i])
            x1, y1, x2, y2 = [int(v) for v in boxes.xyxy[i].tolist()]
            cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 255), 2)
            cv2.putText(annotated, f"ID:{track_id}", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)

    # Tampilkan penghitung
    counts = counter.get_counts()
    status = queue_mon.get_status(now)
    info_lines = [
        f"Masuk: {counts['in']}  Keluar: {counts['out']}",
        f"Antrean: {status['people_count']} orang",
        f"Tunggu maks: {status['max_wait_sec']:.0f}s",
    ]
    for i, text in enumerate(info_lines):
        y = 30 + i * 30
        cv2.putText(annotated, text, (10, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    return annotated


if __name__ == "__main__":
    run()

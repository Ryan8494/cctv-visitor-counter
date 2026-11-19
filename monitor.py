"""
monitor.py — Program utama: baca video, deteksi + pelacakan orang,
panggil modul logika penghitung garis, monitor antrean, dan okupansi meja,
serta simpan ke database SQLite.

Impor berat (cv2, ultralytics) dilakukan di dalam fungsi agar modul logika
tetap bisa diuji tanpa dependensi berat.
"""

from __future__ import annotations

import json
import os
import sys
import logging
from datetime import datetime, timedelta

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
    from table_tracker import TableTracker
    from db import (
        init_db,
        save_visit,
        save_queue_sample,
        save_queue_visit,
        save_table_session,
        save_occupancy_sample,
        save_event,
    )
    from notifier import send_alert

    # Muat konfigurasi
    config = load_config()

    source = config["source"]
    line_cfg = config["line"]
    zone_polygon = [tuple(p) for p in config["queue_zone"]]
    tables_cfg = {
        name: [tuple(p) for p in poly]
        for name, poly in config.get("tables", {}).items()
    }

    db_path = config.get("db_path", "data.db")
    yolo_model = config.get("yolo_model", "yolov8n.pt")
    confidence = config.get("confidence", 0.4)
    tracker_cfg = config.get("tracker", "bytetrack.yaml")

    queue_sample_interval = config.get("queue_sample_interval_sec", 30)
    occ_sample_interval = config.get("occupancy_sample_interval_sec", 60)

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
        min_dwell_sec=config.get("queue_min_dwell_sec", 5),
    )

    # Inisialisasi pelacak meja
    table_tracker = TableTracker(
        tables_cfg=tables_cfg,
        min_dwell_sec=config.get("table_min_dwell_sec", 30),
        leave_grace_sec=config.get("table_leave_grace_sec", 20),
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
    last_queue_sample_time = -999.0
    last_occ_sample_time = -999.0
    run_start_time = datetime.now()

    def sec_to_ts(sec: float) -> str:
        return (run_start_time + timedelta(seconds=sec)).strftime("%Y-%m-%d %H:%M:%S")

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

            # Proses hasil deteksi: list (track_id, (cx, cy))
            detections = []

            if results and results[0].boxes is not None and results[0].boxes.id is not None:
                boxes = results[0].boxes
                for i in range(len(boxes)):
                    track_id = int(boxes.id[i])
                    x1, y1, x2, y2 = boxes.xyxy[i].tolist()
                    cx = (x1 + x2) / 2
                    cy = (y1 + y2) / 2

                    # 1. Perbarui penghitung garis
                    event = counter.update(track_id, (cx, cy), now)
                    if event:
                        ts_str = sec_to_ts(now)
                        save_visit(conn, event, ts_str)
                        logger.info(f"Lintasan terdeteksi: ID={track_id} arah={event}")

                    detections.append((track_id, (cx, cy)))

            # 2. Perbarui monitor antrean
            alerts = queue_mon.update(detections, now)
            for alert in alerts:
                ts_str = sec_to_ts(now)
                save_event(conn, alert["event"], alert["detail"], ts_str)
                send_alert(alert["event"], alert["detail"])
                logger.warning(f"ALERT: {alert['event']} — {alert['detail']}")

            # Simpan sesi kunjungan antrean yang selesai
            finished_queue_visits = queue_mon.pop_completed_visits()
            for visit in finished_queue_visits:
                save_queue_visit(
                    conn,
                    start_ts=sec_to_ts(visit["start_time"]),
                    end_ts=sec_to_ts(visit["end_time"]),
                    wait_sec=visit["wait_sec"],
                )
                logger.info(f"Antrean kasir selesai: ID={visit['track_id']} wait={visit['wait_sec']:.0f}s")

            # Simpan sampel antrean periodik
            if (now - last_queue_sample_time) >= queue_sample_interval:
                status = queue_mon.get_status(now)
                save_queue_sample(
                    conn,
                    status["people_count"],
                    status["max_wait_sec"],
                    sec_to_ts(now),
                )
                last_queue_sample_time = now

            # 3. Perbarui pelacak meja
            finished_table_sessions = table_tracker.update(detections, now)
            for session in finished_table_sessions:
                save_table_session(
                    conn,
                    table_name=session["table_name"],
                    start_ts=sec_to_ts(session["start_time"]),
                    end_ts=sec_to_ts(session["end_time"]),
                    duration_sec=session["duration_sec"],
                )
                logger.info(f"Sesi meja selesai: {session['table_name']} durasi={session['duration_sec']:.0f}s")

            # Simpan sampel okupansi meja periodik
            if (now - last_occ_sample_time) >= occ_sample_interval:
                occ_status = table_tracker.get_status()
                save_occupancy_sample(
                    conn,
                    occupied=occ_status["occupied"],
                    total=occ_status["total"],
                    ts=sec_to_ts(now),
                )
                last_occ_sample_time = now

            # 4. Visualisasi
            annotated = _draw_overlay(
                frame=frame,
                counter=counter,
                queue_mon=queue_mon,
                table_tracker=table_tracker,
                now=now,
                line_cfg=line_cfg,
                zone_polygon=zone_polygon,
                tables_cfg=tables_cfg,
                results=results,
            )
            cv2.imshow("Monitor Restoran & Pengunjung", annotated)

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


def _draw_overlay(
    frame,
    counter,
    queue_mon,
    table_tracker,
    now,
    line_cfg,
    zone_polygon,
    tables_cfg,
    results,
):
    """Gambar overlay visualisasi di frame."""
    import cv2
    import numpy as np

    annotated = frame.copy()

    # 1. Gambar garis virtual pintu (hijau)
    pt1 = tuple(line_cfg["pt1"])
    pt2 = tuple(line_cfg["pt2"])
    cv2.line(annotated, pt1, pt2, (0, 255, 0), 2)
    cv2.putText(annotated, "Pintu Masuk", (pt1[0], pt1[1] - 8),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # 2. Gambar zona antrean (oranye transparan)
    zone_pts = np.array(zone_polygon, dtype=np.int32)
    overlay = annotated.copy()
    cv2.fillPoly(overlay, [zone_pts], (255, 150, 0))
    cv2.addWeighted(overlay, 0.3, annotated, 0.7, 0, annotated)
    cv2.polylines(annotated, [zone_pts], True, (255, 150, 0), 2)
    cv2.putText(annotated, "Kasir", (zone_pts[0][0], zone_pts[0][1] - 8),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 150, 0), 2)

    # 3. Gambar poligon meja-meja pengunjung
    table_status = table_tracker.get_status()["tables"]
    for name, pts in tables_cfg.items():
        t_pts = np.array(pts, dtype=np.int32)
        is_occupied = table_status.get(name) == "TERISI"
        color = (0, 165, 255) if is_occupied else (0, 255, 0)  # oranye jika terisi, hijau jika kosong

        table_overlay = annotated.copy()
        cv2.fillPoly(table_overlay, [t_pts], color)
        cv2.addWeighted(table_overlay, 0.25 if is_occupied else 0.15, annotated, 0.75 if is_occupied else 0.85, 0, annotated)
        cv2.polylines(annotated, [t_pts], True, color, 2)

        cx = int(sum(p[0] for p in pts) / len(pts))
        cy = int(sum(p[1] for p in pts) / len(pts))
        cv2.putText(annotated, f"{name}: {table_status.get(name, 'KOSONG')}",
                    (cx - 40, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

    # 4. Gambar bounding box dan ID orang
    if results and results[0].boxes is not None and results[0].boxes.id is not None:
        boxes = results[0].boxes
        for i in range(len(boxes)):
            track_id = int(boxes.id[i])
            x1, y1, x2, y2 = [int(v) for v in boxes.xyxy[i].tolist()]
            cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 255), 2)
            cv2.putText(annotated, f"ID:{track_id}", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)

    # 5. Tampilkan panel informasi di pojok kiri atas
    counts = counter.get_counts()
    q_status = queue_mon.get_status(now)
    t_status = table_tracker.get_status()

    info_lines = [
        f"Pintu  : Masuk {counts['in']} | Keluar {counts['out']}",
        f"Antrean: {q_status['people_count']} org | Tunggu {q_status['max_wait_sec']:.0f}s",
        f"Meja   : {t_status['occupied']}/{t_status['total']} terisi",
    ]
    for i, text in enumerate(info_lines):
        y = 30 + i * 26
        # Background baris info
        cv2.putText(annotated, text, (12, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 0), 3)
        cv2.putText(annotated, text, (12, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)

    return annotated


if __name__ == "__main__":
    run()

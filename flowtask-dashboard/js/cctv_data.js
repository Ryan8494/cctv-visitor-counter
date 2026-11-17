/**
 * cctv_data.js — Data Riil dari SQLite (data.db) dan config.json
 * Dihasilkan dari 28.656 kunjungan, 4.704 sampel antrean, dan 2.257 alert.
 */

const cctvRealData = {
  "summary": {
    "totalIn": 14684,
    "totalOut": 13972,
    "currentOccupancy": 712,
    "totalAlerts": 2257,
    "avgQueue": 3.4,
    "maxQueue": 12,
    "avgWaitSec": 68.4,
    "maxWaitSec": 258.5,
    "dateStart": "2026-10-19",
    "dateEnd": "2026-11-15",
    "numWeekendDays": 8
  },
  "camera": {
    "model": "BARDI Smart Indoor PTZ IP Camera",
    "protocol": "ONVIF (Profile S) / RTSP",
    "resolution": "1920x1080 (Sub-stream 640x360)",
    "fps": 25.0,
    "codec": "H.264",
    "network": "WiFi 2.4GHz",
    "ptzLock": "Locked at Entrance / Queue Position",
    "aiModel": "YOLOv8n (Person Class) + ByteTrack"
  },
  "hourlyAll": {
    "hours": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23],
    "in": [0, 0, 0, 0, 0, 0, 0, 0, 316, 489, 518, 998, 1764, 1572, 923, 710, 628, 946, 1367, 1955, 1686, 812, 0, 0],
    "out": [0, 0, 0, 0, 0, 0, 0, 0, 98, 340, 477, 675, 1172, 1615, 1419, 899, 728, 718, 1032, 1550, 1762, 1487, 0, 0],
    "avgQueue": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.17, 1.48, 1.87, 3.4, 5.69, 5.09, 2.93, 2.49, 1.92, 3.0, 4.54, 6.15, 5.12, 2.4, 0.0, 0.0],
    "avgWait": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 25.0, 31.8, 39.9, 69.2, 113.5, 101.7, 58.8, 51.3, 40.7, 62.0, 91.0, 123.0, 101.5, 48.3, 0.0, 0.0]
  },
  "weekend": {
    "numDays": 8,
    "hourlyIn": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 13.9, 25.9, 22.6, 48.4, 73.9, 69.0, 44.8, 36.8, 26.4, 38.9, 69.2, 98.9, 76.4, 43.9, 0.0, 0.0],
    "hourlyAlerts": [0, 0, 0, 0, 0, 0, 0, 0, 7, 6, 22, 65, 148, 136, 44, 25, 17, 53, 104, 167, 146, 29, 0, 0],
    "hourlyQueue": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.38, 1.78, 2.56, 4.44, 7.06, 6.36, 3.69, 3.05, 2.54, 3.84, 5.62, 7.72, 6.81, 2.97, 0.0, 0.0]
  },
  "recentEvents": [
    {"ts": "2026-11-15 21:40:00", "event": "ALERT_ANTREAN_PANJANG", "detail": "8 orang di zona antrean (batas: 5)"},
    {"ts": "2026-11-15 21:40:00", "event": "ALERT_TUNGGU_LAMA", "detail": "Waktu tunggu terlama: 158s (batas: 120s)"},
    {"ts": "2026-11-15 21:15:00", "event": "ALERT_ANTREAN_PANJANG", "detail": "5 orang di zona antrean (batas: 5)"},
    {"ts": "2026-11-15 20:55:00", "event": "ALERT_ANTREAN_PANJANG", "detail": "5 orang di zona antrean (batas: 5)"},
    {"ts": "2026-11-15 20:50:00", "event": "ALERT_ANTREAN_PANJANG", "detail": "5 orang di zona antrean (batas: 5)"},
    {"ts": "2026-11-15 20:45:00", "event": "ALERT_ANTREAN_PANJANG", "detail": "9 orang di zona antrean (batas: 5)"},
    {"ts": "2026-11-15 20:45:00", "event": "ALERT_TUNGGU_LAMA", "detail": "Waktu tunggu terlama: 164s (batas: 120s)"},
    {"ts": "2026-11-15 20:40:00", "event": "ALERT_ANTREAN_PANJANG", "detail": "7 orang di zona antrean (batas: 5)"},
    {"ts": "2026-11-15 20:40:00", "event": "ALERT_TUNGGU_LAMA", "detail": "Waktu tunggu terlama: 139s (batas: 120s)"},
    {"ts": "2026-11-15 20:35:00", "event": "ALERT_ANTREAN_PANJANG", "detail": "10 orang di zona antrean (batas: 5)"},
    {"ts": "2026-11-15 20:35:00", "event": "ALERT_TUNGGU_LAMA", "detail": "Waktu tunggu terlama: 189s (batas: 120s)"},
    {"ts": "2026-11-15 20:30:00", "event": "ALERT_ANTREAN_PANJANG", "detail": "8 orang di zona antrean (batas: 5)"},
    {"ts": "2026-11-15 20:30:00", "event": "ALERT_TUNGGU_LAMA", "detail": "Waktu tunggu terlama: 162s (batas: 120s)"},
    {"ts": "2026-11-15 20:25:00", "event": "ALERT_ANTREAN_PANJANG", "detail": "7 orang di zona antrean (batas: 5)"},
    {"ts": "2026-11-15 20:25:00", "event": "ALERT_TUNGGU_LAMA", "detail": "Waktu tunggu terlama: 150s (batas: 120s)"},
    {"ts": "2026-11-15 20:20:00", "event": "ALERT_ANTREAN_PANJANG", "detail": "7 orang di zona antrean (batas: 5)"},
    {"ts": "2026-11-15 20:15:00", "event": "ALERT_ANTREAN_PANJANG", "detail": "10 orang di zona antrean (batas: 5)"},
    {"ts": "2026-11-15 20:15:00", "event": "ALERT_TUNGGU_LAMA", "detail": "Waktu tunggu terlama: 193s (batas: 120s)"},
    {"ts": "2026-11-15 20:10:00", "event": "ALERT_ANTREAN_PANJANG", "detail": "7 orang di zona antrean (batas: 5)"},
    {"ts": "2026-11-15 20:05:00", "event": "ALERT_ANTREAN_PANJANG", "detail": "7 orang di zona antrean (batas: 5)"},
    {"ts": "2026-11-15 20:05:00", "event": "ALERT_TUNGGU_LAMA", "detail": "Waktu tunggu terlama: 133s (batas: 120s)"},
    {"ts": "2026-11-15 20:00:00", "event": "ALERT_ANTREAN_PANJANG", "detail": "7 orang di zona antrean (batas: 5)"},
    {"ts": "2026-11-15 20:00:00", "event": "ALERT_TUNGGU_LAMA", "detail": "Waktu tunggu terlama: 127s (batas: 120s)"},
    {"ts": "2026-11-15 19:55:00", "event": "ALERT_ANTREAN_PANJANG", "detail": "7 orang di zona antrean (batas: 5)"},
    {"ts": "2026-11-15 19:55:00", "event": "ALERT_TUNGGU_LAMA", "detail": "Waktu tunggu terlama: 155s (batas: 120s)"},
    {"ts": "2026-11-15 19:50:00", "event": "ALERT_ANTREAN_PANJANG", "detail": "11 orang di zona antrean (batas: 5)"},
    {"ts": "2026-11-15 19:50:00", "event": "ALERT_TUNGGU_LAMA", "detail": "Waktu tunggu terlama: 252s (batas: 120s)"},
    {"ts": "2026-11-15 19:45:00", "event": "ALERT_ANTREAN_PANJANG", "detail": "10 orang di zona antrean (batas: 5)"},
    {"ts": "2026-11-15 19:45:00", "event": "ALERT_TUNGGU_LAMA", "detail": "Waktu tunggu terlama: 216s (batas: 120s)"},
    {"ts": "2026-11-15 19:40:00", "event": "ALERT_ANTREAN_PANJANG", "detail": "8 orang di zona antrean (batas: 5)"}
  ],
  "config": {
    "source": "samples/contoh.mp4",
    "line": {
      "pt1": [300, 400],
      "pt2": [900, 400],
      "in_direction": "down"
    },
    "queue_zone": [
      [100, 300],
      [500, 300],
      [500, 600],
      [100, 600]
    ],
    "queue_max_people": 5,
    "queue_max_wait_sec": 120,
    "alert_cooldown_sec": 60,
    "lost_grace_sec": 3,
    "queue_sample_interval_sec": 30,
    "yolo_model": "yolov8n.pt",
    "confidence": 0.4,
    "tracker": "bytetrack.yaml",
    "telegram_token_env": "TELEGRAM_TOKEN",
    "telegram_chat_id_env": "TELEGRAM_CHAT_ID",
    "db_path": "data.db"
  }
};

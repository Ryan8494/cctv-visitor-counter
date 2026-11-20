/**
 * cctv_data.js — Data Riil Komprehensif dari SQLite (data.db) dan config.json
 * Mencakup 3 Zona Restoran: Pintu Masuk, Antrean Kasir, dan Okupansi Meja Pengunjung
 */

const cctvRealData = {
  "summary": {
    "totalIn": 29588,
    "totalOut": 27929,
    "currentOccupancy": 1659,
    "totalAlerts": 4551,
    "alertBreakdown": {
      "ALERT_ANTREAN_PANJANG": 2971,
      "ALERT_TUNGGU_LAMA": 1580
    },
    "avgQueue": 3.37,
    "maxQueue": 12,
    "avgWaitSec": 68.6,
    "maxWaitSec": 261.8,
    "totalTableSessions": 10509,
    "avgTableDurationMin": 54.4,
    "tableOccupancyRate": 60.2,
    "totalTables": 2,
    "tableBreakdown": {
      "Meja 1": {
        "count": 5262,
        "avg_duration_min": 54.6
      },
      "Meja 2": {
        "count": 5247,
        "avg_duration_min": 54.1
      }
    },
    "totalQueueVisits": 9908,
    "avgQueueVisitWait": 45.1,
    "dateStart": "2026-10-19",
    "dateEnd": "2026-11-15",
    "totalDays": 28,
    "numWeekendDays": 8,
    "numWeekdayDays": 20
  },
  "camera": {
    "model": "BARDI Smart Indoor PTZ IP Camera",
    "protocol": "ONVIF (Profile S) / RTSP",
    "resolution": "1920x1080 (Sub-stream 640x360)",
    "fps": 25.0,
    "codec": "H.264",
    "network": "WiFi 2.4GHz",
    "ptzLock": "Terkunci (Posisi Fix: Pintu, Kasir & Meja Restoran)",
    "aiModel": "YOLOv8n (Person Class) + ByteTrack ID",
    "cameraNotice": "Pemberitahuan CCTV Terpasang (Sesuai UU PDP)"
  },
  "hourlyAll": {
    "in": [
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      585,
      924,
      1137,
      2050,
      3712,
      3185,
      1932,
      1432,
      1318,
      1801,
      2808,
      3695,
      3437,
      1572,
      0,
      0
    ],
    "out": [
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      144,
      584,
      912,
      1351,
      2277,
      3354,
      3003,
      1957,
      1471,
      1479,
      1932,
      2969,
      3439,
      3057,
      0,
      0
    ],
    "avgQueue": [
      0.0,
      0.0,
      0.0,
      0.0,
      0.0,
      0.0,
      0.0,
      0.0,
      1.15,
      1.51,
      1.97,
      3.42,
      5.75,
      5.02,
      2.93,
      2.42,
      1.88,
      2.97,
      4.45,
      6.22,
      5.0,
      2.44,
      0.0,
      0.0
    ],
    "avgWait": [
      0.0,
      0.0,
      0.0,
      0.0,
      0.0,
      0.0,
      0.0,
      0.0,
      25.0,
      33.1,
      41.6,
      69.5,
      115.4,
      100.4,
      59.1,
      50.6,
      39.7,
      60.9,
      89.5,
      125.3,
      100.3,
      49.8,
      0.0,
      0.0
    ],
    "occupancyRate": [
      0.0,
      0.0,
      0.0,
      0.0,
      0.0,
      0.0,
      0.0,
      0.0,
      16.8,
      28.0,
      38.1,
      62.8,
      94.0,
      89.0,
      55.5,
      48.1,
      38.8,
      54.9,
      81.5,
      98.4,
      89.9,
      46.7,
      0.0,
      0.0
    ],
    "alerts": [
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      22,
      33,
      86,
      280,
      793,
      623,
      203,
      134,
      69,
      199,
      475,
      881,
      613,
      140,
      0,
      0
    ]
  },
  "weekend": {
    "numDays": 8,
    "hourlyIn": [
      0.0,
      0.0,
      0.0,
      0.0,
      0.0,
      0.0,
      0.0,
      0.0,
      26.5,
      47.9,
      50.5,
      95.4,
      167.2,
      148.1,
      89.8,
      70.6,
      52.8,
      75.1,
      132.4,
      169.9,
      151.4,
      80.8,
      0.0,
      0.0
    ],
    "hourlyAlerts": [
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      12,
      12,
      48,
      137,
      307,
      273,
      93,
      56,
      30,
      104,
      212,
      332,
      276,
      73,
      0,
      0
    ],
    "hourlyQueue": [
      0.0,
      0.0,
      0.0,
      0.0,
      0.0,
      0.0,
      0.0,
      0.0,
      1.3,
      1.77,
      2.73,
      4.47,
      7.03,
      6.45,
      3.7,
      2.95,
      2.42,
      3.81,
      5.58,
      7.7,
      6.59,
      3.11,
      0.0,
      0.0
    ],
    "hourlyWait": [
      0.0,
      0.0,
      0.0,
      0.0,
      0.0,
      0.0,
      0.0,
      0.0,
      28.0,
      38.5,
      55.6,
      89.0,
      141.4,
      126.8,
      73.9,
      61.8,
      49.9,
      78.4,
      110.9,
      156.0,
      131.8,
      62.9,
      0.0,
      0.0
    ],
    "occupancyRate": [
      0.0,
      0.0,
      0.0,
      0.0,
      0.0,
      0.0,
      0.0,
      0.0,
      24.0,
      36.5,
      47.4,
      80.7,
      100.0,
      100.0,
      69.3,
      55.2,
      46.9,
      65.1,
      98.4,
      100.0,
      100.0,
      55.7,
      0.0,
      0.0
    ]
  },
  "weekday": {
    "numDays": 20,
    "hourlyIn": [
      0.0,
      0.0,
      0.0,
      0.0,
      0.0,
      0.0,
      0.0,
      0.0,
      18.6,
      27.1,
      36.6,
      64.3,
      118.7,
      100.0,
      60.7,
      43.4,
      44.8,
      60.0,
      87.5,
      116.8,
      111.3,
      46.3,
      0.0,
      0.0
    ],
    "hourlyAlerts": [
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      10,
      21,
      38,
      143,
      486,
      350,
      110,
      78,
      39,
      95,
      263,
      549,
      337,
      67,
      0,
      0
    ],
    "hourlyQueue": [
      0.0,
      0.0,
      0.0,
      0.0,
      0.0,
      0.0,
      0.0,
      0.0,
      1.09,
      1.41,
      1.67,
      3.0,
      5.24,
      4.45,
      2.62,
      2.21,
      1.66,
      2.64,
      3.99,
      5.62,
      4.36,
      2.17,
      0.0,
      0.0
    ],
    "hourlyWait": [
      0.0,
      0.0,
      0.0,
      0.0,
      0.0,
      0.0,
      0.0,
      0.0,
      23.8,
      30.9,
      36.0,
      61.7,
      105.0,
      89.8,
      53.2,
      46.2,
      35.6,
      54.0,
      81.0,
      113.0,
      87.7,
      44.5,
      0.0,
      0.0
    ],
    "occupancyRate": [
      0.0,
      0.0,
      0.0,
      0.0,
      0.0,
      0.0,
      0.0,
      0.0,
      14.0,
      24.6,
      34.4,
      55.6,
      91.7,
      84.6,
      50.0,
      45.2,
      35.6,
      50.8,
      74.8,
      97.7,
      85.8,
      43.1,
      0.0,
      0.0
    ]
  },
  "recentEvents": [
    {
      "ts": "2026-11-15 21:45:00",
      "event": "ALERT_ANTREAN_PANJANG",
      "detail": "6 orang di zona antrean (batas: 5)"
    },
    {
      "ts": "2026-11-15 21:45:00",
      "event": "ALERT_TUNGGU_LAMA",
      "detail": "Waktu tunggu terlama: 125s (batas: 120s)"
    },
    {
      "ts": "2026-11-15 21:40:00",
      "event": "ALERT_ANTREAN_PANJANG",
      "detail": "8 orang di zona antrean (batas: 5)"
    },
    {
      "ts": "2026-11-15 21:40:00",
      "event": "ALERT_TUNGGU_LAMA",
      "detail": "Waktu tunggu terlama: 158s (batas: 120s)"
    },
    {
      "ts": "2026-11-15 21:40:00",
      "event": "ALERT_ANTREAN_PANJANG",
      "detail": "5 orang di zona antrean (batas: 5)"
    },
    {
      "ts": "2026-11-15 21:30:00",
      "event": "ALERT_ANTREAN_PANJANG",
      "detail": "7 orang di zona antrean (batas: 5)"
    },
    {
      "ts": "2026-11-15 21:30:00",
      "event": "ALERT_TUNGGU_LAMA",
      "detail": "Waktu tunggu terlama: 127s (batas: 120s)"
    },
    {
      "ts": "2026-11-15 21:15:00",
      "event": "ALERT_ANTREAN_PANJANG",
      "detail": "5 orang di zona antrean (batas: 5)"
    },
    {
      "ts": "2026-11-15 21:05:00",
      "event": "ALERT_ANTREAN_PANJANG",
      "detail": "5 orang di zona antrean (batas: 5)"
    },
    {
      "ts": "2026-11-15 20:55:00",
      "event": "ALERT_ANTREAN_PANJANG",
      "detail": "5 orang di zona antrean (batas: 5)"
    },
    {
      "ts": "2026-11-15 20:55:00",
      "event": "ALERT_ANTREAN_PANJANG",
      "detail": "7 orang di zona antrean (batas: 5)"
    },
    {
      "ts": "2026-11-15 20:55:00",
      "event": "ALERT_TUNGGU_LAMA",
      "detail": "Waktu tunggu terlama: 157s (batas: 120s)"
    },
    {
      "ts": "2026-11-15 20:50:00",
      "event": "ALERT_ANTREAN_PANJANG",
      "detail": "5 orang di zona antrean (batas: 5)"
    },
    {
      "ts": "2026-11-15 20:45:00",
      "event": "ALERT_ANTREAN_PANJANG",
      "detail": "9 orang di zona antrean (batas: 5)"
    },
    {
      "ts": "2026-11-15 20:45:00",
      "event": "ALERT_TUNGGU_LAMA",
      "detail": "Waktu tunggu terlama: 164s (batas: 120s)"
    },
    {
      "ts": "2026-11-15 20:45:00",
      "event": "ALERT_ANTREAN_PANJANG",
      "detail": "7 orang di zona antrean (batas: 5)"
    },
    {
      "ts": "2026-11-15 20:45:00",
      "event": "ALERT_TUNGGU_LAMA",
      "detail": "Waktu tunggu terlama: 146s (batas: 120s)"
    },
    {
      "ts": "2026-11-15 20:40:00",
      "event": "ALERT_ANTREAN_PANJANG",
      "detail": "7 orang di zona antrean (batas: 5)"
    },
    {
      "ts": "2026-11-15 20:40:00",
      "event": "ALERT_TUNGGU_LAMA",
      "detail": "Waktu tunggu terlama: 139s (batas: 120s)"
    },
    {
      "ts": "2026-11-15 20:40:00",
      "event": "ALERT_ANTREAN_PANJANG",
      "detail": "7 orang di zona antrean (batas: 5)"
    },
    {
      "ts": "2026-11-15 20:35:00",
      "event": "ALERT_ANTREAN_PANJANG",
      "detail": "10 orang di zona antrean (batas: 5)"
    },
    {
      "ts": "2026-11-15 20:35:00",
      "event": "ALERT_TUNGGU_LAMA",
      "detail": "Waktu tunggu terlama: 189s (batas: 120s)"
    },
    {
      "ts": "2026-11-15 20:35:00",
      "event": "ALERT_ANTREAN_PANJANG",
      "detail": "6 orang di zona antrean (batas: 5)"
    },
    {
      "ts": "2026-11-15 20:30:00",
      "event": "ALERT_ANTREAN_PANJANG",
      "detail": "8 orang di zona antrean (batas: 5)"
    },
    {
      "ts": "2026-11-15 20:30:00",
      "event": "ALERT_TUNGGU_LAMA",
      "detail": "Waktu tunggu terlama: 162s (batas: 120s)"
    },
    {
      "ts": "2026-11-15 20:30:00",
      "event": "ALERT_ANTREAN_PANJANG",
      "detail": "9 orang di zona antrean (batas: 5)"
    },
    {
      "ts": "2026-11-15 20:30:00",
      "event": "ALERT_TUNGGU_LAMA",
      "detail": "Waktu tunggu terlama: 190s (batas: 120s)"
    },
    {
      "ts": "2026-11-15 20:25:00",
      "event": "ALERT_ANTREAN_PANJANG",
      "detail": "7 orang di zona antrean (batas: 5)"
    },
    {
      "ts": "2026-11-15 20:25:00",
      "event": "ALERT_TUNGGU_LAMA",
      "detail": "Waktu tunggu terlama: 150s (batas: 120s)"
    },
    {
      "ts": "2026-11-15 20:25:00",
      "event": "ALERT_ANTREAN_PANJANG",
      "detail": "6 orang di zona antrean (batas: 5)"
    }
  ],
  "config": {
    "source": "samples/contoh.mp4",
    "line": {
      "pt1": [
        300,
        400
      ],
      "pt2": [
        900,
        400
      ],
      "in_direction": "down"
    },
    "queue_zone": [
      [
        100,
        300
      ],
      [
        500,
        300
      ],
      [
        500,
        600
      ],
      [
        100,
        600
      ]
    ],
    "tables": {
      "table_1": [
        [
          600,
          150
        ],
        [
          900,
          150
        ],
        [
          900,
          400
        ],
        [
          600,
          400
        ]
      ],
      "table_2": [
        [
          600,
          450
        ],
        [
          900,
          450
        ],
        [
          900,
          700
        ],
        [
          600,
          700
        ]
      ]
    },
    "table_min_dwell_sec": 30,
    "table_leave_grace_sec": 20,
    "queue_max_people": 5,
    "queue_max_wait_sec": 120,
    "queue_min_dwell_sec": 5,
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

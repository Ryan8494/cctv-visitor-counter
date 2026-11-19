"""
tools/draw_zones.py — Alat bantu visual menggambar garis pintu, zona kasir,
dan poligon meja dari frame video/CCTV, lalu menyimpannya langsung ke config.json.

Jalankan:
    python tools/draw_zones.py [video_atau_screenshot]

Tombol Keyboard:
    [1] : Mode Garis Pintu Masuk (Klik 2 titik)
    [2] : Mode Zona Antrean Kasir (Klik titik poligon, min 3 titik)
    [3] : Mode Poligon Meja Pengunjung (Klik 4 titik per meja)
  [SPASI] : Pause / Resume video
    [s] : Simpan seluruh zona ke config.json
    [r] : Reset / batalkan titik yang sedang diklik
    [q] : Keluar
"""

import sys
import os
import json
import cv2
import numpy as np

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config.json")


def load_config() -> dict:
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_config(cfg: dict):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=4)
    print(f"\n[OK] Konfigurasi berhasil disimpan ke: {CONFIG_PATH}\n")


class ZoneDrawer:
    def __init__(self, source: str):
        self.source = source
        self.cfg = load_config()

        # Data zona dari config yang ada atau baru
        self.line_pt1 = self.cfg.get("line", {}).get("pt1")
        self.line_pt2 = self.cfg.get("line", {}).get("pt2")
        self.queue_zone = self.cfg.get("queue_zone", [])
        self.tables = self.cfg.get("tables", {})

        self.mode = "line"  # "line", "queue", "table"
        self.temp_points = []
        self.table_counter = len(self.tables) + 1

    def handle_click(self, x: int, y: int):
        pt = [int(x), int(y)]

        if self.mode == "line":
            if len(self.temp_points) == 0:
                self.temp_points.append(pt)
                print(f"[Pintu] Titik 1: {pt}")
            elif len(self.temp_points) == 1:
                self.line_pt1 = self.temp_points[0]
                self.line_pt2 = pt
                self.temp_points = []
                print(f"[Pintu] Selesai: pt1={self.line_pt1}, pt2={self.line_pt2}")

        elif self.mode == "queue":
            self.temp_points.append(pt)
            print(f"[Kasir] Tambah titik {len(self.temp_points)}: {pt} (Tekan 'c' untuk tutup poligon)")

        elif self.mode == "table":
            self.temp_points.append(pt)
            print(f"[Meja] Titik {len(self.temp_points)}/4: {pt}")
            if len(self.temp_points) == 4:
                name = f"Meja {self.table_counter}"
                self.tables[name] = list(self.temp_points)
                print(f"[Meja] {name} berhasil dibuat: {self.tables[name]}")
                self.table_counter += 1
                self.temp_points = []

    def close_queue_polygon(self):
        if len(self.temp_points) >= 3:
            self.queue_zone = list(self.temp_points)
            print(f"[Kasir] Poligon antrean selesai ({len(self.queue_zone)} titik).")
            self.temp_points = []
        else:
            print("[Kasir] Poligon butuh minimal 3 titik!")

    def export_config(self):
        if "line" not in self.cfg:
            self.cfg["line"] = {"in_direction": "down"}
        if self.line_pt1 and self.line_pt2:
            self.cfg["line"]["pt1"] = self.line_pt1
            self.cfg["line"]["pt2"] = self.line_pt2

        if self.queue_zone:
            self.cfg["queue_zone"] = self.queue_zone

        if self.tables:
            self.cfg["tables"] = self.tables

        save_config(self.cfg)


def main():
    source = sys.argv[1] if len(sys.argv) > 1 else None
    if not source:
        cfg = load_config()
        source = cfg.get("source", "samples/contoh.mp4")

    drawer = ZoneDrawer(source)

    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        print(f"Error: Gagal membuka video '{source}'")
        return

    window_name = "Alat Gambar Zona (1: Pintu, 2: Kasir, 3: Meja, SPASI: Pause, S: Simpan, Q: Keluar)"
    cv2.namedWindow(window_name)

    def mouse_callback(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            drawer.handle_click(x, y)

    cv2.setMouseCallback(window_name, mouse_callback)

    paused = False
    ret, frame = cap.read()
    if not ret:
        print("Gagal membaca frame video.")
        return

    print("\n=== PANDUAN MENGGAMBAR ZONA ===")
    print("Tekan [1] untuk Garis Pintu Masuk (klik 2 titik)")
    print("Tekan [2] untuk Poligon Kasir (klik titik poligon, tekan 'c' untuk tutup)")
    print("Tekan [3] untuk Poligon Meja (klik 4 titik per meja)")
    print("Tekan [SPASI] untuk Pause/Play video")
    print("Tekan [s] untuk Simpan ke config.json")
    print("Tekan [r] untuk Reset titik aktif")
    print("Tekan [q] untuk Keluar")
    print("================================\n")

    while True:
        if not paused:
            ret, next_frame = cap.read()
            if ret:
                frame = next_frame
            else:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

        disp = frame.copy()

        # 1. Gambar garis pintu
        if drawer.line_pt1 and drawer.line_pt2:
            cv2.line(disp, tuple(drawer.line_pt1), tuple(drawer.line_pt2), (0, 255, 0), 2)
            cv2.putText(disp, "Garis Pintu", tuple(drawer.line_pt1),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # 2. Gambar zona antrean kasir
        if len(drawer.queue_zone) >= 3:
            pts = np.array(drawer.queue_zone, dtype=np.int32)
            cv2.polylines(disp, [pts], True, (255, 150, 0), 2)
            cv2.putText(disp, "Zona Kasir", tuple(drawer.queue_zone[0]),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 150, 0), 2)

        # 3. Gambar meja-meja pengunjung
        for name, t_pts in drawer.tables.items():
            pts = np.array(t_pts, dtype=np.int32)
            cv2.polylines(disp, [pts], True, (0, 255, 255), 2)
            cx = int(sum(p[0] for p in t_pts) / len(t_pts))
            cy = int(sum(p[1] for p in t_pts) / len(t_pts))
            cv2.putText(disp, name, (cx - 30, cy),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

        # 4. Gambar titik sementara yang sedang diklik
        for pt in drawer.temp_points:
            cv2.circle(disp, tuple(pt), 5, (0, 0, 255), -1)
        if len(drawer.temp_points) > 1:
            cv2.polylines(disp, [np.array(drawer.temp_points, np.int32)], False, (0, 0, 255), 1)

        # Status mode di layar
        mode_text = f"Mode Aktif: [{drawer.mode.upper()}] (1: Pintu, 2: Kasir, 3: Meja)"
        cv2.putText(disp, mode_text, (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        cv2.imshow(window_name, disp)
        key = cv2.waitKey(30) & 0xFF

        if key == ord(' '):
            paused = not paused
        elif key == ord('1'):
            drawer.mode = "line"
            drawer.temp_points = []
            print(">> Berpindah ke Mode: Garis Pintu Masuk")
        elif key == ord('2'):
            drawer.mode = "queue"
            drawer.temp_points = []
            print(">> Berpindah ke Mode: Zona Kasir (Tekan 'c' setelah selesai)")
        elif key == ord('3'):
            drawer.mode = "table"
            drawer.temp_points = []
            print(">> Berpindah ke Mode: Poligon Meja")
        elif key == ord('c') and drawer.mode == "queue":
            drawer.close_queue_polygon()
        elif key == ord('r'):
            drawer.temp_points = []
            print("Titik aktif di-reset.")
        elif key == ord('s'):
            drawer.export_config()
        elif key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()

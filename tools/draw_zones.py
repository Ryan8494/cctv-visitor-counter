"""
tools/draw_zones.py — Alat bantu visual menggambar garis pintu, zona kasir,
dan poligon meja dari frame video/CCTV, lalu menyimpannya langsung ke config.json.

Jalankan:
    python tools/draw_zones.py [video_atau_screenshot]

Tombol Keyboard:
    [1] : Mode Garis Pintu Masuk (Klik 2 titik)
    [2] : Mode Zona Antrean Kasir (Klik titik poligon, tekan 'c' untuk tutup)
    [3] : Mode Poligon Meja Pengunjung (Klik 4 titik per meja)
  [SPASI] : Pause / Resume video
 [d] / [z]: Hapus / Undo (batal titik aktif, atau hapus garis/meja yang salah)
    [r] : Reset seluruh elemen pada mode aktif
    [s] : Simpan seluruh zona ke config.json
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
        self.status_msg = "Tekan [1] Pintu, [2] Kasir, [3] Meja | Klik Kiri: Gambar | Klik Kanan: Hapus"

    def set_status(self, msg: str):
        self.status_msg = msg

    def handle_click(self, x: int, y: int):
        pt = [int(x), int(y)]

        if self.mode == "line":
            if len(self.temp_points) == 0:
                self.temp_points.append(pt)
                self.set_status(f"[PINTU] Titik 1: {pt}. Klik titik ke-2.")
                print(f"[Pintu] Titik 1: {pt}")
            elif len(self.temp_points) == 1:
                self.line_pt1 = self.temp_points[0]
                self.line_pt2 = pt
                self.temp_points = []
                self.set_status(f"[PINTU] Garis selesai ({self.line_pt1} -> {self.line_pt2}).")
                print(f"[Pintu] Selesai: pt1={self.line_pt1}, pt2={self.line_pt2}")

        elif self.mode == "queue":
            self.temp_points.append(pt)
            self.set_status(f"[KASIR] Titik {len(self.temp_points)}: {pt}. Tekan 'c' jika selesai.")
            print(f"[Kasir] Tambah titik {len(self.temp_points)}: {pt} (Tekan 'c' untuk tutup poligon)")

        elif self.mode == "table":
            self.temp_points.append(pt)
            self.set_status(f"[MEJA {self.table_counter}] Titik {len(self.temp_points)}/4.")
            print(f"[Meja] Titik {len(self.temp_points)}/4: {pt}")
            if len(self.temp_points) == 4:
                name = f"Meja {self.table_counter}"
                self.tables[name] = list(self.temp_points)
                self.set_status(f"[MEJA] {name} berhasil dibuat! (Total: {len(self.tables)} meja)")
                print(f"[Meja] {name} berhasil dibuat: {self.tables[name]}")
                self.table_counter += 1
                self.temp_points = []

    def close_queue_polygon(self):
        if len(self.temp_points) >= 3:
            self.queue_zone = list(self.temp_points)
            self.set_status(f"[KASIR] Poligon antrean selesai ({len(self.queue_zone)} titik).")
            print(f"[Kasir] Poligon antrean selesai ({len(self.queue_zone)} titik).")
            self.temp_points = []
        else:
            self.set_status("[KASIR] Poligon butuh minimal 3 titik!")
            print("[Kasir] Poligon butuh minimal 3 titik!")

    def undo_or_delete(self):
        """Hapus titik sementara, atau hapus zona pada mode aktif."""
        if self.temp_points:
            self.temp_points = []
            self.set_status(f"[{self.mode.upper()}] Titik yang belum selesai dibatalkan.")
            print(f"[{self.mode.upper()}] Titik yang belum selesai dibatalkan.")
            return

        if self.mode == "line":
            if self.line_pt1 or self.line_pt2:
                self.line_pt1 = None
                self.line_pt2 = None
                self.set_status("[PINTU] Garis pintu berhasil dihapus.")
                print("[Pintu] Garis pintu dihapus.")
            else:
                self.set_status("[PINTU] Garis pintu sudah kosong.")
                print("[Pintu] Tidak ada garis pintu untuk dihapus.")

        elif self.mode == "queue":
            if self.queue_zone:
                self.queue_zone = []
                self.set_status("[KASIR] Poligon zona kasir dihapus.")
                print("[Kasir] Poligon zona kasir dihapus.")
            else:
                self.set_status("[KASIR] Zona kasir sudah kosong.")
                print("[Kasir] Tidak ada zona kasir untuk dihapus.")

        elif self.mode == "table":
            if self.tables:
                last_table, _ = self.tables.popitem()
                self.table_counter = max(1, len(self.tables) + 1)
                self.set_status(f"[MEJA] {last_table} berhasil dihapus. (Sisa: {len(self.tables)})")
                print(f"[Meja] {last_table} dihapus.")
            else:
                self.set_status("[MEJA] Tidak ada meja yang tersimpan.")
                print("[Meja] Tidak ada meja untuk dihapus.")

    def reset_current_mode(self):
        """Reset total elemen pada mode yang sedang aktif."""
        self.temp_points = []
        if self.mode == "line":
            self.line_pt1 = None
            self.line_pt2 = None
            self.set_status("[PINTU] Garis pintu berhasil di-reset (kosong).")
            print("[Pintu] Garis pintu berhasil di-reset.")
        elif self.mode == "queue":
            self.queue_zone = []
            self.set_status("[KASIR] Zona kasir berhasil di-reset (kosong).")
            print("[Kasir] Zona antrean kasir berhasil di-reset.")
        elif self.mode == "table":
            if self.tables:
                self.tables.clear()
                self.table_counter = 1
                self.set_status("[MEJA] SEMUA MEJA berhasil di-reset (kosong).")
                print("[Meja] Seluruh meja berhasil di-reset.")
            else:
                self.set_status("[MEJA] Meja sudah kosong.")
                print("[Meja] Tidak ada data meja.")

    def export_config(self):
        if "line" not in self.cfg:
            self.cfg["line"] = {"in_direction": "down"}
        self.cfg["line"]["pt1"] = self.line_pt1
        self.cfg["line"]["pt2"] = self.line_pt2
        self.cfg["queue_zone"] = self.queue_zone
        self.cfg["tables"] = self.tables

        save_config(self.cfg)
        self.set_status("[SUKSES] Seluruh koordinat berhasil disimpan ke config.json!")


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

    ret, frame = cap.read()
    if not ret:
        print("Gagal membaca frame video.")
        return

    window_name = "Alat Gambar Zona (1: Pintu, 2: Kasir, 3: Meja, SPASI: Pause, S: Simpan, Q: Keluar)"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    # Sesuaikan ukuran awal jendela agar pas di layar (tidak terpotong / zoom)
    h, w = frame.shape[:2]
    scale = min(1100 / w, 620 / h, 1.0)
    disp_w = int(w * scale)
    disp_h = int(h * scale)
    cv2.resizeWindow(window_name, disp_w, disp_h)

    def mouse_callback(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            drawer.handle_click(x, y)
        elif event == cv2.EVENT_RBUTTONDOWN:
            drawer.undo_or_delete()

    cv2.setMouseCallback(window_name, mouse_callback)

    paused = False

    print("\n=== PANDUAN MENGGAMBAR ZONA ===")
    print("Tekan [1] : Mode Garis Pintu Masuk (klik 2 titik)")
    print("Tekan [2] : Mode Poligon Kasir (klik titik poligon, tekan 'c' untuk tutup)")
    print("Tekan [3] : Mode Poligon Meja (klik 4 titik per meja)")
    print("Tekan [SPASI] : Pause/Play video")
    print("KLIK KANAN atau [d] / [Backspace] : Hapus titik / Hapus zona aktif")
    print("Tekan [r] : Reset total seluruh elemen pada mode aktif")
    print("Tekan [s] : Simpan seluruh zona ke config.json")
    print("Tekan [q] : Keluar")
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
            cv2.circle(disp, tuple(pt), 6, (0, 0, 255), -1)
        if len(drawer.temp_points) > 1:
            cv2.polylines(disp, [np.array(drawer.temp_points, np.int32)], False, (0, 0, 255), 2)

        # Status mode & petunjuk di layar dengan latar semi-transparan
        overlay = disp.copy()
        cv2.rectangle(overlay, (0, 0), (disp.shape[1], 105), (20, 20, 20), -1)
        cv2.addWeighted(overlay, 0.70, disp, 0.30, 0, disp)

        mode_color = (0, 255, 0) if drawer.mode == "line" else ((255, 180, 0) if drawer.mode == "queue" else (0, 255, 255))
        mode_text = f"Mode: [{drawer.mode.upper()}]  |  [1] Pintu  [2] Kasir  [3] Meja  |  [SPASI] Pause"
        hint_text = "Klik Kiri: Titik | Klik Kanan / [d]: Hapus | [c]: Tutup Kasir | [r]: Reset | [s]: Simpan | [q]: Keluar"
        cv2.putText(disp, mode_text, (20, 32), cv2.FONT_HERSHEY_SIMPLEX, 0.8, mode_color, 2)
        cv2.putText(disp, hint_text, (20, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.60, (255, 255, 255), 2)
        if drawer.status_msg:
            cv2.putText(disp, f">> {drawer.status_msg}", (20, 95), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 255), 2)

        cv2.imshow(window_name, disp)
        key = cv2.waitKey(30) & 0xFF

        # Konversi key ke karakter lowercase jika printable
        k_char = chr(key).lower() if (0 <= key < 256 and chr(key).isprintable()) else ''

        if key == 32 or k_char == ' ':
            paused = not paused
            drawer.set_status("Video DIJEDA (PAUSE)" if paused else "Video BERJALAN (PLAY)")
        elif k_char == '1':
            drawer.mode = "line"
            drawer.temp_points = []
            drawer.set_status("Mode PINTU aktif. Klik 2 titik garis.")
            print(">> Berpindah ke Mode: Garis Pintu Masuk")
        elif k_char == '2':
            drawer.mode = "queue"
            drawer.temp_points = []
            drawer.set_status("Mode KASIR aktif. Klik poligon antrean, lalu tekan 'c'.")
            print(">> Berpindah ke Mode: Zona Kasir (Tekan 'c' setelah selesai)")
        elif k_char == '3':
            drawer.mode = "table"
            drawer.temp_points = []
            drawer.set_status(f"Mode MEJA aktif ({len(drawer.tables)} meja tersimpan). Klik 4 titik per meja.")
            print(">> Berpindah ke Mode: Poligon Meja")
        elif k_char == 'c' and drawer.mode == "queue":
            drawer.close_queue_polygon()
        elif k_char in ('d', 'z') or key in (8, 127):  # 'd', 'z', Backspace, Delete
            drawer.undo_or_delete()
        elif k_char == 'r':
            drawer.reset_current_mode()
        elif k_char == 's':
            drawer.export_config()
        elif k_char == 'q' or key == 27:  # 'q' atau ESC
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()

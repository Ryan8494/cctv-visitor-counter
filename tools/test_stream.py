"""
tools/test_stream.py — Uji koneksi stream RTSP / ONVIF kamera BARDI.

Mengecek:
- Frame terbaca atau tidak
- Resolusi (lebar x tinggi)
- FPS video
- Codec stream
- Kestabilan penerimaan frame

Jalankan:
    python tools/test_stream.py [rtsp_url]
Contoh:
    python tools/test_stream.py rtsp://admin:password@192.168.1.50:554/live/ch0
"""

import sys
import os
import json
import time

try:
    import cv2
except ImportError:
    print("Error: OpenCV belum terpasang. Jalankan: pip install opencv-python")
    sys.exit(1)


def decode_fourcc(fourcc_int: int) -> str:
    """Decode integer fourcc ke 4 karakter kode codec."""
    try:
        return "".join([chr((int(fourcc_int) >> 8 * i) & 0xFF) for i in range(4)])
    except Exception:
        return "Unknown"


def main():
    if len(sys.argv) > 1:
        source = sys.argv[1]
    else:
        # Baca dari config.json jika ada
        cfg_path = os.path.join(os.path.dirname(__file__), "..", "config.json")
        if os.path.exists(cfg_path):
            with open(cfg_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                source = cfg.get("source", "samples/contoh.mp4")
        else:
            source = "samples/contoh.mp4"

    print("=" * 60)
    print("Pengujian Stream Kamera / Video CCTV")
    print(f"Sumber: {source}")
    print("=" * 60)

    start_connect = time.time()
    cap = cv2.VideoCapture(source)

    if not cap.isOpened():
        print("[GAGAL] Tidak dapat membuka sumber stream/video.")
        print("Periksa kembali:")
        print("1. Pastikan URL RTSP dan kredensial (user:password) benar.")
        print("2. Pastikan port RTSP (default: 554) terbuka dan tidak diblokir firewall.")
        print("3. Pastikan IP kamera dapat di-ping dari komputer ini.")
        return

    connect_time = time.time() - start_connect
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    fourcc_val = int(cap.get(cv2.CAP_PROP_FOURCC))
    codec_str = decode_fourcc(fourcc_val)

    print(f"[BERHASIL] Terhubung dalam {connect_time:.2f} detik")
    print(f"• Resolusi : {width} x {height}")
    print(f"• FPS      : {fps:.1f}")
    print(f"• Codec    : {codec_str} (fourcc: {fourcc_val})")

    # Uji pembacaan 30 frame untuk cek stabilitas
    print("\nMenguji pembacaan 30 frame...")
    success_frames = 0
    t0 = time.time()
    for _ in range(30):
        ret, frame = cap.read()
        if ret:
            success_frames += 1
        else:
            break

    elapsed = time.time() - t0
    real_fps = success_frames / elapsed if elapsed > 0 else 0

    print(f"• Frame sukses terbaca : {success_frames}/30")
    print(f"• FPS aktual           : {real_fps:.1f} fps")

    if success_frames == 30:
        print("\n[OK] Stream stabil dan siap digunakan untuk deteksi monitor.py!")
    else:
        print("\n[PERINGATAN] Ada frame yang terputus atau dropped. Periksa sinyal WiFi kamera.")

    cap.release()


if __name__ == "__main__":
    main()

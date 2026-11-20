"""
server.py — Dedicated Web Server untuk VisionCCTV Resto Dashboard

Menyajikan file dashboard langsung dari direktori flowtask-dashboard/ pada port 3000:
- Menggunakan ThreadingHTTPServer (multi-threaded) agar tidak ada request yang hang/memblokir browser.
- Mengatur daemon_threads = True dan allow_reuse_address = False.
- Otomatis membuka http://localhost:3000 di browser.
"""

import os
import sys
import webbrowser
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

PORT = 3000
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DASHBOARD_DIR = os.path.join(BASE_DIR, "flowtask-dashboard")


class DashboardHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DASHBOARD_DIR, **kwargs)

    def log_message(self, format, *args):
        # Format log konsol ringkas
        sys.stderr.write(f"[{self.log_date_time_string()}] {format % args}\n")


class ThreadingDashboardServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = False


def start_server():
    print("=" * 60)
    print("   [VISIONCCTV RESTO] - WEB DASHBOARD SERVER")
    print("=" * 60)
    print(f" Direktori : {DASHBOARD_DIR}")
    print(f" URL Utama : http://localhost:{PORT}")
    print("=" * 60)

    try:
        httpd = ThreadingDashboardServer(("0.0.0.0", PORT), DashboardHandler)
        print(f"[+] Server web aktif pada port {PORT}.")
        print("[+] Membuka http://localhost:3000 di browser...")
        try:
            webbrowser.open(f"http://localhost:{PORT}")
        except Exception:
            pass
        print("[+] Tekan Ctrl + C di terminal untuk menghentikan server.\n")
        httpd.serve_forever()

    except OSError as err:
        err_str = str(err).lower()
        if "10048" in err_str or "already in use" in err_str:
            print(f"[!] Peringatan: Port {PORT} sudah digunakan oleh proses lain.")
            print(f"[+] Membuka browser ke http://localhost:{PORT}...")
            try:
                webbrowser.open(f"http://localhost:{PORT}")
            except Exception:
                pass
        else:
            print(f"[-] Gagal menjalankan server: {err}")
    except KeyboardInterrupt:
        print("\n[+] Server web dihentikan oleh pengguna.")


if __name__ == "__main__":
    start_server()

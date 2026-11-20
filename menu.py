"""
menu.py — CLI Command Launcher Interaktif untuk Proyek VisionCCTV

Menyediakan antarmuka terminal sederhana agar pengguna dapat menjalankan
seluruh perintah utama, alat kalibrasi zona, pengujian, dan dashboard dengan
sekali tekan tombol tanpa harus menghafal perintah terminal.

Jalankan:
    python menu.py
"""

import os
import sys
import subprocess
import webbrowser
import socket


def is_port_in_use(port: int) -> bool:
    """Periksa apakah port lokal sedang aktif/digunakan."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) == 0


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def print_banner():
    print("=" * 66)
    print("      🎥 VISIONCCTV — PUSAT KONTROL & COMMAND LAUNCHER 🎥")
    print("=" * 66)
    print(" Pilih aksi yang ingin dijalankan:")
    print("  [1] 📹 Jalankan Deteksi CCTV & Pelacakan 3 Zona (monitor.py)")
    print("  [2] 📊 Jalankan Streamlit Dashboard Manajer (dashboard.py)")
    print("  [3] 🌐 Jalankan Web Dashboard Modern (Port 3000)")
    print("  [4] 🎨 Kalibrasi Garis Pintu, Kasir & Meja (draw_zones.py)")
    print("  [5] 📡 Uji Koneksi Stream RTSP Kamera BARDI (test_stream.py)")
    print("  [6] 🧪 Jalankan 35 Unit Test Otomatis (pytest)")
    print("  [7] 🎲 Isi Ulang Database dengan Simulasi 4 Minggu (simulate.py)")
    print("  [8] 🔍 Periksa Jumlah Data SQLite 6 Tabel (data.db)")
    print("  [9] ⚙️  Periksa Sintaks Seluruh File Python (py_compile)")
    print("  [10]📖 Buka File Dokumentasi Perintah (COMMANDS.md)")
    print("  [0] ❌ Keluar")
    print("=" * 66)


def main():
    while True:
        clear_screen()
        print_banner()
        try:
            choice = input(" Masukkan pilihan Anda [0-10]: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nKeluar dari menu.")
            break

        if choice == "1":
            print("\n[+] Menjalankan program deteksi CCTV (monitor.py)...")
            print("[+] Petunjuk: Tekan tombol 'q' pada jendela video untuk keluar.\n")
            try:
                subprocess.run([sys.executable, "monitor.py"])
            except KeyboardInterrupt:
                print("\nProgram deteksi dihentikan.")
            input("\nTekan Enter untuk kembali ke menu...")

        elif choice == "2":
            print("\n[+] Menjalankan Streamlit Dashboard...")
            print("[+] Tekan Ctrl + C di terminal untuk menghentikan Streamlit.\n")
            try:
                subprocess.run([sys.executable, "-m", "streamlit", "run", "dashboard.py"])
            except FileNotFoundError:
                print("[-] Error: 'streamlit' belum terpasang. Jalankan: pip install -r requirements.txt")
            except KeyboardInterrupt:
                print("\nStreamlit dihentikan.")
            input("\nTekan Enter untuk kembali ke menu...")

        elif choice == "3":
            print("\n[+] Menjalankan Web Dashboard Server (server.py)...")
            try:
                subprocess.run([sys.executable, "server.py"])
            except KeyboardInterrupt:
                print("\nServer web dihentikan.")
            input("\nTekan Enter untuk kembali ke menu...")

        elif choice == "4":
            print("\n[+] Membuka Alat Kalibrasi Zona Visual (draw_zones.py)...")
            print("[+] Tombol: [1] Pintu, [2] Kasir, [3] Meja, [SPASI] Pause, [s] Simpan, [q] Keluar\n")
            source = input(" Path video (tekan Enter untuk default 'samples/contoh.mp4'): ").strip()
            cmd = [sys.executable, "tools/draw_zones.py"]
            if source:
                cmd.append(source)
            try:
                subprocess.run(cmd)
            except KeyboardInterrupt:
                print("\nAlat gambar zona dihentikan.")
            input("\nTekan Enter untuk kembali ke menu...")

        elif choice == "5":
            print("\n[+] Pengujian Koneksi RTSP Kamera BARDI (test_stream.py)...")
            rtsp_url = input(" Masukkan URL RTSP (tekan Enter untuk baca dari config.json): ").strip()
            cmd = [sys.executable, "tools/test_stream.py"]
            if rtsp_url:
                cmd.append(rtsp_url)
            try:
                subprocess.run(cmd)
            except KeyboardInterrupt:
                print("\nPengujian stream dihentikan.")
            input("\nTekan Enter untuk kembali ke menu...")

        elif choice == "6":
            print("\n[+] Menjalankan 35 unit test otomatis (Garis, Kasir, Meja, Ringkasan)...\n")
            subprocess.run([sys.executable, "-m", "pytest", "tests/", "-v"])
            input("\nTekan Enter untuk kembali ke menu...")

        elif choice == "7":
            print("\n[+] Membuat data simulasi realistis 4 minggu ke data.db...\n")
            subprocess.run([sys.executable, "simulate.py"])
            input("\nTekan Enter untuk kembali ke menu...")

        elif choice == "8":
            print("\n[+] Memeriksa isi 6 tabel database data.db...\n")
            try:
                import sqlite3
                if not os.path.exists("data.db"):
                    print("[-] Database 'data.db' belum dibuat. Jalankan opsi [7] terlebih dahulu.")
                else:
                    conn = sqlite3.connect("data.db")
                    cur = conn.cursor()

                    tables = [
                        ("visits", "Kunjungan Pintu (IN/OUT)"),
                        ("table_sessions", "Sesi Duduk Meja Pengunjung"),
                        ("occupancy_samples", "Sampel Okupansi Meja Berkala"),
                        ("queue_samples", "Sampel Antrean Kasir Berkala"),
                        ("queue_visits", "Riwayat Kunjungan Antrean Kasir"),
                        ("events", "Log Alert & Kejadian Penting"),
                    ]

                    for tbl, desc in tables:
                        try:
                            cur.execute(f"SELECT COUNT(*) FROM {tbl}")
                            count = cur.fetchone()[0]
                            print(f"  • {desc:<35} : {count:,} baris")
                        except sqlite3.OperationalError:
                            print(f"  • {desc:<35} : (tabel belum ada)")

                    conn.close()
            except Exception as e:
                print(f"[-] Terjadi kesalahan saat membaca database: {e}")
            input("\nTekan Enter untuk kembali ke menu...")

        elif choice == "9":
            print("\n[+] Memeriksa integritas sintaks file Python (*.py)...\n")
            files = [f for f in os.listdir(".") if f.endswith(".py")]
            all_ok = True
            for f in files:
                res = subprocess.run([sys.executable, "-m", "py_compile", f], capture_output=True, text=True)
                if res.returncode == 0:
                    print(f"  [OK] {f}")
                else:
                    print(f"  [GAGAL] {f}: {res.stderr.strip()}")
                    all_ok = False
            if all_ok:
                print("\n[✓] Seluruh file Python lulus cek sintaks tanpa error!")
            input("\nTekan Enter untuk kembali ke menu...")

        elif choice == "10":
            print("\n[+] Membaca ringkasan COMMANDS.md...\n")
            if os.path.exists("COMMANDS.md"):
                with open("COMMANDS.md", "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    print("".join(lines[:45]))
                print("\n[i] Buka file 'COMMANDS.md' di editor untuk panduan selengkapnya.")
            else:
                print("[-] Berkas COMMANDS.md tidak ditemukan.")
            input("\nTekan Enter untuk kembali ke menu...")

        elif choice == "0":
            print("\nTerima kasih! Sampai jumpa.\n")
            break

        else:
            print("\n[-] Pilihan tidak valid. Silakan pilih angka 0 sampai 10.")
            input("\nTekan Enter untuk mencoba lagi...")


if __name__ == "__main__":
    main()

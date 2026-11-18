"""
menu.py — CLI Command Launcher Interaktif untuk Proyek VisionCCTV

Menyediakan antarmuka terminal sederhana agar pengguna dapat menjalankan
perintah-perintah utama proyek dengan sekali tekan tombol tanpa harus menghafal perintah.
Jalankan: python menu.py
"""

import os
import sys
import subprocess
import webbrowser


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def print_banner():
    print("=" * 62)
    print("      🎥 VISIONCCTV — PUSAT KONTROL & COMMAND LAUNCHER 🎥")
    print("=" * 62)
    print(" Pilih aksi yang ingin dijalankan:")
    print("  [1] 🌐 Jalankan Web Dashboard Modern (Port 3000)")
    print("  [2] 📊 Jalankan Streamlit Dashboard (dashboard.py)")
    print("  [3] 📹 Jalankan Deteksi CCTV & Pelacakan (monitor.py)")
    print("  [4] 🧪 Jalankan Unit Test Otomatis (pytest)")
    print("  [5] 🎲 Isi Ulang Database dengan Simulasi (simulate.py)")
    print("  [6] 🔍 Periksa Jumlah Data SQLite (data.db)")
    print("  [7] ⚙️  Periksa Sintaks Seluruh File Python (py_compile)")
    print("  [8] 📖 Buka File Dokumentasi Perintah (COMMANDS.md)")
    print("  [0] ❌ Keluar")
    print("=" * 62)


def main():
    while True:
        clear_screen()
        print_banner()
        try:
            choice = input(" Masukkan pilihan Anda [0-8]: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nKeluar dari menu.")
            break

        if choice == "1":
            print("\n[+] Menjalankan Web Dashboard pada port 3000...")
            print("[+] Membuka http://localhost:3000 di browser...")
            try:
                webbrowser.open("http://localhost:3000")
            except Exception:
                pass
            print("[+] Tekan Ctrl + C di terminal untuk menghentikan server web.\n")
            try:
                subprocess.run([sys.executable, "-m", "http.server", "3000"])
            except KeyboardInterrupt:
                print("\nServer web dihentikan.")
            input("\nTekan Enter untuk kembali ke menu...")

        elif choice == "2":
            print("\n[+] Menjalankan Streamlit Dashboard...")
            print("[+] Tekan Ctrl + C di terminal untuk menghentikan Streamlit.\n")
            try:
                subprocess.run(["streamlit", "run", "dashboard.py"])
            except FileNotFoundError:
                print("[-] Error: 'streamlit' belum terpasang. Jalankan: pip install -r requirements.txt")
            except KeyboardInterrupt:
                print("\nStreamlit dihentikan.")
            input("\nTekan Enter untuk kembali ke menu...")

        elif choice == "3":
            print("\n[+] Menjalankan program deteksi CCTV (monitor.py)...")
            print("[+] Petunjuk: Tekan tombol 'q' pada jendela video untuk keluar.\n")
            try:
                subprocess.run([sys.executable, "monitor.py"])
            except KeyboardInterrupt:
                print("\nProgram deteksi dihentikan.")
            input("\nTekan Enter untuk kembali ke menu...")

        elif choice == "4":
            print("\n[+] Menjalankan 24 unit test otomatis...\n")
            subprocess.run([sys.executable, "-m", "pytest", "tests/", "-v"])
            input("\nTekan Enter untuk kembali ke menu...")

        elif choice == "5":
            print("\n[+] Membuat data simulasi 4 minggu ke data.db...\n")
            subprocess.run([sys.executable, "simulate.py"])
            input("\nTekan Enter untuk kembali ke menu...")

        elif choice == "6":
            print("\n[+] Memeriksa isi database data.db...\n")
            try:
                import sqlite3
                if not os.path.exists("data.db"):
                    print("[-] Database 'data.db' belum dibuat. Jalankan opsi [5] terlebih dahulu.")
                else:
                    conn = sqlite3.connect("data.db")
                    cur = conn.cursor()
                    cur.execute("SELECT COUNT(*) FROM visits")
                    n_visits = cur.fetchone()[0]
                    cur.execute("SELECT COUNT(*) FROM queue_samples")
                    n_samples = cur.fetchone()[0]
                    cur.execute("SELECT COUNT(*) FROM events")
                    n_events = cur.fetchone()[0]
                    print(f"  • Total Lintasan Pengunjung (visits): {n_visits:,} baris")
                    print(f"  • Total Sampel Antrean (queue_samples): {n_samples:,} baris")
                    print(f"  • Total Alert Tercatat (events): {n_events:,} baris")
                    conn.close()
            except Exception as e:
                print(f"[-] Terjadi kesalahan saat membaca database: {e}")
            input("\nTekan Enter untuk kembali ke menu...")

        elif choice == "7":
            print("\n[+] Memeriksa sintaks file Python (*.py)...\n")
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
                print("\n[✓] Seluruh file Python lulus cek sintaks!")
            input("\nTekan Enter untuk kembali ke menu...")

        elif choice == "8":
            print("\n[+] Membaca ringkasan COMMANDS.md...\n")
            if os.path.exists("COMMANDS.md"):
                with open("COMMANDS.md", "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    # Tampilkan 35 baris pertama
                    print("".join(lines[:35]))
                print("\n[i] Buka file 'COMMANDS.md' di editor untuk panduan selengkapnya.")
            else:
                print("[-] Berkas COMMANDS.md tidak ditemukan.")
            input("\nTekan Enter untuk kembali ke menu...")

        elif choice == "0":
            print("\nTerima kasih! Sampai jumpa.\n")
            break

        else:
            print("\n[-] Pilihan tidak valid. Silakan pilih angka 0 sampai 8.")
            input("\nTekan Enter untuk mencoba lagi...")


if __name__ == "__main__":
    main()

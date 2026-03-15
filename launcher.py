"""
╔══════════════════════════════════════════════════════╗
║           SensorKamera — Main Launcher               ║
╚══════════════════════════════════════════════════════╝
Jalankan file ini untuk memilih mode yang diinginkan.
"""

import os
import sys
import subprocess

# ─── ANSI Color Codes ───────────────────────────────────────────────────────
R  = "\033[0m"        # Reset
B  = "\033[1m"        # Bold
DIM= "\033[2m"        # Dim
CY = "\033[96m"       # Cyan
YL = "\033[93m"       # Yellow
GR = "\033[92m"       # Green
RD = "\033[91m"       # Red
MG = "\033[95m"       # Magenta
BL = "\033[94m"       # Blue
BG = "\033[100m"      # Dark BG highlight

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def banner():
    print(f"""
{CY}{B}
  ███████╗███████╗███╗   ██╗███████╗ ██████╗ ██████╗ 
  ██╔════╝██╔════╝████╗  ██║██╔════╝██╔═══██╗██╔══██╗
  ███████╗█████╗  ██╔██╗ ██║███████╗██║   ██║██████╔╝
  ╚════██║██╔══╝  ██║╚██╗██║╚════██║██║   ██║██╔══██╗
  ███████║███████╗██║ ╚████║███████║╚██████╔╝██║  ██║
  ╚══════╝╚══════╝╚═╝  ╚═══╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝
{R}{DIM}           K A M E R A   &   V I S I   A I{R}
{CY}{'─'*55}{R}
""")

MENU_ITEMS = [
    {
        "key": "1",
        "icon": "🤟",
        "title": "SIBI Reader",
        "desc": "Deteksi Bahasa Isyarat Indonesia (A–Z)",
        "file": "sibi.py",
        "color": CY,
    },
    {
        "key": "2",
        "icon": "😄",
        "title": "Deteksi Emosi",
        "desc": "Baca ekspresi wajah secara real-time",
        "file": "emotion.py",
        "color": YL,
    },
    {
        "key": "3",
        "icon": "👤",
        "title": "Tambah Wajah",
        "desc": "Daftarkan wajah baru ke dataset",
        "file": "add_face.py",
        "color": GR,
    },
    {
        "key": "4",
        "icon": "🔍",
        "title": "Kenali Wajah",
        "desc": "Identifikasi wajah dari dataset",
        "file": "find_face.py",
        "color": BL,
    },
    {
        "key": "5",
        "icon": "✊",
        "title": "Jokowi",
        "desc": "Deteksi gestur Selamat / Berjuang / Sukses",
        "file": "jokowi.py",
        "color": MG,
    },
    {
        "key": "0",
        "icon": "🚪",
        "title": "Keluar",
        "desc": "Tutup launcher",
        "file": None,
        "color": RD,
    },
]

def print_menu():
    for item in MENU_ITEMS:
        c = item["color"]
        sep = f"{DIM}│{R}"
        print(f"  {c}{B}[{item['key']}]{R}  {item['icon']}  {c}{B}{item['title']:<18}{R} {sep} {DIM}{item['desc']}{R}")
    print(f"\n{CY}{'─'*55}{R}")

def run_module(filepath):
    """Jalankan file Python dalam direktori yang sama."""
    script = os.path.join(os.path.dirname(os.path.abspath(__file__)), filepath)
    if not os.path.exists(script):
        print(f"\n{RD}[ERROR]{R} File tidak ditemukan: {script}")
        input(f"\n{DIM}Tekan Enter untuk kembali...{R}")
        return
    print(f"\n{GR}[INFO]{R} Menjalankan {B}{filepath}{R} ...\n")
    try:
        subprocess.run([sys.executable, script], check=True)
    except KeyboardInterrupt:
        print(f"\n{YL}[INFO]{R} Dihentikan oleh pengguna.")
    except subprocess.CalledProcessError as e:
        print(f"\n{RD}[ERROR]{R} Program keluar dengan kode: {e.returncode}")
    input(f"\n{DIM}Tekan Enter untuk kembali ke menu...{R}")

def main():
    while True:
        clear()
        banner()
        print_menu()
        choice = input(f"\n{B}  Pilih menu [{CY}0{R}{B}–{CY}5{R}{B}]{R} : ").strip()

        if choice == "0":
            clear()
            print(f"\n{CY}Sampai jumpa! 👋{R}\n")
            sys.exit(0)

        matched = next((m for m in MENU_ITEMS if m["key"] == choice and m["file"]), None)
        if matched:
            clear()
            run_module(matched["file"])
        else:
            print(f"\n{RD}  Pilihan tidak valid.{R}")
            import time; time.sleep(1)

if __name__ == "__main__":
    main()
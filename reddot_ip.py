import os
import socket
import requests
import dns.resolver
from colorama import Fore, Style, init
from bs4 import BeautifulSoup
import collections

# Fix for compatibility issues in older Python versions
if not hasattr(collections, 'Callable'):
    import collections.abc
    collections.Callable = collections.abc.Callable

try:
    from core.utils import clear_screen, save_result, print_status
except ImportError:
    def clear_screen(): os.system('cls' if os.name == 'nt' else 'clear')
    def save_result(t, r): pass
    def print_status(m, s): print(f"[{s.upper()}] {m}")

init(autoreset=True)

class ReddotIP:
    # [FIX] Added 'target' argument to __init__ to match main engine
    def __init__(self, target):
        self.developer = "Deathnihilist"
        self.version = "2.2.0 (Grid Display Mode)"
        # Clean the target input immediately upon initialization
        self.target = target.replace("https://", "").replace("http://", "").split('/')[0]

    def banner(self):
        clear_screen()
        print(f"""{Fore.RED}
██████╗ ███████╗██████╗ ██████╗  ██████╗ ████████╗
██╔══██╗██╔════╝██╔══██╗██╔══██╗██╔═══██╗╚══██╔══╝
██████╔╝█████╗  ██║  ██║██║  ██║██║   ██║   ██║   
██╔══██╗██╔══╝  ██║  ██║██║  ██║██║   ██║   ██║   
██║  ██║███████╗██████╔╝██████╔╝╚██████╔╝   ██║   
╚═╝  ╚═╝╚══════╝╚═════╝ ╚═════╝  ╚═════╝    ╚═╝   {Fore.WHITE}      [ IP ORIGIN FINDER - BY {self.developer} ]{Fore.YELLOW}      [ VERSION: {self.version} | PURE RECON ]
        """)

    def check_cloudflare(self, domain):
        try:
            r = requests.head(f"http://{domain}", timeout=5)
            if 'cloudflare' in r.headers.get('Server', '').lower():
                return True
        except: pass
        return False

    def dns_recon(self, domain):
        ip_found = None
        print_status("Performing DNS Reconnaissance...", "info")
        try:
            ip_found = socket.gethostbyname(domain)
            print_status(f"Direct IP Resolution: {ip_found}", "success")
        except: pass
        return ip_found

    def reverse_ip_hunter(self, ip):
        """Mencari website tetangga dengan tampilan Grid matrix"""
        print_status(f"Scanning Server Neighbors on {ip}...", "info")
        try:
            url = f"https://api.hackertarget.com/reverseiplookup/?q={ip}"
            r = requests.get(url, timeout=10)
            
            if r.status_code == 200 and "API count exceeded" not in r.text and "No records" not in r.text:
                domains = r.text.strip().split('\n')
                print_status(f"Found {len(domains)} other websites on this server!\n", "success")
                
                # ===== GRID SYSTEM CONFIGURATION =====
                columns = 4          # Jumlah website menyamping
                col_width = 35       # Lebar tiap kolom (menjaga agar teks sejajar)
                
                print(Fore.CYAN, end="") # Set warna list menjadi Cyan
                
                # Looping untuk memotong list domain menjadi barisan (chunks)
                for i in range(0, len(domains), columns):
                    chunk = domains[i:i+columns]
                    # Gabungkan website dalam 1 baris, beri spasi ljust() agar rata
                    row_str = "".join(str(d).ljust(col_width) for d in chunk)
                    print(f"  {row_str}")
                    
                print(Style.RESET_ALL) # Kembalikan warna terminal ke asal
                # =====================================
                
                save_result(ip, f"Neighbors Found: {', '.join(domains)}")
            else:
                print(f"{Fore.YELLOW}[!] Server looks isolated or API limit reached.")
        except Exception as e:
            print_status(f"Neighbor Scan Error: {e}", "error")

    def run(self):
        is_cf = self.check_cloudflare(self.target)
        if is_cf:
            print(f"{Fore.RED}[!] Cloudflare Detected! Target is hiding. Initiating Deep DNS Scan...")
        else:
            print(f"{Fore.GREEN}[+] No Cloudflare detected. Target is exposed.")

        target_ip = self.dns_recon(self.target)
        
        if not is_cf and target_ip:
            self.reverse_ip_hunter(target_ip)
        elif is_cf:
            print(f"{Fore.YELLOW}[!] Bypassing techniques needed to find real IP before neighbor scan.")

        # --- [ PERBAIKAN DI SINI ] ---
        # Kirim IP yang ditemukan kembali ke Framework Utama (reddot.py)
        if target_ip:
            return [target_ip]
        return []

# Standalone execution block (for direct testing outside the framework)
if __name__ == "__main__":
    t = input(f"{Fore.WHITE}Target Domain (e.g. site.com): ")
    if t:
        scanner = ReddotIP(t)
        scanner.banner()
        scanner.run()
        print(f"\n{Fore.GREEN}[+] Scan Complete. Results in logs/ directory.")
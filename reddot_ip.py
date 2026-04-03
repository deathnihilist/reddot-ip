import os
import socket
import requests
import dns.resolver
from colorama import Fore, Style, init
from bs4 import BeautifulSoup

import collections
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
    def __init__(self):
        self.developer = "Deathnihilist"
        self.version = "2.1.0 (Shared Server Hunter)"

    def banner(self):
        clear_screen()
        print(f"""{Fore.RED}
██████╗ ███████╗██████╗ ██████╗  ██████╗ ████████╗
██╔══██╗██╔════╝██╔══██╗██╔══██╗██╔═══██╗╚══██╔══╝
██████╔╝█████╗  ██║  ██║██║  ██║██║   ██║   ██║   
██╔══██╗██╔══╝  ██║  ██║██║  ██║██║   ██║   ██║   
██║  ██║███████╗██████╔╝██████╔╝╚██████╔╝   ██║   
╚═╝  ╚═╝╚══════╝╚═════╝ ╚═════╝  ╚═════╝    ╚═╝   
{Fore.WHITE}      [ IP ORIGIN FINDER - BY {self.developer} ]
{Fore.YELLOW}      [ VERSION: {self.version} | PURE RECON ]
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
        """Mencari website tetangga di server yang sama untuk target Symlink"""
        print_status(f"Scanning Server Neighbors on {ip}...", "info")
        try:
            url = f"https://api.hackertarget.com/reverseiplookup/?q={ip}"
            r = requests.get(url, timeout=10)
            
            if r.status_code == 200 and "API count exceeded" not in r.text and "No records" not in r.text:
                domains = r.text.strip().split('\n')
                print_status(f"Found {len(domains)} other websites on this server!", "success")
                
                # Menampilkan 10 tetangga pertama agar terminal tidak banjir
                for d in domains[:10]:
                    print(f"{Fore.CYAN}   [+] Neighbor: {d}")
                
                if len(domains) > 10:
                    print(f"{Fore.YELLOW}   ... and {len(domains)-10} more. (Results saved to logs)")
                    
                save_result(ip, f"Neighbors Found: {', '.join(domains)}")
            else:
                print(f"{Fore.YELLOW}[!] Server looks isolated or API limit reached.")
        except Exception as e:
            print_status(f"Neighbor Scan Error: {e}", "error")

    def scan(self, target):
        target = target.replace("https://", "").replace("http://", "").split('/')[0]
        
        is_cf = self.check_cloudflare(target)
        if is_cf:
            print(f"{Fore.RED}[!] Cloudflare Detected! Target is hiding. Initiating Deep DNS Scan...")
        else:
            print(f"{Fore.GREEN}[+] No Cloudflare detected. Target is exposed.")

        # Ambil IP
        target_ip = self.dns_recon(target)
        
        # Kalau tidak pakai Cloudflare, langsung sikat tetangganya
        if not is_cf and target_ip:
            self.reverse_ip_hunter(target_ip)
        elif is_cf:
            print(f"{Fore.YELLOW}[!] Bypassing techniques needed to find real IP before neighbor scan.")

if __name__ == "__main__":
    scanner = ReddotIP()
    scanner.banner()
    target = input(f"{Fore.WHITE}Target Domain (e.g. site.com): ")
    if target:
        scanner.scan(target)
        print(f"\n{Fore.GREEN}[+] Scan Complete. Results in logs/ directory.")
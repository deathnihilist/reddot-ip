import os
import socket
import requests
import shodan
from censys.search import CensysHosts
from colorama import Fore, Style, init

# Mengambil fungsi gahar dari folder core/utils.py
try:
    from core.utils import clear_screen, save_result, print_status
except ImportError:
    # Fallback jika folder core belum terbaca di environment tertentu
    def clear_screen(): os.system('cls' if os.name == 'nt' else 'clear')
    def save_result(t, r): pass
    def print_status(m, s): print(f"[{s.upper()}] {m}")

# Inisialisasi warna untuk terminal Kali Linux
init(autoreset=True)

class ReddotIP:
    def __init__(self):
        self.developer = "Deathnihilist"
        self.version = "1.0.1"
        self.shodan_key = ""
        self.censys_id = ""
        self.censys_secret = ""

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
{Fore.YELLOW}      [ VERSION: {self.version} | FOR KALI LINUX ]
        """)

    def setup_api(self):
        print_status("Configuration Required (API Keys)", "warning")
        # Tips: Gunakan .strip() untuk membuang spasi yang tidak sengaja ter-copy
        self.shodan_key = input(f"{Fore.CYAN}Enter Shodan API Key: ").strip()
        self.censys_id = input(f"{Fore.CYAN}Enter Censys API ID: ").strip()
        self.censys_secret = input(f"{Fore.CYAN}Enter Censys API Secret: ").strip()
        print_status("API Keys Loaded Successfully!\n", "success")

    def scan_origin(self, target):
        # Membersihkan target dari http/https/slash agar tidak error
        target = target.replace("https://", "").replace("http://", "").split('/')[0]
        
        print_status(f"Initiating Predator Mode on: {target}", "info")
        
        # 1. DNS Resolution
        try:
            initial_ip = socket.gethostbyname(target)
            print(f"{Fore.WHITE}[-] Current Public IP: {initial_ip} (WAF/Proxy Detector)")
        except:
            print_status("Could not resolve initial DNS.", "error")

        # 2. Shodan Deep Search (Enhanced Query)
        print_status("Searching Shodan Database...", "info")
        try:
            api = shodan.Shodan(self.shodan_key)
            # Menggunakan query 'hostname' dan 'ssl' untuk mencari kebocoran
            results = api.search(f'hostname:"{target}"')
            if results['total'] > 0:
                for result in results['matches']:
                    found_ip = result['ip_str']
                    org = result.get('org', 'Unknown Organization')
                    print_status(f"Potential Origin IP Found: {found_ip} ({org})", "success")
                    save_result(target, f"Shodan Discovery: {found_ip}")
            else:
                print(f"{Fore.YELLOW}[!] No direct matches in Shodan for this hostname.")
        except Exception as e:
            print_status(f"Shodan Error: {e}", "error")

        # 3. Censys SSL Analysis (Bypass Logic v2 - 2026 Ready)
        print_status("Analyzing SSL Certificates via Censys...", "info")
        try:
            h = CensysHosts(api_id=self.censys_id, api_secret=self.censys_secret)
            # Mencari host yang menggunakan sertifikat dengan nama domain target
            query = f"services.tls.certificates.leaf_data.subject.common_name: `{target}`"
            
            # Mengambil hasil dari API v2
            search_results = h.search(query, per_page=5)
            for page in search_results:
                for host in page:
                    found_ip = host.get('ip')
                    if found_ip:
                        print_status(f"Origin IP Detected (SSL Match): {found_ip}", "success")
                        save_result(target, f"Censys SSL Match: {found_ip}")
        except Exception as e:
            print_status(f"Censys Error: {e}", "error")

        # 4. Shared Hosting Detection
        print_status("Checking for Shared Hosting Environment...", "info")
        try:
            res = requests.get(f"https://api.hackertarget.com/reverseiplookup/?q={target}", timeout=10).text
            if "No records" not in res and len(res.splitlines()) > 5:
                print(f"{Fore.MAGENTA}[ALERT] Target is on Shared Hosting. Results might show server-mate IPs.")
            else:
                print_status("Target seems to be on a Dedicated server.", "success")
        except:
            print_status("Reverse IP lookup failed.", "error")

if __name__ == "__main__":
    scanner = ReddotIP()
    scanner.banner()
    scanner.setup_api()
    target_input = input(f"{Fore.WHITE}Target Domain (e.g. site.com): ")
    
    if target_input:
        scanner.scan_origin(target_input)
        print(f"\n{Fore.GREEN}[+] Scan Complete. Check logs/ directory for details.")
    else:
        print_status("No target provided.", "error")
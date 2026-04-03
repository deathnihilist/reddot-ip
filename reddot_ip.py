import os
import socket
import requests
import shodan
from censys.search import CensysHosts
from colorama import Fore, Style, init
from bs4 import BeautifulSoup

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
        self.version = "1.1.0"
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
        self.shodan_key = input(f"{Fore.CYAN}Enter Shodan API Key: ").strip()
        self.censys_id = input(f"{Fore.CYAN}Enter Censys API ID: ").strip()
        self.censys_secret = input(f"{Fore.CYAN}Enter Censys API Secret: ").strip()
        print_status("API Keys Loaded Successfully!\n", "success")

    def is_using_cloudflare(self, domain):
        """Mendeteksi apakah website menggunakan Cloudflare (Taktik CloakQuest3r)"""
        try:
            response = requests.head(f"https://{domain}", timeout=5)
            headers = response.headers
            if "server" in headers and "cloudflare" in headers["server"].lower():
                return True
            if "cf-ray" in headers:
                return True
        except:
            pass
        return False

    def viewdns_history(self, domain):
        """Scraping IP History tanpa API dari ViewDNS (Taktik CloakQuest3r)"""
        print_status("Checking ViewDNS IP History (OSINT Mode)...", "info")
        try:
            url = f"https://viewdns.info/iphistory/?domain={domain}"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.102 Safari/537.36"
            }
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find('table', {'border': '1'})

            if table:
                rows = table.find_all('tr')[2:] # Lewati header tabel
                for row in rows:
                    columns = row.find_all('td')
                    ip_address = columns[0].text.strip()
                    owner = columns[2].text.strip()
                    
                    # Kita filter agar tidak memunculkan IP Cloudflare lagi
                    if "Cloudflare" not in owner:
                        print_status(f"Historical IP Found: {ip_address} (Owner: {owner})", "success")
                        save_result(domain, f"ViewDNS History: {ip_address} ({owner})")
            else:
                print(f"{Fore.YELLOW}[!] No historical records found on ViewDNS.")
        except Exception as e:
            print_status(f"ViewDNS Error: {e}", "error")

    def scan_origin(self, target):
        # Membersihkan target dari http/https/slash
        target = target.replace("https://", "").replace("http://", "").split('/')[0]
        
        print_status(f"Initiating Predator Mode on: {target}", "info")
        
        # 1. Cloudflare Check
        if self.is_using_cloudflare(target):
            print(f"{Fore.RED}[!] Target is actively using Cloudflare. Proceeding with bypass techniques...")
        else:
            print(f"{Fore.GREEN}[+] Target does not seem to use Cloudflare. Direct resolution might be real.")

        # 2. DNS Resolution
        try:
            initial_ip = socket.gethostbyname(target)
            print(f"{Fore.WHITE}[-] Current Public IP: {initial_ip}")
        except:
            print_status("Could not resolve initial DNS.", "error")

        # 3. ViewDNS History (New Mixing Feature)
        self.viewdns_history(target)

        # 4. Shodan Deep Search
        print_status("Searching Shodan Database...", "info")
        try:
            api = shodan.Shodan(self.shodan_key)
            results = api.search(f'hostname:"{target}"')
            if results['total'] > 0:
                for result in results['matches']:
                    found_ip = result['ip_str']
                    print_status(f"Potential Origin IP Found (Shodan): {found_ip}", "success")
                    save_result(target, f"Shodan Discovery: {found_ip}")
            else:
                print(f"{Fore.YELLOW}[!] No direct matches in Shodan.")
        except Exception as e:
            print_status(f"Shodan Error: {e}", "error")

        # 5. Censys SSL Analysis (Fixed v2)
        print_status("Analyzing SSL Certificates via Censys...", "info")
        try:
            h = CensysHosts(api_id=self.censys_id, api_secret=self.censys_secret)
            query = f"services.tls.certificates.leaf_data.subject.common_name: `{target}`"
            search_results = h.search(query, per_page=5)
            for page in search_results:
                for host in page:
                    found_ip = host.get('ip')
                    if found_ip:
                        print_status(f"Origin IP Detected (Censys SSL): {found_ip}", "success")
                        save_result(target, f"Censys SSL Match: {found_ip}")
        except Exception as e:
            print_status(f"Censys Error: {e}", "error")

        # 6. Shared Hosting Detection
        print_status("Checking for Shared Hosting Environment...", "info")
        try:
            res = requests.get(f"https://api.hackertarget.com/reverseiplookup/?q={target}", timeout=10).text
            if "No records" not in res and len(res.splitlines()) > 5:
                print(f"{Fore.MAGENTA}[ALERT] Target is on Shared Hosting. Result might be a shared server IP.")
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
import os
import socket
import requests
import shodan
from censys.search import CensysHosts
from colorama import Fore, Style, init

# Mengambil fungsi gahar dari folder core/utils.py
from core.utils import clear_screen, save_result, print_status

# Inisialisasi warna untuk terminal Kali Linux
init(autoreset=True)

class ReddotIP:
    def __init__(self):
        self.developer = "Deathnihilist"
        self.version = "1.0.0"
        self.shodan_key = ""
        self.censys_id = ""
        self.censys_secret = ""

    def banner(self):
        clear_screen()
        print(f"""
{Fore.RED}██████╗ ███████╗██████╗ ██████╗  ██████╗ ████████╗
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
        self.shodan_key = input(f"{Fore.CYAN}Enter Shodan API Key: ")
        self.censys_id = input(f"{Fore.CYAN}Enter Censys API ID: ")
        self.censys_secret = input(f"{Fore.CYAN}Enter Censys API Secret: ")
        print_status("API Keys Loaded Successfully!\n", "success")

    def scan_origin(self, target):
        print_status(f"Initiating Predator Mode on: {target}", "info")
        
        # 1. DNS Resolution
        try:
            initial_ip = socket.gethostbyname(target)
            print(f"{Fore.WHITE}[-] Current Public IP: {initial_ip} (Cloudflare/WAF Proxy)")
        except:
            print_status("Could not resolve initial DNS.", "error")

        # 2. Shodan Deep Search
        print_status("Searching Shodan Database...", "info")
        try:
            api = shodan.Shodan(self.shodan_key)
            results = api.search(f'hostname:{target}')
            for result in results['matches']:
                found_ip = result['ip_str']
                print_status(f"Potential Origin IP Found: {found_ip} ({result['org']})", "success")
                save_result(target, f"Shodan Discovery: {found_ip}")
        except Exception as e:
            print_status(f"Shodan Error: {e}", "error")

        # 3. Censys SSL Analysis (Bypass Logic)
        print_status("Analyzing SSL Certificates via Censys...", "info")
        try:
            c = CensysHosts(api_id=self.censys_id, api_secret=self.censys_secret)
            query = f"services.tls.certificates.leaf_data.subject.common_name: {target}"
            for page in c.search(query, pages=1):
                for host in page:
                    found_ip = host['ip']
                    print_status(f"Origin IP Detected (SSL Match): {found_ip}", "success")
                    save_result(target, f"Censys SSL Match: {found_ip}")
        except Exception as e:
            print_status(f"Censys Error: {e}", "error")

        # 4. Shared Hosting Detection
        print_status("Checking for Shared Hosting Environment...", "info")
        try:
            res = requests.get(f"https://api.hackertarget.com/reverseiplookup/?q={target}").text
            if len(res.splitlines()) > 5:
                print(f"{Fore.MAGENTA}[ALERT] Target is on Shared Hosting. Result might be a shared server IP.")
            else:
                print_status("Target seems to be on a Dedicated server.", "success")
        except:
            print_status("Reverse IP lookup failed.", "error")

if __name__ == "__main__":
    scanner = ReddotIP()
    scanner.banner()
    scanner.setup_api()
    target_domain = input(f"{Fore.WHITE}Target Domain (e.g. site.com): ")
    
    if target_domain:
        scanner.scan_origin(target_domain)
        print(f"\n{Fore.GREEN}[+] Scan Complete. Results saved in logs/ directory.")
    else:
        print_status("No target provided.", "error")
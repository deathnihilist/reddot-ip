import os
import socket
import requests
import dns.resolver
from colorama import Fore, Style, init
from bs4 import BeautifulSoup

# Fix untuk error 'collections' di Python terbaru
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
        self.version = "2.0.0 (No-API Edition)"

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
        """Mencari kebocoran IP melalui MX dan Subdomain standar"""
        print_status("Performing DNS Reconnaissance...", "info")
        
        # 1. Cek MX Records (Email Server)
        try:
            print_status("Checking MX Records (Mail Leak)...", "info")
            answers = dns.resolver.resolve(domain, 'MX')
            for rdata in answers:
                mx_host = str(rdata.exchange).rstrip('.')
                mx_ip = socket.gethostbyname(mx_host)
                print_status(f"Mail Server Found: {mx_host} -> {mx_ip}", "success")
                save_result(domain, f"MX Leak: {mx_ip}")
        except:
            print(f"{Fore.YELLOW}[!] No MX Records found.")

        # 2. Cek Subdomain Umum (Brute Force Ringan)
        subdomains = ['mail', 'dev', 'webmail', 'cpanel', 'direct', 'test', 'admin']
        print_status("Bruteforcing common subdomains...", "info")
        for sub in subdomains:
            try:
                sub_domain = f"{sub}.{domain}"
                ip = socket.gethostbyname(sub_domain)
                print_status(f"Subdomain Found: {sub_domain} -> {ip}", "success")
                save_result(domain, f"Subdomain Discovery: {sub_domain} ({ip})")
            except:
                continue

    def viewdns_scraper(self, domain):
        """Scraping IP History (Fixed Logic)"""
        print_status("Checking ViewDNS IP History...", "info")
        try:
            url = f"https://viewdns.info/iphistory/?domain={domain}"
            headers = {"User-Agent": "Mozilla/5.0"}
            r = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(r.text, 'html.parser')
            table = soup.find('table', {'border': '1'})
            if table:
                rows = table.find_all('tr')[2:]
                for row in rows:
                    cols = row.find_all('td')
                    ip = cols[0].text.strip()
                    owner = cols[2].text.strip()
                    if "cloudflare" not in owner.lower():
                        print_status(f"Historical IP Found: {ip} ({owner})", "success")
                        save_result(domain, f"ViewDNS Match: {ip}")
            else:
                print(f"{Fore.YELLOW}[!] No history found.")
        except Exception as e:
            print_status(f"ViewDNS Scraper Error: {e}", "error")

    def scan(self, target):
        target = target.replace("https://", "").replace("http://", "").split('/')[0]
        
        if self.check_cloudflare(target):
            print(f"{Fore.RED}[!] Cloudflare Detected! Starting Bypass Logic...")
        else:
            print(f"{Fore.GREEN}[+] No Cloudflare detected. Target is exposed.")

        self.dns_recon(target)
        self.viewdns_scraper(target)

if __name__ == "__main__":
    scanner = ReddotIP()
    scanner.banner()
    target = input(f"{Fore.WHITE}Target Domain (e.g. site.com): ")
    if target:
        scanner.scan(target)
        print(f"\n{Fore.GREEN}[+] Scan Complete. Results in logs/ directory.")
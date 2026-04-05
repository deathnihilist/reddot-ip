import requests
import socket
import concurrent.futures
from colorama import Fore, Style, init
import json
import re

init(autoreset=True)

class ReddotSubHunter:
    def __init__(self, domain):
        # Clean the target input just like in Module 1
        self.domain = domain.replace("https://", "").replace("http://", "").split('/')[0]
        self.found_subdomains = set()
        # Common subdomains wordlist (The "Fangs")
        self.wordlist = [
            'dev', 'staging', 'test', 'admin', 'api', 'v1', 'v2', 'corp', 'internal',
            'mail', 'webmail', 'db', 'database', 'sql', 'mysql', 'vpn', 'remote',
            'blog', 'shop', 'git', 'gitlab', 'jenkins', 'docker', 'ssh', 'cpanel', 'whm'
        ]

    def log(self, msg, status="info"):
        colors = {"info": Fore.CYAN, "found": Fore.GREEN, "warn": Fore.YELLOW, "crit": Fore.RED}
        prefix = {"info": "[*]", "found": "[+]", "warn": "[#]", "crit": "[!]"}
        print(f"{colors.get(status)}{prefix.get(status)} {msg}")

    def passive_recon(self):
        """OSINT Bypass: Probe public certificate logs (crt.sh)"""
        self.log(f"Phase 1: Deep Passive Recon (Bypassing Direct DNS)...", "info")
        try:
            url = f"https://crt.sh/?q=%25.{self.domain}&output=json"
            r = requests.get(url, timeout=15)
            if r.status_code == 200:
                data = r.json()
                for entry in data:
                    name = entry['name_value'].lower()
                    # Clean the wildcard and duplicates
                    subs = name.split('\n')
                    for s in subs:
                        if s.endswith(self.domain) and "*" not in s:
                            self.found_subdomains.add(s)
                self.log(f"Passive Recon found {len(self.found_subdomains)} potential subdomains.", "found")
        except Exception as e:
            self.log(f"Passive Recon throttled or failed: {e}", "warn")

    def brute_force_worker(self, sub):
        """Active Probing: Physical verification of subdomain existence"""
        full_url = f"{sub}.{self.domain}"
        try:
            # Resolve IP to verify the subdomain is alive
            ip = socket.gethostbyname(full_url)
            return (full_url, ip)
        except:
            return None

    def run(self):
        print(f"\n{Fore.WHITE}--- [ REDDOT SHADOW SUBDOMAIN HUNTER ] ---")
        self.log(f"Hunting for shadows in: {self.domain}", "info")

        # Step 1: Passive Recon (No touch to target)
        self.passive_recon()

        # Step 2: Active Brute-force (Deep Probing)
        self.log(f"Phase 2: Aggressive Brute-force (Wordlist Probe)...", "info")
        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            results = list(executor.map(self.brute_force_worker, self.wordlist))
            for res in results:
                if res:
                    self.found_subdomains.add(res[0])

        # --- [ PERBAIKAN DI SINI ] ---
        discovered_ips = set() # Menggunakan set agar IP yang didapat tidak duplikat

        # Final Report
        if not self.found_subdomains:
            self.log("No subdomains found. Target perimeter is extremely isolated.", "crit")
        else:
            print(f"\n{Fore.RED}SUBDOMAIN DISCOVERY REPORT FOR {self.domain}:")
            print(f"{Fore.WHITE}{'-'*50}")
            # Sort for clean output
            sorted_subs = sorted(list(self.found_subdomains))
            for sub in sorted_subs:
                try:
                    ip = socket.gethostbyname(sub)
                    print(f"{Fore.GREEN}[+] {sub.ljust(30)} {Fore.YELLOW}-> IP: {ip}")
                    discovered_ips.add(ip) # Catat IP yang aktif
                except:
                    print(f"{Fore.WHITE}[?] {sub.ljust(30)} {Fore.YELLOW}-> IP: Resolution Failed")
            print(f"{Fore.WHITE}{'-'*50}")
            self.log(f"Total Unique Subdomains Found: {len(self.found_subdomains)}", "found")
            
            # Kembalikan daftar IP unik ke Framework (reddot.py)
            return list(discovered_ips)
            
        return []

if __name__ == "__main__":
    target = input(f"{Fore.WHITE}Enter Target Domain: ")
    if target:
        hunter = ReddotSubHunter(target)
        hunter.run()
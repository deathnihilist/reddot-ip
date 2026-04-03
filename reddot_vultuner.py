import requests
import urllib3
import concurrent.futures
from colorama import Fore, init

# Nuclear Option: Disable all SSL and warnings for max speed
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
init(autoreset=True)

class ReddotVulnTunner:
    def __init__(self, target):
        self.target = target.replace("https://", "").replace("http://", "").split('/')[0]
        self.url = f"http://{self.target}"
        
        # Strategies for Bypassing 403 Forbidden / WAF Blocks
        self.bypass_headers = [
            {'X-Forwarded-For': '127.0.0.1'},
            {'X-Originating-IP': '127.0.0.1'},
            {'X-Remote-IP': '127.0.0.1'},
            {'X-Client-IP': '127.0.0.1'},
            {'User-Agent': 'Googlebot/2.1 (+http://www.google.com/bot.html)'}
        ]

        # High-Value "Lethal" Targets (Data Leaks & Entry Points)
        self.payloads = {
            "Critical Environment": ["/.env", "/.env.old", "/.env.php", "/.env.bak", "/core/.env"],
            "Git/VCS Exposure": ["/.git/config", "/.git/index", "/.gitignore", "/.svn/entries"],
            "Config & Database": ["/web-config.xml", "/config.php.bak", "/db.php.swp", "/database.sql.gz"],
            "System Info": ["/phpinfo.php", "/info.php", "/version.txt", "/server-status"],
            "Admin Backdoors": ["/shell.php", "/pma/", "/admin/config.php", "/backup.tar.gz"]
        }

    def log(self, msg, status="info"):
        colors = {"info": Fore.CYAN, "found": Fore.RED, "warn": Fore.YELLOW}
        prefix = {"info": "[*]", "found": "[!]", "warn": "[#]"}
        print(f"{colors.get(status)}{prefix.get(status)} {msg}")

    def probe(self, name, path):
        """The 'Wraith' Probe: Tries multiple headers to bypass 403/401 blocks"""
        full_url = f"{self.url}{path}"
        
        for header in self.bypass_headers:
            try:
                # Timeout tipis agar lincah (Fast Strike)
                r = requests.get(full_url, headers=header, timeout=5, verify=False, allow_redirects=False)
                
                # Logic Bypass: Jika 200 OK atau 301/302 yang mencurigakan
                if r.status_code == 200 and len(r.text) > 10:
                    # Double Check: Pastikan bukan 'Fake 200' (Page Not Found custom)
                    if "404" not in r.text.lower() and "not found" not in r.text.lower():
                        self.log(f"VULNERABILITY FOUND: {name} exposed at {path}", "found")
                        print(f"    {Fore.WHITE}└── Bypass Technique: {header}")
                        # Simpan hasil ke file log otomatis
                        with open("leaks_found.txt", "a") as f:
                            f.write(f"[{self.target}] {name}: {full_url}\n")
                        return True
            except:
                continue
        return False

    def cve_analyzer(self, tech_string):
        """Deep CVE Matcher for Unpatched Systems"""
        self.log(f"Deep Analyzing CVEs for: {tech_string}", "info")
        
        # CVE Database Simulation (Targeting Government-level common tech)
        cve_database = {
            "Apache/2.4.49": ["CVE-2021-41773 (Path Traversal/RCE) - CRITICAL"],
            "Apache/2.4.50": ["CVE-2021-42013 (RCE Bypass) - CRITICAL"],
            "PHP/5.": ["Multiple RCE & Heap Overflow (Legacy System) - HIGH"],
            "Nginx/1.18": ["CVE-2021-23017 (DNS Resolver DoS/RCE) - HIGH"],
            "OpenSSL/1.0.1": ["Heartbleed Vulnerability - CRITICAL"]
        }

        found_cve = False
        for tech, cves in cve_database.items():
            if tech in tech_string:
                for cve in cves:
                    print(f"{Fore.RED}[DANGER] {cve}")
                found_cve = True
        
        if not found_cve:
            self.log("No known major CVEs for this specific build signature.", "warn")

    def run(self, tech_stack=None):
        print(f"\n{Fore.WHITE}--- [ REDDOT AUTOMATED VULN ENGINE - WRAITH MODE ] ---")
        self.log(f"Starting Recursive Scan on {self.target}...", "info")

        # Flattening the list for threading
        all_tasks = []
        for category, paths in self.payloads.items():
            for path in paths:
                all_tasks.append((category, path))

        # 100-Legs Logic: High speed concurrent probing
        with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
            executor.map(lambda p: self.probe(*p), all_tasks)

        if tech_stack:
            self.cve_analyzer(tech_stack)

if __name__ == "__main__":
    t = input("Target: ")
    rv = ReddotVulnTunner(t)
    rv.run("Apache/2.4.49")

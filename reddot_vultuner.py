import requests
import urllib3
import concurrent.futures
from colorama import Fore, init

# Disable SSL warnings for max speed & bypass
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
init(autoreset=True)

class ReddotVulnTunner:
    def __init__(self, target):
        # Bersihkan target dari protokol
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

        # High-Value "Lethal" Targets
        self.payloads = {
            "Critical Environment": ["/.env", "/.env.old", "/.env.bak"],
            "Git/VCS Exposure": ["/.git/config", "/.git/index", "/.gitignore"],
            "Config & Database": ["/config.php.bak", "/db.php.swp", "/database.sql.gz"],
            "System Info": ["/phpinfo.php", "/info.php", "/version.txt"],
            "Admin Backdoors": ["/shell.php", "/pma/", "/backup.tar.gz"]
        }

    def log(self, msg, status="info"):
        colors = {"info": Fore.CYAN, "found": Fore.RED, "warn": Fore.YELLOW}
        prefix = {"info": "[*]", "found": "[!]", "warn": "[#]"}
        print(f"{colors.get(status, Fore.WHITE)}{prefix.get(status, '[*]')} {msg}")

    def probe(self, category, path):
        """The 'Wraith' Probe: Tries multiple headers to bypass blocks"""
        full_url = f"{self.url}{path}"
        
        for header in self.bypass_headers:
            try:
                # Timeout 5 detik agar tidak stuck
                r = requests.get(full_url, headers=header, timeout=5, verify=False, allow_redirects=False)
                
                if r.status_code == 200 and len(r.text) > 10:
                    # Anti-Fake 404 Logic
                    if "404" not in r.text.lower() and "not found" not in r.text.lower():
                        self.log(f"FOUND ({category}): {path}", "found")
                        with open("leaks_found.txt", "a") as f:
                            f.write(f"[{self.target}] {category}: {full_url}\n")
                        return True
            except:
                continue
        return False

    def run(self, tech_stack=None):
        print(f"\n{Fore.WHITE}--- [ REDDOT AUTOMATED VULN ENGINE - WRAITH MODE ] ---")
        self.log(f"Initiating Recursive Strike on {self.target}...", "info")

        # Prepare task list
        tasks = []
        for category, paths in self.payloads.items():
            for path in paths:
                tasks.append((category, path))

        # Start Multi-Threading (100-Legs)
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            # Menggunakan list comprehension untuk memicu eksekusi
            futures = [executor.submit(self.probe, cat, path) for cat, path in tasks]
            concurrent.futures.wait(futures)

        self.log("Scan Sequence Completed.", "info")

if __name__ == "__main__":
    t = input("Target: ")
    rv = ReddotVulnTunner(t)
    rv.run()
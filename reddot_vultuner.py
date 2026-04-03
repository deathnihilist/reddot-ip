import requests
import urllib3
import concurrent.futures
from colorama import Fore, init

# Suppress insecure request warnings for cleaner output
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
init(autoreset=True)

class ReddotVulnTunner:
    def __init__(self, target):
        # Sanitize target input
        self.target = target.replace("https://", "").replace("http://", "").split('/')[0]
        self.base_url = f"https://{self.target}"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        # High-Value Path Dictionary
        self.payloads = {
            "Environment": ["/.env", "/.env.local", "/.env.php", "/.env.bak"],
            "VCS": ["/.git/config", "/.git/index", "/.gitignore", "/.svn/entries"],
            "Config": ["/web.config", "/phpinfo.php", "/config.php.bak", "/.htaccess"],
            "Backup": ["/backup.zip", "/database.sql", "/site.tar.gz", "/archive.rar"]
        }

    def log(self, msg, status="info"):
        color = {"info": Fore.CYAN, "found": Fore.RED, "warn": Fore.YELLOW}.get(status, Fore.WHITE)
        symbol = {"info": "[*]", "found": "[!]", "warn": "[#]"}.get(status, "[*]")
        print(f"{color}{symbol} {msg}")

    def probe(self, category, path):
        """Execute a single HTTP request and analyze the response header/body."""
        target_url = f"{self.base_url}{path}"
        try:
            # Using allow_redirects=False to catch sensitive files before they get masked by 301/302
            response = requests.get(
                target_url, 
                headers=self.headers, 
                timeout=6, 
                verify=False, 
                allow_redirects=False
            )
            
            # Status Tracking (Verbose Output)
            if response.status_code != 404:
                status_color = Fore.GREEN if response.status_code == 200 else Fore.YELLOW
                print(f"{Fore.BLUE}[DEBUG] {status_color}{response.status_code}{Fore.WHITE} -> {path}")

            # Vulnerability Detection Logic
            if response.status_code == 200:
                # Filter out generic 'Not Found' pages returning 200 OK
                if "404" not in response.text.lower() and len(response.text) > 15:
                    self.log(f"CRITICAL EXPOSURE: {target_url} ({category})", "found")
                    return True
            
            elif response.status_code == 403:
                self.log(f"Access Forbidden (Path Exists): {path}", "warn")
                
        except Exception:
            pass
        return False

    def run(self):
        print(f"\n{Fore.RED}--- [ WRAITH VULN ENGINE : ACTIVE RECON ] ---")
        self.log(f"Engaging Target: {self.base_url}", "info")
        
        # Build task queue
        scan_queue = []
        for cat, paths in self.payloads.items():
            for path in paths:
                scan_queue.append((cat, path))

        # Threading Execution (Max 30 workers to avoid WAF rate-limiting)
        with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
            # Force execution using list comprehension
            futures = [executor.submit(self.probe, cat, path) for cat, path in scan_queue]
            concurrent.futures.wait(futures)

        self.log("Scan operation completed successfully.", "info")

if __name__ == "__main__":
    host = input("Target Domain: ")
    engine = ReddotVulnTunner(host)
    engine.run()
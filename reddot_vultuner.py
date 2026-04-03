import requests
import urllib3
import concurrent.futures
from colorama import Fore, init

# Suppress SSL Warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
init(autoreset=True)

class ReddotVulnTunner:
    def __init__(self, target):
        self.target = target.replace("https://", "").replace("http://", "").split('/')[0]
        self.base_url = f"https://{self.target}"
        self.headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) Reddot/3.0'}
        
        self.stats = {"200": 0, "403": 0, "404": 0, "Errors": 0}
        self.payloads = {
            "Config": ["/.env", "/.git/config", "/web.config", "/.htaccess"],
            "Admin": ["/phpinfo.php", "/pma/", "/admin/config.php", "/shell.php"],
            "Backup": ["/backup.zip", "/database.sql", "/site.tar.gz", "/old.bak"]
        }

    def log_status(self, code, path):
        """Color-coded logging for every single request."""
        color = Fore.WHITE
        if code == 200: color = Fore.GREEN
        elif code == 403: color = Fore.YELLOW
        elif code == 404: color = Fore.LIGHTBLACK_EX # Dimmed for 404s
        else: color = Fore.RED

        print(f"{Fore.BLUE}[SCAN]{Fore.WHITE} Status: {color}{code}{Fore.WHITE} -> {path}")

    def probe(self, category, path):
        target_url = f"{self.base_url}{path}"
        try:
            # We use allow_redirects=False to see exactly what the server says
            r = requests.get(target_url, headers=self.headers, timeout=5, verify=False, allow_redirects=False)
            
            # Update Internal Stats
            status_str = str(r.status_code)
            if status_str in self.stats:
                self.stats[status_str] += 1
            
            # Log the detail to terminal
            self.log_status(r.status_code, path)

            if r.status_code == 200 and len(r.text) > 15:
                if "404" not in r.text.lower():
                    print(f"\n{Fore.RED}[!!!] VULNERABILITY FOUND: {target_url}\n")
                    return True
        except Exception as e:
            self.stats["Errors"] += 1
            print(f"{Fore.RED}[ERROR]{Fore.WHITE} Failed to connect to {path}")
        return False

    def run(self):
        print(f"\n{Fore.RED}--- [ WRAITH VULN ENGINE : FULL VERBOSE MODE ] ---")
        print(f"{Fore.CYAN}[*] Targeting: {self.base_url}\n")
        
        tasks = []
        for cat, paths in self.payloads.items():
            for path in paths:
                tasks.append((cat, path))

        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            # list() forces the generator to execute immediately
            list(executor.map(lambda p: self.probe(*p), tasks))

        # Final Report Summary
        print(f"\n{Fore.CYAN}--- [ SCAN SUMMARY ] ---")
        print(f"{Fore.GREEN}Success (200)   : {self.stats['200']}")
        print(f"{Fore.YELLOW}Forbidden (403) : {self.stats['403']}")
        print(f"{Fore.WHITE}Not Found (404) : {self.stats['404']}")
        print(f"{Fore.RED}Failures/Errors : {self.stats['Errors']}")
        print(f"{Fore.CYAN}--- [ SCAN COMPLETE ] ---\n")

if __name__ == "__main__":
    t = input("Target: ")
    ReddotVulnTunner(t).run()
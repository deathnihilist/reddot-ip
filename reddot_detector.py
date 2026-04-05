import requests
import urllib3
import concurrent.futures
from colorama import Fore, init

# Suppress SSL warnings if the target certificate is invalid/expired
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
init(autoreset=True)

class ReddotDetector:
    def __init__(self, target):
        self.target = target.replace("https://", "").replace("http://", "").split('/')[0]
        # Prioritize HTTPS, as HTTP often causes connection resets or blocks
        self.base_url = f"https://{self.target}"
        self.headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) Reddot-Centipede/3.0'}
        self.results = {
            "web_server": "Unknown",
            "backend": "Unknown",
            "cms": "Unknown",
            "leaks": []
        }

    def print_status(self, msg, status="info"):
        colors = {"info": Fore.CYAN, "success": Fore.GREEN, "warn": Fore.YELLOW, "crit": Fore.RED}
        symbol = {"info": "[*]", "success": "[+]", "warn": "[#]", "crit": "[!]"}.get(status, "[*]")
        print(f"{colors.get(status, Fore.WHITE)}{symbol} {msg}")

    def check_path(self, path):
        """Aggressive probe to check sensitive files/folders."""
        url = f"{self.base_url}/{path}"
        try:
            r = requests.get(url, headers=self.headers, timeout=6, verify=False, allow_redirects=False)
            # 200 OK without a typical 404 page body means we found something
            if r.status_code == 200 and "404" not in r.text.lower() and len(r.text) > 15:
                return (path, True, len(r.content))
            return (path, False, 0)
        except Exception:
            return (path, False, 0)

    def detect_headers(self):
        self.print_status("Ripping HTTP Headers for Identity...", "info")
        try:
            # First attempt with HTTPS
            r = requests.get(self.base_url, headers=self.headers, timeout=8, verify=False)
        except Exception:
            # Fallback to HTTP if HTTPS fails
            self.print_status("HTTPS connection failed. Falling back to HTTP...", "warn")
            self.base_url = f"http://{self.target}"
            try:
                r = requests.get(self.base_url, headers=self.headers, timeout=8, verify=False)
            except Exception as e:
                self.print_status(f"Header Rip Failed completely: {e}", "crit")
                return

        h = r.headers
        
        # Server & OS Detection
        self.results["web_server"] = h.get('Server', 'Hidden')
        
        # Backend Language Detection
        self.results["backend"] = h.get('X-Powered-By', 'Hidden')
        if "PHP" in self.results["backend"] or "php" in r.text.lower():
            if self.results["backend"] == "Hidden": 
                self.results["backend"] = "PHP (Detected via patterns)"

        # Basic CMS Detection
        if "wp-content" in r.text.lower(): self.results["cms"] = "WordPress"
        elif "joomla" in r.text.lower(): self.results["cms"] = "Joomla"
        elif "drupal" in r.text.lower(): self.results["cms"] = "Drupal"
        elif "laravel" in r.text.lower() or h.get('Set-Cookie', '').find('laravel') != -1: 
            self.results["cms"] = "Laravel Framework"

    def run_centipede(self):
        """100-Leg Mode: Simultaneous identity and leak probing."""
        paths_to_check = [
            ".env", ".git/config", "phpinfo.php", "info.php", "test.php",
            "wp-config.php.bak", ".htaccess", "config.php", "v1/.env",
            "license.txt", "readme.html", "server-status", ".ssh/id_rsa"
        ]
        
        self.print_status(f"Deploying {len(paths_to_check)} legs to probe files on {self.base_url}...", "info")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            future_to_path = {executor.submit(self.check_path, p): p for p in paths_to_check}
            for future in concurrent.futures.as_completed(future_to_path):
                path, found, size = future.result()
                if found:
                    self.print_status(f"CRITICAL LEAK FOUND: /{path} (Size: {size} bytes)", "crit")
                    self.results["leaks"].append(path)

    def display_report(self):
        print(f"\n{Fore.RED}{'='*50}")
        print(f"{Fore.WHITE}       DIGITAL DNA REPORT: {self.target}")
        print(f"{Fore.RED}{'='*50}")
        print(f"{Fore.YELLOW}OS/Web Server : {Fore.WHITE}{self.results['web_server']}")
        print(f"{Fore.YELLOW}Backend Tech  : {Fore.WHITE}{self.results['backend']}")
        print(f"{Fore.YELLOW}CMS Identity  : {Fore.WHITE}{self.results['cms']}")
        
        if self.results["leaks"]:
            print(f"{Fore.RED}Vulnerable Points: {Fore.WHITE}{', '.join(self.results['leaks'])}")
        else:
            print(f"{Fore.GREEN}Vulnerable Points: {Fore.WHITE}No direct file leaks found.")
        print(f"{Fore.RED}{'='*50}\n")

    def run(self):
        """Main execution flow managed by the Reddot core engine."""
        print(f"\n{Fore.RED}--- [ DIGITAL DNA DETECTOR : CENTIPEDE MODE ] ---")
        self.detect_headers()
        self.run_centipede()
        self.display_report()

# Standalone testing block
if __name__ == "__main__":
    t = input(f"{Fore.WHITE}Enter Target Domain for Tech Scan: ")
    if t:
        detector = ReddotDetector(t)
        detector.run()
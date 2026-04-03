import requests
import urllib3
import concurrent.futures
from colorama import Fore, Style, init

# Abaikan peringatan SSL jika sertifikat target busuk/expired
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

init(autoreset=True)

class ReddotDetector:
    def __init__(self, target):
        self.target = target.replace("https://", "").replace("http://", "").split('/')[0]
        self.base_url = f"http://{self.target}"
        self.headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) Reddot-Centipede/2.0'}
        self.results = {
            "web_server": "Unknown",
            "backend": "Unknown",
            "cms": "Unknown",
            "leaks": []
        }

    def print_status(self, msg, status="info"):
        colors = {"info": Fore.CYAN, "success": Fore.GREEN, "warn": Fore.YELLOW, "crit": Fore.RED}
        print(f"{colors.get(status, Fore.WHITE)}[*] {msg}")

    def check_path(self, path):
        """Kaki agresif untuk mengecek folder/file sensitif"""
        url = f"{self.base_url}/{path}"
        try:
            r = requests.get(url, headers=self.headers, timeout=5, verify=False, allow_redirects=False)
            if r.status_code == 200:
                return (path, True, len(r.content))
            return (path, False, 0)
        except:
            return (path, False, 0)

    def detect_headers(self):
        self.print_status("Ripping HTTP Headers for Identity...", "info")
        try:
            r = requests.get(self.base_url, headers=self.headers, timeout=5, verify=False)
            h = r.headers
            
            # Deteksi Server & OS
            self.results["web_server"] = h.get('Server', 'Hidden')
            
            # Deteksi Backend Language
            self.results["backend"] = h.get('X-Powered-By', 'Hidden')
            if "PHP" in self.results["backend"] or "php" in r.text.lower():
                if "backend" == "Hidden": self.results["backend"] = "PHP (Detected via patterns)"

            # Deteksi CMS Awal
            if "wp-content" in r.text: self.results["cms"] = "WordPress"
            elif "joomla" in r.text.lower(): self.results["cms"] = "Joomla"
            elif "drupal" in r.text.lower(): self.results["cms"] = "Drupal"
            
        except Exception as e:
            self.print_status(f"Header Rip Failed: {e}", "crit")

    def run_centipede(self):
        """Mode 100 Kaki: Brute force identitas secara simultan"""
        paths_to_check = [
            ".env", ".git/config", "phpinfo.php", "info.php", "test.php",
            "wp-config.php.bak", ".htaccess", "config.php", "v1/.env",
            "license.txt", "readme.html", "server-status", ".ssh/id_rsa"
        ]
        
        self.print_status(f"Deploying {len(paths_to_check)} legs to probe files...", "info")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            future_to_path = {executor.submit(self.check_path, p): p for p in paths_to_check}
            for future in concurrent.futures.as_completed(future_to_path):
                path, found, size = future.result()
                if found:
                    self.print_status(f"CRITICAL LEAK FOUND: /{path} (Size: {size})", "crit")
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

if __name__ == "__main__":
    target = input(f"{Fore.WHITE}Enter Target Domain for Tech Scan: ")
    if target:
        detector = ReddotDetector(target)
        detector.detect_headers()
        detector.run_centipede()
        detector.display_report()

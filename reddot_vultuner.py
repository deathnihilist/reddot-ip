import requests
import urllib3
import concurrent.futures
from colorama import Fore, init
import os  # Ditambahkan untuk membaca file eksternal

# Suppress SSL Warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
init(autoreset=True)

class ReddotVulnTunner:
    def __init__(self, target):
        self.target = target.replace("https://", "").replace("http://", "").split('/')[0]
        self.base_url = f"https://{self.target}"
        self.headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) Reddot/3.0'}
        
        self.stats = {"200": 0, "403": 0, "404": 0, "Errors": 0}
        
        # [KODE ASLIMU DIPERTAHANKAN] Sebagai cadangan jika master_fuzz.txt hilang
        self.payloads = {
            "Config": ["/.env", "/.git/config", "/web.config", "/.htaccess"],
            "Admin": ["/phpinfo.php", "/pma/", "/admin/config.php", "/shell.php"],
            "Backup": ["/backup.zip", "/database.sql", "/site.tar.gz", "/old.bak"]
        }
        self.master_file = "master_fuzz.txt"

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
        
        # [INTEGRASI STRATEGI BARU]
        # Jika file 6,4 Juta barismu ada, jalankan mode kencang
        if os.path.exists(self.master_file):
            print(f"{Fore.YELLOW}[*] Master file detected! Loading 6.4 Million payloads...")
            
            # Wrapper agar tidak merusak fungsi 'probe' bawaanmu yang butuh argumen 'category'
            def probe_wrapper(path):
                p = path if path.startswith('/') else '/' + path
                return self.probe("Master", p)
            
            # Saya naikkan ke 100 workers agar lari kencang
            with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
                with open(self.master_file, 'r', encoding='utf-8', errors='ignore') as f:
                    paths = (line.strip() for line in f if line.strip())
                    list(executor.map(probe_wrapper, paths))
                    
        else:
            # Jika file master_fuzz.txt tidak ada, pakai kodemu yang lama secara otomatis
            print(f"{Fore.CYAN}[*] Master file not found. Using your original hardcoded payloads...")
            tasks = []
            for cat, paths in self.payloads.items():
                for path in paths:
                    tasks.append((cat, path))

            with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
                list(executor.map(lambda p: self.probe(*p), tasks))

        # Final Report Summary (Semua datamu tetap terekam sempurna)
        print(f"\n{Fore.CYAN}--- [ SCAN SUMMARY ] ---")
        print(f"{Fore.GREEN}Success (200)   : {self.stats['200']}")
        print(f"{Fore.YELLOW}Forbidden (403) : {self.stats['403']}")
        print(f"{Fore.WHITE}Not Found (404) : {self.stats['404']}")
        print(f"{Fore.RED}Failures/Errors : {self.stats['Errors']}")
        print(f"{Fore.CYAN}--- [ SCAN COMPLETE ] ---\n")

if __name__ == "__main__":
    t = input("Target: ")
    ReddotVulnTunner(t).run()
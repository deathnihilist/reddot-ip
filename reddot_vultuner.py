import requests
import urllib3
import concurrent.futures
from colorama import Fore, init

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
init(autoreset=True)

class ReddotVulnTunner:
    def __init__(self, target):
        self.target = target.replace("https://", "").replace("http://", "").split('/')[0]
        # Kita coba HTTPS dulu karena lebih standar sekarang
        self.base_url = f"https://{self.target}"
        
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        
        # Payload lebih luas & spesifik
        self.payloads = {
            "Config": ["/.env", "/.env.bak", "/config.php.bak", "/web.config", "/.git/config"],
            "Backdoors": ["/shell.php", "/wp-content/plugins/shell.php", "/pma/", "/admin/index.php"],
            "Logs/Info": ["/phpinfo.php", "/info.php", "/error_log", "/access_log", "/debug.log"],
            "Backups": ["/backup.zip", "/data.sql", "/site.tar.gz", "/database.bak"]
        }

    def log(self, msg, status="info"):
        color = {"info": Fore.CYAN, "found": Fore.RED, "warn": Fore.YELLOW}.get(status, Fore.WHITE)
        print(f"{color}[*] {msg}")

    def probe(self, category, path):
        full_url = f"{self.base_url}{path}"
        try:
            # Gunakan session agar lebih cepat & bypass beberapa filter sederhana
            r = requests.get(full_url, headers=self.headers, timeout=7, verify=False, allow_redirects=False)
            
            # Jika 200 OK atau 403 (Forbidden seringkali berarti filenya ADA tapi dilarang)
            if r.status_code == 200:
                if "404" not in r.text.lower() and len(r.text) > 20:
                    print(f"{Fore.RED}[!] VULN FOUND [{category}]: {full_url} (Size: {len(r.text)})")
                    return True
            elif r.status_code == 403:
                # 403 seringkali pertanda bagus (filenya ada tapi di-protect)
                print(f"{Fore.YELLOW}[#] POTENTIAL [{category}]: {full_url} (Status: 403 Forbidden)")
                
        except:
            pass
        return False

    def run(self):
        print(f"\n{Fore.RED}--- [ WRAITH VULN ENGINE : AGGRESSIVE MODE ] ---")
        self.log(f"Targeting: {self.base_url}", "info")
        
        tasks = []
        for cat, paths in self.payloads.items():
            for path in paths:
                tasks.append((cat, path))

        # Gunakan 50 threads agar bener-bener "Nuclear"
        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            executor.map(lambda p: self.probe(*p), tasks)

        print(f"\n{Fore.CYAN}[*] Scan Finished. Jika kosong, target mungkin menggunakan WAF kuat.")

if __name__ == "__main__":
    t = input("Target: ")
    ReddotVulnTunner(t).run()
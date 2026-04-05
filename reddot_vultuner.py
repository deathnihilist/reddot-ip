import requests
import urllib3
import concurrent.futures
from colorama import Fore, init
import os
import threading
import sys
from itertools import islice

# Suppress SSL Warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
init(autoreset=True)

class ReddotVulnTunner:
    def __init__(self, target):
        self.target = target.replace("https://", "").replace("http://", "").split('/')[0]
        self.base_url = f"https://{self.target}"
        self.headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) Reddot/3.0'}
        
        # Lock untuk mencegah logs bertabrakan
        self.log_lock = threading.Lock()
        
        # Menambahkan status 401 ke dalam statistik
        self.stats = {"200": 0, "401": 0, "403": 0, "404": 0, "Errors": 0}
        
        self.payloads = {
            "Config": ["/.env", "/.git/config", "/web.config", "/.htaccess"],
            "Admin": ["/phpinfo.php", "/pma/", "/admin/config.php", "/shell.php"],
            "Backup": ["/backup.zip", "/database.sql", "/site.tar.gz", "/old.bak"]
        }
        self.master_file = "master_fuzz.txt"

    def probe(self, category, path):
        target_url = f"{self.base_url}{path}"
        try:
            # allow_redirects=False untuk memonitor respons murni server
            r = requests.get(target_url, headers=self.headers, timeout=5, verify=False, allow_redirects=False)
            
            status_str = str(r.status_code)
            
            # Kunci terminal agar log rapi dan tidak tumpang tindih
            with self.log_lock:
                if status_str in self.stats:
                    self.stats[status_str] += 1
                else:
                    self.stats["Errors"] += 1

                # 1. FORMAT UNTUK STATUS 200 (AI-READY)
                if r.status_code == 200:
                    if len(r.text) > 15 and "404" not in r.text.lower():
                        print(f"\n{Fore.GREEN}[+] [STATUS=200] [CLASS=VULN_EXPOSED] [PRIORITY=CRITICAL]{Fore.WHITE}")
                        print(f"    IDENTIFIER : {path.strip('/').replace('/', '_').upper() if path.strip('/') else 'ROOT'}")
                        print(f"    TARGET_URL : {target_url}")
                        print(f"    RAW_DATA   : \"{r.text[:60].strip().replace('\n', ' ')}...\"")
                        print(f"    ANALYSIS   : Accessible sensitive or active endpoint detected.")
                        print(f"    AI_ACTION  : Inspect content for hardcoded credentials or data leaks.")
                        print(f"{Fore.GREEN}----------------------------------------------------------------------------------{Fore.WHITE}")
                        return True
                        
                # 2. FORMAT UNTUK STATUS 401 & 403 (AI-READY)
                elif r.status_code in [401, 403]:
                    cls_tag = "AUTH_REQUIRED" if r.status_code == 401 else "INTERESTING_PATH"
                    print(f"{Fore.YELLOW}[!] [STATUS={r.status_code}] [CLASS={cls_tag}] [PRIORITY=MEDIUM]{Fore.WHITE}")
                    print(f"    IDENTIFIER : {path.strip('/').replace('/', '_').upper() if path.strip('/') else 'ROOT'}")
                    print(f"    TARGET_URL : {target_url}")
                    print(f"    ANALYSIS   : Endpoint exists but access is restricted or requires auth.")
                    print(f"    AI_ACTION  : Attempt directory traversal, extension fuzzing, or auth bypass.")
                    print(f"{Fore.YELLOW}----------------------------------------------------------------------------------{Fore.WHITE}")

        except requests.exceptions.ConnectionError:
            with self.log_lock:
                self.stats["Errors"] += 1
                print(f"{Fore.RED}[✖] [STATUS=ERR] [CLASS=CONN_RESET] [PRIORITY=HIGH]{Fore.WHITE}")
                print(f"    IDENTIFIER : NETWORK_FAILURE")
                print(f"    TARGET_URL : {target_url}")
                print(f"    SYMPTOMS   : Server closed connection or WAF blocked request.")
                print(f"    AI_ACTION  : Rotate proxy or slow down requests.")
                print(f"{Fore.RED}----------------------------------------------------------------------------------{Fore.WHITE}")
        except Exception as e:
            with self.log_lock:
                self.stats["Errors"] += 1
                pass
        return False

    def run(self):
        print(f"\n{Fore.RED}--- [ WRAITH VULN ENGINE : FULL VERBOSE MODE ] ---")
        print(f"{Fore.CYAN}[*] Targeting: {self.base_url}\n")
        
        try:
            if os.path.exists(self.master_file):
                print(f"{Fore.YELLOW}[*] Master file detected! Processing in chunks to save memory...")
                
                def probe_wrapper(path):
                    p = path if path.startswith('/') else '/' + path
                    return self.probe("Master", p)
                
                chunk_size = 3000
                total_scanned = 0

                with open(self.master_file, 'r', encoding='utf-8', errors='ignore') as f:
                    while True:
                        # Ambil 3000 baris selanjutnya
                        chunk = list(islice(f, chunk_size))
                        if not chunk:
                            break # Berhenti jika file sudah habis dibaca
                            
                        paths = [line.strip() for line in chunk if line.strip()]
                        
                        # Jalankan thread hanya untuk 3000 baris ini
                        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
                            list(executor.map(probe_wrapper, paths))
                            
                        total_scanned += len(paths)
                        
                        # Pertanyaan setiap 3000 payloads selesai
                        if len(chunk) == chunk_size:
                            print(f"\n{Fore.CYAN}[?] System Paused. {total_scanned} payloads have been scanned.")
                            choice = input(f"{Fore.YELLOW}Do you want to continue this scan? [Y/N]: {Fore.WHITE}").strip().upper()
                            if choice == 'N':
                                print(f"{Fore.RED}[!] Scan aborted by user.{Fore.WHITE}")
                                break
                            else:
                                print(f"{Fore.GREEN}[+] Resuming scan...\n{Fore.WHITE}")
                        
            else:
                print(f"{Fore.CYAN}[*] Master file not found. Using your original hardcoded payloads...")
                tasks = []
                for cat, paths in self.payloads.items():
                    for path in paths:
                        tasks.append((cat, path))

                with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
                    list(executor.map(lambda p: self.probe(*p), tasks))

        except KeyboardInterrupt:
            # Handle Ctrl+C / Ctrl+X dengan rapi
            print(f"\n{Fore.RED}[!] Scan forcefully interrupted by user. Cleaning up processes...{Fore.WHITE}")
        
        finally:
            # Final Report Summary tetap muncul meskipun di-cancel
            print(f"\n{Fore.CYAN}--- [ SCAN SUMMARY ] ---")
            print(f"{Fore.GREEN}Success (200)   : {self.stats['200']}")
            print(f"{Fore.YELLOW}Unauthorized (401) : {self.stats['401']}")
            print(f"{Fore.YELLOW}Forbidden (403) : {self.stats['403']}")
            print(f"{Fore.WHITE}Not Found (404) : {self.stats['404']}")
            print(f"{Fore.RED}Failures/Errors : {self.stats['Errors']}")
            print(f"{Fore.CYAN}--- [ SCAN COMPLETE ] ---\n")

if __name__ == "__main__":
    t = input("Target: ")
    ReddotVulnTunner(t).run()
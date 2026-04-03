import requests
import urllib3
from colorama import Fore, Style, init

# Sembunyikan warning SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
init(autoreset=True)

class ReddotWAF:
    def __init__(self, target):
        self.target = target.replace("https://", "").replace("http://", "").split('/')[0]
        self.url = f"http://{self.target}"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        # Payload agresif untuk memicu reaksi WAF (XSS, SQLi, LFI)
        self.malicious_payloads = {
            "XSS": "<script>alert('Reddot')</script>",
            "SQLi": "UNION SELECT ALL FROM information_schema.tables--",
            "LFI": "../../../../etc/passwd"
        }

    def log(self, msg, status="info"):
        colors = {"info": Fore.CYAN, "found": Fore.RED, "safe": Fore.GREEN, "warn": Fore.YELLOW}
        prefix = {"info": "[*]", "found": "[!]", "safe": "[+]", "warn": "[#]"}
        print(f"{colors.get(status)}{prefix.get(status)} {msg}")

    def detect_by_headers(self):
        """Kaki 1: Deteksi identitas melalui HTTP Fingerprint"""
        self.log("Ripping headers for WAF signatures...", "info")
        try:
            r = requests.get(self.url, headers=self.headers, timeout=10, verify=False)
            h = r.headers
            
            waf_signatures = {
                "Cloudflare": ["cloudflare", "cf-ray", "__cfduid"],
                "Sucuri": ["x-sucuri-id", "x-sucuri-cache", "sucuri/cloudproxy"],
                "ModSecurity": ["mod_security", "NOVEL-ID"],
                "Akamai": ["akamai-ghost", "x-akamai-transformed"],
                "Imperva": ["x-iinfo", "incap_ses", "visid_incap"],
                "F5 BIG-IP": ["f5_cspm", "bigipserver", "x-wa-info"]
            }

            for waf, sigs in waf_signatures.items():
                for sig in sigs:
                    if sig in str(h).lower() or sig in str(r.cookies).lower():
                        return waf
            return None
        except: return None

    def attack_test(self):
        """Kaki 2: Agresif - Mencoba memicu blokade untuk konfirmasi WAF"""
        self.log("Launching mini-payloads to test WAF reactivity...", "info")
        detected_waf = []
        
        for name, payload in self.malicious_payloads.items():
            try:
                # Kirim payload lewat parameter URL
                test_url = f"{self.url}/?search={payload}"
                r = requests.get(test_url, headers=self.headers, timeout=10, verify=False)
                
                # Jika di-block (403, 406, 501) atau server merespon berbeda, berarti ada WAF aktif
                if r.status_code in [403, 406, 501, 999]:
                    self.log(f"Blocked by WAF on {name} test (Status: {r.status_code})", "found")
                    return True
            except: pass
        return False

    def check(self):
        print(f"\n{Fore.WHITE}--- [ REDDOT WAF FINGERPRINTING ] ---")
        
        waf_name = self.detect_by_headers()
        is_reactive = self.attack_test()

        if waf_name or is_reactive:
            print(f"\n{Fore.RED}[WARNING] WAF DETECTED: {waf_name if waf_name else 'Generic/Unknown WAF'}")
            print(f"{Fore.YELLOW}[!] STATUS: Hati-hati, jangan brute force terlalu kencang! IP kamu bisa di-ban.")
            
            # Tips Bypass (Analisis singkat)
            print(f"\n{Fore.CYAN}[BYPASS HINT]:")
            if waf_name == "Cloudflare":
                print(f"  - Cari IP Origin asli (Gunakan reddot_ip.py)")
                print(f"  - Coba ganti Host Header atau cari subdomain yang tidak diproteksi.")
            else:
                print(f"  - Coba teknik HTTP Parameter Pollution (HPP)")
                print(f"  - Gunakan rotasi Proxy/VPN untuk menghindari rate-limit.")
        else:
            self.log("No WAF detected or WAF is in monitoring mode (Transparent).", "safe")
            print(f"{Fore.GREEN}[+] STATUS: Jalur aman. Kamu bisa bergerak lebih agresif.")

if __name__ == "__main__":
    target = input(f"{Fore.WHITE}Enter Target Domain to check WAF: ")
    if target:
        wf = ReddotWAF(target)
        wf.check()

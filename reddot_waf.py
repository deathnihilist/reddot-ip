import requests
import urllib3
from colorama import Fore, Style, init

# Suppress insecure SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
init(autoreset=True)

class ReddotWAF:
    def __init__(self, target):
        self.target = target.replace("https://", "").replace("http://", "").split('/')[0]
        self.url = f"http://{self.target}"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        # Aggressive payloads to trigger WAF reactions (XSS, SQLi, LFI)
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
        """Leg 1: Detect identity via HTTP Fingerprinting"""
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
        """Leg 2: Aggressive - Trigger blockade to confirm WAF presence"""
        self.log("Launching mini-payloads to test WAF reactivity...", "info")
        
        for name, payload in self.malicious_payloads.items():
            try:
                # Send payload via URL parameter
                test_url = f"{self.url}/?search={payload}"
                r = requests.get(test_url, headers=self.headers, timeout=10, verify=False)
                
                # If blocked (403, 406, 501) or different response, WAF is likely active
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
            print(f"{Fore.YELLOW}[!] STATUS: High risk. Avoid aggressive brute-forcing to prevent IP banning.")
            
            # Bypass Analysis
            print(f"\n{Fore.CYAN}[BYPASS HINT]:")
            if waf_name == "Cloudflare":
                print(f"  - Look for the Real Origin IP (Use reddot_ip.py)")
                print(f"  - Try changing the Host Header or probe unprotected subdomains.")
            else:
                print(f"  - Experiment with HTTP Parameter Pollution (HPP)")
                print(f"  - Use Proxy/VPN rotation to evade rate-limiting.")
        else:
            self.log("No WAF detected or WAF is in monitoring mode (Transparent).", "safe")
            print(f"{Fore.GREEN}[+] STATUS: Path is clear. You can proceed with aggressive scanning.")

if __name__ == "__main__":
    target = input(f"{Fore.WHITE}Enter Target Domain to check WAF: ")
    if target:
        wf = ReddotWAF(target)
        wf.check()
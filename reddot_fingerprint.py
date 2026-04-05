import requests
import urllib3
import concurrent.futures
from colorama import Fore, init
import os
import threading
import socket
import ssl
import codecs
import mmh3

# Suppress SSL Warnings for direct IP connections
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
init(autoreset=True)

class ReddotFingerprint:
    def __init__(self, target_domain, ip_list_file):
        self.target_domain = target_domain.replace("https://", "").replace("http://", "").split('/')[0]
        self.target_url = f"https://{self.target_domain}"
        self.ip_list_file = ip_list_file
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Reddot/7.0 Fingerprinter'}
        self.log_lock = threading.Lock()
        
        # Identity Profile Storage
        self.target_profile = {
            "favicon_hash": None,
            "server_header": None,
            "x_powered_by": None
        }
        
    def get_favicon_hash(self, url):
        """Calculate MurmurHash3 of the favicon (Shodan Standard)"""
        try:
            favicon_url = f"{url}/favicon.ico"
            r = requests.get(favicon_url, headers=self.headers, timeout=5, verify=False)
            if r.status_code == 200 and len(r.content) > 0:
                favicon_base64 = codecs.encode(r.content, "base64")
                return mmh3.hash(favicon_base64)
            return None
        except:
            return None

    def extract_ssl_cert_name(self, ip):
        """Extract the Common Name (CN) from the IP's direct SSL certificate"""
        try:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            with socket.create_connection((ip, 443), timeout=3) as sock:
                with context.wrap_socket(sock, server_hostname=ip) as ssock:
                    cert = ssock.getpeercert(binary_form=False)
                    for item in cert.get('subject', ()):
                        for k, v in item:
                            if k == 'commonName':
                                return v.lower()
        except:
            return None
        return None

    def profile_target(self):
        """Phase 1: Build the DNA profile of the shielded target"""
        print(f"\n{Fore.CYAN}[*] PHASE 1: INITIATING DEEP TARGET PROFILING...{Fore.WHITE}")
        print(f"{Fore.CYAN}[*] Target: {self.target_domain}{Fore.WHITE}")
        
        try:
            # Get Headers
            r = requests.get(self.target_url, headers=self.headers, timeout=10, verify=False)
            self.target_profile["server_header"] = r.headers.get("Server", "UNKNOWN")
            self.target_profile["x_powered_by"] = r.headers.get("X-Powered-By", "UNKNOWN")
            
            # Get Favicon Hash
            self.target_profile["favicon_hash"] = self.get_favicon_hash(self.target_url)
            
            print(f"{Fore.GREEN}[+] Target DNA Profile Successfully Extracted:{Fore.WHITE}")
            print(f"    -> Favicon Hash : {Fore.YELLOW}{self.target_profile['favicon_hash']}{Fore.WHITE}")
            print(f"    -> Server Stack : {Fore.YELLOW}{self.target_profile['server_header']}{Fore.WHITE}")
            print(f"    -> Framework    : {Fore.YELLOW}{self.target_profile['x_powered_by']}{Fore.WHITE}\n")
            return True
            
        except Exception as e:
            print(f"{Fore.RED}[!] Failed to profile target: {str(e)}{Fore.WHITE}")
            return False

    def scan_candidate(self, ip):
        """Phase 2 & 3: Scan candidate IP and perform deep cross-matching"""
        ip = ip.strip()
        if not ip: return
        
        confidence = 0
        match_reasons = []
        
        # 1. SSL Certificate Inspection (Ultimate Bypass)
        ssl_cn = self.extract_ssl_cert_name(ip)
        if ssl_cn and (self.target_domain in ssl_cn or ssl_cn in self.target_domain):
            confidence += 80
            match_reasons.append(f"SSL_CERT_MATCH [{ssl_cn}]")

        # 2. Favicon Hash Correlation
        ip_favicon = self.get_favicon_hash(f"http://{ip}")
        if not ip_favicon:
            ip_favicon = self.get_favicon_hash(f"https://{ip}")
            
        if ip_favicon and ip_favicon == self.target_profile["favicon_hash"]:
            confidence += 50
            match_reasons.append(f"FAVICON_HASH_MATCH [{ip_favicon}]")
            
        # 3. Header Fingerprinting
        try:
            r = requests.get(f"http://{ip}", headers=self.headers, timeout=3, verify=False)
            ip_server = r.headers.get("Server", "N/A")
            
            if ip_server != "UNKNOWN" and ip_server != "N/A" and ip_server == self.target_profile["server_header"]:
                # Exclude generic Cloudflare/Akamai headers from adding confidence
                if "cloudflare" not in ip_server.lower() and "akamai" not in ip_server.lower():
                    confidence += 20
                    match_reasons.append(f"SERVER_STACK_MATCH [{ip_server}]")
        except:
            pass

        # Logging Logic
        with self.log_lock:
            if confidence >= 80:
                print(f"\n{Fore.GREEN}======================================================================{Fore.WHITE}")
                print(f"{Fore.GREEN}[+] [STATUS=CONFIRMED] [CLASS=ORIGIN_IP_EXPOSED] [PRIORITY=CRITICAL]{Fore.WHITE}")
                print(f"    TARGET_IP  : {Fore.CYAN}{ip}{Fore.WHITE}")
                print(f"    CONFIDENCE : {Fore.GREEN}{min(confidence, 100)}%{Fore.WHITE}")
                print(f"    VECTORS    : {', '.join(match_reasons)}")
                print(f"    ANALYSIS   : Infrastructure DNA perfectly matches the shielded target.")
                print(f"    AI_ACTION  : Update /etc/hosts to bypass WAF and execute Module 6 directly.")
                print(f"{Fore.GREEN}======================================================================{Fore.WHITE}")
            
            elif confidence >= 50:
                print(f"\n{Fore.YELLOW}----------------------------------------------------------------------{Fore.WHITE}")
                print(f"{Fore.YELLOW}[!] [STATUS=SUSPICIOUS] [CLASS=POSSIBLE_BACKEND] [PRIORITY=HIGH]{Fore.WHITE}")
                print(f"    TARGET_IP  : {Fore.CYAN}{ip}{Fore.WHITE}")
                print(f"    CONFIDENCE : {Fore.YELLOW}{min(confidence, 100)}%{Fore.WHITE}")
                print(f"    VECTORS    : {', '.join(match_reasons)}")
                print(f"    ANALYSIS   : Strong visual/structural correlation found. Could be staging/dev server.")
                print(f"{Fore.YELLOW}----------------------------------------------------------------------{Fore.WHITE}")
            
            # Print a subtle progress indicator for IPs that don't match
            else:
                print(f"{Fore.BLACK}{Fore.LIGHTBLACK_EX}[-] IP {ip} rejected (Confidence: {confidence}%){Fore.WHITE}", end='\r')

    def run(self):
        print(f"\n{Fore.RED}██████╗ ███████╗██████╗ ██████╗  ██████╗ ████████╗{Fore.WHITE}")
        print(f"{Fore.RED}██╔══██╗██╔════╝██╔══██╗██╔══██╗██╔═══██╗╚══██╔══╝{Fore.WHITE}")
        print(f"{Fore.RED}██████╔╝█████╗  ██║  ██║██║  ██║██║   ██║   ██║   {Fore.WHITE}")
        print(f"{Fore.RED}██╔══██╗██╔══╝  ██║  ██║██║  ██║██║   ██║   ██║   {Fore.WHITE}")
        print(f"{Fore.RED}██║  ██║███████╗██████╔╝██████╔╝╚██████╔╝   ██║   {Fore.WHITE}")
        print(f"{Fore.RED}╚═╝  ╚═╝╚══════╝╚═════╝ ╚═════╝  ╚═════╝    ╚═╝   {Fore.WHITE}")
        print(f"{Fore.DARK_GREY}      [ MODULE 7 : IDENTITY FINGERPRINT MATCHING ]{Fore.WHITE}")
        
        if not self.profile_target():
            return
            
        if not os.path.exists(self.ip_list_file):
            print(f"{Fore.RED}[!] Candidate IP file '{self.ip_list_file}' not found!{Fore.WHITE}")
            return
            
        print(f"\n{Fore.CYAN}[*] PHASE 2: LAUNCHING GLOBAL CROSS-MATCHING...{Fore.WHITE}")
        
        try:
            with open(self.ip_list_file, 'r') as f:
                ips = [line.strip() for line in f if line.strip()]
            
            print(f"{Fore.YELLOW}[*] Loaded {len(ips)} candidate IPs. Initiating silent reconnaissance...{Fore.WHITE}\n")
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
                executor.map(self.scan_candidate, ips)
                
        except KeyboardInterrupt:
            print(f"\n\n{Fore.RED}[!] Reconnaissance aborted by user.{Fore.WHITE}")
            
        print(f"\n\n{Fore.CYAN}[*] MODULE 7 EXECUTION COMPLETE.{Fore.WHITE}\n")

if __name__ == "__main__":
    target = input("Enter Shielded Target Domain (e.g., target.com) : ")
    ip_file = input("Enter Candidate IP List File (e.g., ips.txt)  : ")
    if target and ip_file:
        ReddotFingerprint(target, ip_file).run()
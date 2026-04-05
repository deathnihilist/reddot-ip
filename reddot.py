import os
import sys
import importlib
from colorama import Fore, Style, init

init(autoreset=True)

class ReddotFramework:
    def __init__(self):
        self.target = ""
        self.developer = "Deathnihilist"
        self.collected_ips = set() # <--- PENAMPUNG IP OTOMATIS (Mencegah duplikat)
        
        # KONFIGURASI MODUL
        self.MODULE_MAP = {
            "1": {"name": "IP Origin Finder", "desc": "Find real server IP & neighbors.", "file": "reddot_ip", "class": "ReddotIP"},
            "2": {"name": "Digital DNA Detector", "desc": "100-Legs Fingerprinting & Leaks.", "file": "reddot_detector", "class": "ReddotDetector"},
            "3": {"name": "WAF Fingerprinting", "desc": "Detect Firewalls & analyze bypass.", "file": "reddot_waf", "class": "ReddotWAF"},
            "4": {"name": "Sniper Port Scanner", "desc": "Detect versions & critical backdoors.", "file": "reddot_scanner", "class": "ReddotScanner"},
            "5": {"name": "Shadow Sub-Hunter", "desc": "Passive & Active Shadow Discovery.", "file": "reddot_subhunter", "class": "ReddotSubHunter"},
            "6": {"name": "Wraith Vuln Engine", "desc": "Shadow Probing & CVE Matcher.", "file": "reddot_vultuner", "class": "ReddotVulnTunner"},
            "7": {"name": "Identity Matcher", "desc": "Deep SSL & Favicon Fingerprinting.", "file": "reddot_fingerprint", "class": "ReddotFingerprint"},
        }

    def banner(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"""{Fore.RED}
    ██████╗ ███████╗██████╗ ██████╗  ██████╗ ████████╗
    ██╔══██╗██╔════╝██╔══██╗██╔══██╗██╔═══██╗╚══██╔══╝
    ██████╔╝█████╗  ██║  ██║██║  ██║██║   ██║   ██║   
    ██╔══██╗██╔══╝  ██║  ██║██║  ██║██║   ██║   ██║   
    ██║  ██║███████╗██████╔╝██████╔╝╚██████╔╝   ██║   
    ╚═╝  ╚═╝╚══════╝╚═════╝ ╚═════╝  ╚═════╝    ╚═╝
    {Fore.WHITE}      [ MULTI-FUNCTION RECON FRAMEWORK ]
    {Fore.YELLOW}      [ DEVELOPER: {self.developer} | VERSION: 7.0-PRO ]

    {Fore.CYAN}QUICK START:
    {Fore.WHITE}1. {Fore.YELLOW}set target <domain>{Fore.WHITE} | 2. {Fore.YELLOW}run <number>{Fore.WHITE} | 3. {Fore.YELLOW}back/clear{Fore.WHITE}

    {Fore.CYAN}AVAILABLE MODULES:""")
        
        for key, info in self.MODULE_MAP.items():
            print(f"    {Fore.WHITE}[{Fore.RED}{key}{Fore.WHITE}] {Fore.YELLOW}{info['name']:<20}{Fore.WHITE} : {info['desc']}")

        print(f"""
    {Fore.CYAN}SYSTEM COMMANDS:
    {Fore.WHITE}- {Fore.YELLOW}show options{Fore.WHITE} | {Fore.YELLOW}help{Fore.WHITE} | {Fore.YELLOW}clear{Fore.WHITE} | {Fore.YELLOW}exit reddot{Fore.WHITE}""")

    def execute_module(self, choice):
        if choice not in self.MODULE_MAP:
            print(f"{Fore.RED}[!] Module {choice} not found.")
            return

        mod_info = self.MODULE_MAP[choice]
        try:
            # Dynamic Import
            module = importlib.import_module(mod_info['file'])
            instance_class = getattr(module, mod_info['class'])
            
            print(f"{Fore.CYAN}[*] Launching {mod_info['name']}...")

            # KHUSUS MODUL 7: Cek memori otomatis
            if choice == "7":
                if self.collected_ips:
                    print(f"{Fore.GREEN}[+] Auto-loading {len(self.collected_ips)} IPs discovered in this session.{Fore.WHITE}")
                    # Kirim list IP langsung ke Modul 7
                    instance = instance_class(self.target, list(self.collected_ips))
                else:
                    # Fallback jika memori kosong
                    print(f"{Fore.YELLOW}[!] No IPs collected from Module 1 or 5 yet.{Fore.WHITE}")
                    ip_file = input(f"{Fore.YELLOW}[?] Path to Candidate IP List (e.g., ips.txt): {Fore.WHITE}").strip()
                    if not os.path.exists(ip_file):
                        print(f"{Fore.RED}[!] Error: File '{ip_file}' not found."); return
                    instance = instance_class(self.target, ip_file)
            else:
                instance = instance_class(self.target)
            
            # Jalankan modul & tangkap hasilnya (jika modul mengembalikan list IP)
            result = None
            if hasattr(instance, 'run'): result = instance.run()
            elif hasattr(instance, 'scan'): result = instance.scan(self.target)
            elif hasattr(instance, 'check'): result = instance.check()
            
            # Jika modul me-return list IP, simpan ke memori
            if isinstance(result, list):
                for ip in result:
                    if ip:
                        self.collected_ips.add(ip)
                        print(f"{Fore.MAGENTA}[SYSTEM] IP {ip} cached for Module 7.{Fore.WHITE}")
                
        except Exception as e:
            print(f"{Fore.RED}[!] Execution Error in {mod_info['name']}: {e}")

    def main_menu(self):
        self.banner()
        while True:
            target_display = f"({Fore.RED}{self.target}{Fore.WHITE})" if self.target else ""
            cmd = input(f"{Fore.WHITE}reddot {target_display} > ").strip().lower()

            if cmd == "exit reddot": break
            elif cmd in ["help", "clear"]: self.banner()
            elif cmd.startswith("set target "):
                new_target = cmd.replace("set target ", "").replace("https://", "").replace("http://", "").split('/')[0]
                # Jika ganti target, bersihkan cache IP yang lama
                if new_target != self.target:
                    self.target = new_target
                    self.collected_ips.clear() 
                    print(f"{Fore.GREEN}[+] Target locked: {self.target} (IP cache cleared){Fore.WHITE}")
            elif cmd in ["back", "unset"]:
                self.target = ""
                self.collected_ips.clear() # Bersihkan cache saat lepas target
                print(f"{Fore.YELLOW}[*] Target released (IP cache cleared).{Fore.WHITE}")
            elif cmd.startswith("run "):
                if not self.target:
                    print(f"{Fore.RED}[!] Error: Target is not defined."); continue
                self.execute_module(cmd.replace("run ", ""))
            elif cmd == "show options":
                print(f"\n{Fore.CYAN}[TARGET] : {Fore.YELLOW}{self.target if self.target else 'NONE'}\n")

if __name__ == "__main__":
    ReddotFramework().main_menu()
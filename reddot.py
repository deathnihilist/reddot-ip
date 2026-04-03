import os
import sys
import importlib
from colorama import Fore, Style, init

init(autoreset=True)

class ReddotFramework:
    def __init__(self):
        self.target = ""
        self.developer = "Deathnihilist"
        # KONFIGURASI MODUL: Tambah di sini jika ada file .py baru
        self.MODULE_MAP = {
            "1": {"name": "IP Origin Finder", "desc": "Find real server IP & neighbors.", "file": "reddot_ip", "class": "ReddotIP"},
            "2": {"name": "Digital DNA Detector", "desc": "100-Legs Fingerprinting & Leaks.", "file": "reddot_detector", "class": "ReddotDetector"},
            "3": {"name": "WAF Fingerprinting", "desc": "Detect Firewalls & analyze bypass.", "file": "reddot_waf", "class": "ReddotWAF"},
            "4": {"name": "Sniper Port Scanner", "desc": "Detect versions & critical backdoors.", "file": "reddot_scanner", "class": "ReddotScanner"},
            "5": {"name": "Shadow Sub-Hunter", "desc": "Passive & Active Shadow Discovery.", "file": "reddot_subhunter", "class": "ReddotSubHunter"},
            "6": {"name": "Wraith Vuln Engine", "desc": "Shadow Probing & CVE Matcher.", "file": "reddot_vultuner", "class": "ReddotVulnTunner"},
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
    {Fore.YELLOW}      [ DEVELOPER: {self.developer} | VERSION: 3.0 ]

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
            # Dynamic Import: Memanggil file hanya saat dibutuhkan (Licin!)
            module = importlib.import_lib(mod_info['file'])
            instance_class = getattr(module, mod_info['class'])
            
            # Menjalankan modul
            print(f"{Fore.CYAN}[*] Launching {mod_info['name']}...")
            instance = instance_class(self.target)
            
            # Menyesuaikan cara panggil tiap modul (IP Scanner butuh .scan, yang lain .run)
            if hasattr(instance, 'run'): instance.run()
            elif hasattr(instance, 'scan'): instance.scan(self.target)
            elif hasattr(instance, 'check'): instance.check()
                
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
                self.target = cmd.replace("set target ", "").replace("https://", "").replace("http://", "").split('/')[0]
                print(f"{Fore.GREEN}[+] Target locked: {self.target}")
            elif cmd in ["back", "unset"]:
                self.target = ""
                print(f"{Fore.YELLOW}[*] Target released.")
            elif cmd.startswith("run "):
                if not self.target:
                    print(f"{Fore.RED}[!] Error: Target is not defined."); continue
                self.execute_module(cmd.replace("run ", ""))
            elif cmd == "show options":
                print(f"\n{Fore.CYAN}[TARGET] : {Fore.YELLOW}{self.target if self.target else 'NONE'}\n")

if __name__ == "__main__":
    ReddotFramework().main_menu()
import os
import sys
from colorama import Fore, Style, init

# Import our custom modules
try:
    from reddot_ip import ReddotIP
    from reddot_detector import ReddotDetector
    from reddot_waf import ReddotWAF
    from reddot_scanner import ReddotScanner
    from reddot_subhunter import ReddotSubHunter
    from reddot_vultuner import ReddotVulnTunner
except ImportError as e:
    print(f"{Fore.RED}[!] Error: Required modules not found! ({e})")

init(autoreset=True)

class ReddotConsole:
    def __init__(self):
        self.target = ""
        self.developer = "Deathnihilist"

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

    {Fore.CYAN}AVAILABLE MODULES:
    {Fore.WHITE}[{Fore.RED}1{Fore.WHITE}] {Fore.YELLOW}IP Origin Finder{Fore.WHITE}    : Find real server IP & neighbors.
    [{Fore.RED}2{Fore.WHITE}] {Fore.YELLOW}Digital DNA Detector{Fore.WHITE} : 100-Legs Fingerprinting & Leaks.
    [{Fore.RED}3{Fore.WHITE}] {Fore.YELLOW}WAF Fingerprinting{Fore.WHITE}  : Detect Firewalls & analyze bypass.
    [{Fore.RED}4{Fore.WHITE}] {Fore.YELLOW}Sniper Port Scanner{Fore.WHITE}  : Detect versions & critical backdoors.
    [{Fore.RED}5{Fore.WHITE}] {Fore.YELLOW}Shadow Sub-Hunter{Fore.WHITE}    : Passive & Active Shadow Discovery.
    [{Fore.RED}6{Fore.WHITE}] {Fore.YELLOW}Wraith Vuln Engine{Fore.WHITE}   : Shadow Probing & CVE Matcher.
        """)

    def main_menu(self):
        while True:
            target_display = f"({Fore.RED}{self.target}{Fore.WHITE})" if self.target else ""
            cmd = input(f"{Fore.WHITE}reddot {target_display} > ").strip().lower()

            if cmd == "exit reddot":
                print(f"{Fore.YELLOW}[!] Shutting down Reddot Framework...")
                break
            
            elif cmd in ["help", "clear"]:
                self.banner()

            elif cmd.startswith("set target "):
                self.target = cmd.replace("set target ", "").replace("https://", "").replace("http://", "").split('/')[0]
                print(f"{Fore.GREEN}[+] Target locked: {self.target}")

            elif cmd in ["back", "unset"]:
                self.target = ""
                print(f"{Fore.YELLOW}[*] Target released.")

            elif cmd == "run 1":
                if not self.target: print(f"{Fore.RED}[!] Set target first."); continue
                ReddotIP().scan(self.target)

            elif cmd == "run 2":
                if not self.target: print(f"{Fore.RED}[!] Set target first."); continue
                det = ReddotDetector(self.target)
                det.detect_headers(); det.run_centipede(); det.display_report()

            elif cmd == "run 3":
                if not self.target: print(f"{Fore.RED}[!] Set target first."); continue
                ReddotWAF(self.target).check()

            elif cmd == "run 4":
                if not self.target: print(f"{Fore.RED}[!] Set target first."); continue
                ReddotScanner(self.target).run()

            elif cmd == "run 5":
                if not self.target: print(f"{Fore.RED}[!] Set target first."); continue
                ReddotSubHunter(self.target).run()

            elif cmd == "run 6":
                if not self.target: print(f"{Fore.RED}[!] Set target first."); continue
                ReddotVulnTunner(self.target).run()

if __name__ == "__main__":
    console = ReddotConsole()
    console.banner()
    console.main_menu()
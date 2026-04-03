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
    print(f"Error: Required modules not found! ({e})")

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

    {Fore.CYAN}QUICK START:
    {Fore.WHITE}1. {Fore.YELLOW}set target <domain>{Fore.WHITE} (e.g., set target site.com)
    2. {Fore.YELLOW}run <number>{Fore.WHITE}       (Select tool from the list below)
    3. {Fore.YELLOW}back / unset{Fore.WHITE}      (Clear current target and return)

    {Fore.CYAN}AVAILABLE MODULES:
    {Fore.WHITE}[{Fore.RED}1{Fore.WHITE}] {Fore.YELLOW}IP Origin Finder{Fore.WHITE}    : Find real server IP & neighbors (Grid Mode).
    [{Fore.RED}2{Fore.WHITE}] {Fore.YELLOW}Tech Stack Detector{Fore.WHITE} : 100-Legs aggressive Fingerprinting & Leaks.
    [{Fore.RED}3{Fore.WHITE}] {Fore.YELLOW}WAF Fingerprinting{Fore.WHITE}  : Detect Firewalls & analyze bypass methods.
    [{Fore.RED}4{Fore.WHITE}] {Fore.YELLOW}Sniper Port Scanner{Fore.WHITE}  : Detect versions & find critical backdoors.
    [{Fore.RED}5{Fore.WHITE}] {Fore.YELLOW}Subdomain Hunter{Fore.WHITE}    : Passive & Active Shadow Discovery.
    [{Fore.RED}6{Fore.WHITE}] {Fore.YELLOW}Wraith Vuln Engine{Fore.WHITE}   : Shadow Probing & CVE Matcher (Bypass Mode).

    {Fore.CYAN}SYSTEM COMMANDS:
    {Fore.WHITE}- {Fore.YELLOW}show options{Fore.WHITE}       : Display current configuration.
    - {Fore.YELLOW}back{Fore.WHITE}               : Unset current target.
    - {Fore.YELLOW}clear{Fore.WHITE}              : Clear the terminal screen.
    - {Fore.YELLOW}help{Fore.WHITE}               : Display this menu.
    - {Fore.YELLOW}exit reddot{Fore.WHITE}        : Terminate the session and exit.
        """)

    def main_menu(self):
        while True:
            # Dynamic prompt based on target status
            target_display = f"({Fore.RED}{self.target}{Fore.WHITE})" if self.target else ""
            cmd = input(f"{Fore.WHITE}reddot {target_display} > ").strip().lower()

            if cmd == "exit reddot":
                print(f"{Fore.YELLOW}[!] Shutting down Reddot Framework... Goodbye.")
                break
            
            elif cmd == "help":
                self.banner()

            elif cmd.startswith("set target "):
                self.target = cmd.replace("set target ", "").replace("https://", "").replace("http://", "").split('/')[0]
                print(f"{Fore.GREEN}[+] Target locked: {self.target}")

            elif cmd == "back" or cmd == "unset target" or cmd == "unset":
                if not self.target:
                    print(f"{Fore.CYAN}[*] No target is currently set.")
                else:
                    self.target = ""
                    print(f"{Fore.YELLOW}[*] Target released. Returning to main menu.")

            elif cmd == "show options":
                print(f"\n[{Fore.CYAN}CONFIGURATION{Fore.WHITE}]")
                print(f"TARGET : {Fore.YELLOW}{self.target if self.target else 'NOT SET'}")
                print(f"STATUS : {Fore.GREEN if self.target else Fore.RED}{'Ready to engage' if self.target else 'Waiting for input'}\n")

            elif cmd == "clear":
                self.banner()

            elif cmd.startswith("run "):
                if not self.target: 
                    print(f"{Fore.RED}[!] Error: Target is not defined. Use 'set target <domain>' first.")
                    continue
                
                if cmd == "run 1":
                    scanner = ReddotIP()
                    scanner.scan(self.target)
                elif cmd == "run 2":
                    det = ReddotDetector(self.target)
                    det.detect_headers()
                    det.run_centipede()
                    det.display_report()
                elif cmd == "run 3":
                    wf = ReddotWAF(self.target)
                    wf.check()
                # --- TAMBAHKAN INI ---
                elif cmd == "run 4":
                    scanner = ReddotScanner(self.target)
                    scanner.run()
                # ---------------------
                elif cmd == "run 5":
                     hunter = ReddotSubHunter(self.target)
                     hunter.run()
                elif cmd == "run 6":
                    if not self.target: 
                        print(f"{Fore.RED}[!] Error: No target.")
                        continue
                    # Panggil Vulnerability Engine
                    vuln = ReddotVulnTunner(self.target)
                    vuln.run()
                else:
                    print(f"{Fore.RED}[!] Error: Module '{cmd}' not found.")

            else:
                if cmd:
                    print(f"{Fore.RED}[?] Unknown command. Type 'help' to see available options.")

if __name__ == "__main__":
    console = ReddotConsole()
    console.banner()
    console.main_menu()
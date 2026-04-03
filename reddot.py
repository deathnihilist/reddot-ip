import sys
import os
from colorama import Fore, Style, init

# Import modul-modul buatan kita
try:
    from reddot_ip import ReddotIP
    from reddot_detector import ReddotDetector
    from reddot_waf import ReddotWAF
except ImportError as e:
    print(f"Error: Pastikan semua file modul ada di folder yang sama! ({e})")

init(autoreset=True)

class ReddotConsole:
    def __init__(self):
        self.target = ""

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
    {Fore.YELLOW}      [ DEVELOPER: Deathnihilist | VERSION: 3.0 ]
        """)

    def main_menu(self):
        while True:
            # Prompt ala Metasploit
            target_display = f"({Fore.RED}{self.target}{Fore.WHITE})" if self.target else ""
            cmd = input(f"{Fore.WHITE}reddot {target_display} > ").strip().lower()

            if cmd == "exit reddot":
                print(f"{Fore.YELLOW}[!] Exiting Reddot Framework...")
                break
            
            elif cmd == "help":
                print(f"""
    Commands:
    ---------
    set target <domain>  : Tentukan target (e.g: set target site.com)
    show options         : Lihat target saat ini
    run 1                : Jalankan IP Origin Finder (Grid Mode)
    run 2                : Jalankan Tech Stack Detector (100 Kaki)
    run 3                : Jalankan WAF Fingerprinting & Bypass
    clear                : Bersihkan layar
    exit reddot          : Keluar dari program
                """)

            elif cmd.startswith("set target "):
                self.target = cmd.replace("set target ", "").replace("https://", "").replace("http://", "").split('/')[0]
                print(f"{Fore.GREEN}[+] Target set to: {self.target}")

            elif cmd == "show options":
                print(f"\nTarget: {self.target if self.target else 'Not Set'}\n")

            elif cmd == "clear":
                self.banner()

            elif cmd == "run 1":
                if not self.target: print(f"{Fore.RED}[!] Set target dulu bos!"); continue
                scanner = ReddotIP()
                scanner.scan(self.target)

            elif cmd == "run 2":
                if not self.target: print(f"{Fore.RED}[!] Set target dulu bos!"); continue
                det = ReddotDetector(self.target)
                det.detect_headers()
                det.run_centipede()
                det.display_report()

            elif cmd == "run 3":
                if not self.target: print(f"{Fore.RED}[!] Set target dulu bos!"); continue
                wf = ReddotWAF(self.target)
                wf.check()

            else:
                if cmd:
                    print(f"{Fore.RED}[?] Unknown command: {cmd}. Type 'help' for commands.")

if __name__ == "__main__":
    console = ReddotConsole()
    console.banner()
    console.main_menu()
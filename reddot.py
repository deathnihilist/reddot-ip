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
    {Fore.WHITE}1. {Fore.YELLOW}set target <domain>{Fore.WHITE} (e.g., set target google.com)
    2. {Fore.YELLOW}run <number>{Fore.WHITE}       (Select tool from the list below)

    {Fore.CYAN}AVAILABLE MODULES:
    {Fore.WHITE}[{Fore.RED}1{Fore.WHITE}] {Fore.YELLOW}IP Origin Finder{Fore.WHITE}    : Find real server IP & neighbors (Grid Mode).
    [{Fore.RED}2{Fore.WHITE}] {Fore.YELLOW}Tech Stack Detector{Fore.WHITE} : 100-Legs aggressive Fingerprinting & Leaks.
    [{Fore.RED}3{Fore.WHITE}] {Fore.YELLOW}WAF Fingerprinting{Fore.WHITE}  : Detect Firewalls & analyze bypass methods.

    {Fore.CYAN}SYSTEM COMMANDS:
    {Fore.WHITE}- {Fore.YELLOW}show options{Fore.WHITE}       : Display current configuration.
    - {Fore.YELLOW}clear{Fore.WHITE}              : Clear the terminal screen.
    - {Fore.YELLOW}exit reddot{Fore.WHITE}        : Terminate the session and exit.
        """)

    def main_menu(self):
        while True:
            target_display = f"({Fore.RED}{self.target}{Fore.WHITE})" if self.target else ""
            cmd = input(f"{Fore.WHITE}reddot {target_display} > ").strip().lower()

            if cmd == "exit reddot":
                print(f"{Fore.YELLOW}[!] Shutting down Reddot Framework... Goodbye.")
                break
            
            elif cmd == "help":
                self.banner() # Show the guide again

            elif cmd.startswith("set target "):
                self.target = cmd.replace("set target ", "").replace("https://", "").replace("http://", "").split('/')[0]
                print(f"{Fore.GREEN}[+] Target locked: {self.target}")

            elif cmd == "show options":
                print(f"\n[{Fore.CYAN}CONFIGURATION{Fore.WHITE}]")
                print(f"TARGET : {Fore.YELLOW}{self.target if self.target else 'NOT SET'}")
                print(f"STATUS : {Fore.GREEN}Ready to engage\n")

            elif cmd == "clear":
                self.banner()

            elif cmd == "run 1":
                if not self.target: 
                    print(f"{Fore.RED}[!] Error: Target is not defined. Use 'set target <domain>' first.")
                    continue
                scanner = ReddotIP()
                scanner.scan(self.target)

            elif cmd == "run 2":
                if not self.target: 
                    print(f"{Fore.RED}[!] Error: Target is not defined.")
                    continue
                det = ReddotDetector(self.target)
                det.detect_headers()
                det.run_centipede()
                det.display_report()

            elif cmd == "run 3":
                if not self.target: 
                    print(f"{Fore.RED}[!] Error: Target is not defined.")
                    continue
                wf = ReddotWAF(self.target)
                wf.check()

            else:
                if cmd:
                    print(f"{Fore.RED}[?] Unknown command. Type 'help' to see available options.")
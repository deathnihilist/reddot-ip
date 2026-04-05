import socket
import ssl
import concurrent.futures
from colorama import Fore, Style, init

init(autoreset=True)

class ReddotScanner:
    def __init__(self, target):
        self.target = target
        # Critical ports that often lead to "Backdoors" or Data Leaks
        self.critical_ports = {
            21: "FTP (File Transfer) - Risk: Brute Force / Plaintext",
            22: "SSH (Remote Access) - Risk: Brute Force",
            23: "Telnet (Old Remote) - Risk: Extremely Insecure",
            25: "SMTP (Email) - Risk: Mail Relay",
            53: "DNS (Domain) - Risk: Zone Transfer",
            80: "HTTP (Web) - Risk: Web Exploit",
            110: "POP3 (Email)",
            139: "NetBIOS - Risk: SMB Exploit",
            443: "HTTPS (Secure Web)",
            445: "SMB (File Sharing) - Risk: EternalBlue / Ransomware",
            1433: "MSSQL (Database)",
            3306: "MySQL (Database) - Risk: Data Theft",
            3389: "RDP (Remote Desktop) - Risk: BlueKeep / Brute Force",
            5432: "PostgreSQL (Database)",
            8080: "HTTP-Proxy / Alt-Web",
            27017: "MongoDB - Risk: Unauthenticated Access"
        }
        self.found_ports = []

    def log(self, msg, status="info"):
        colors = {"info": Fore.CYAN, "found": Fore.GREEN, "crit": Fore.RED, "warn": Fore.YELLOW}
        prefix = {"info": "[*]", "found": "[+]", "crit": "[!]", "warn": "[#]"}
        print(f"{colors.get(status)}{prefix.get(status)} {msg}")

    def grab_banner(self, s, port):
        """Aggressive Banner Grabbing to bypass 'Hidden' versions"""
        try:
            s.settimeout(2)
            # Send a generic probe to force the service to speak
            if port in [80, 8080, 443]:
                s.send(b"GET / HTTP/1.1\r\nHost: " + self.target.encode() + b"\r\n\r\n")
            else:
                s.send(b"\x00") # Small nudge for other services
            
            banner = s.recv(1024).decode(errors='ignore').strip()
            if banner:
                # Clean up the banner for display
                return banner.replace('\n', ' ').replace('\r', '')[:100]
            return "No banner (Service silent)"
        except:
            return "No response (Protected/Filtered)"

    def scan_port(self, port):
        """The Sniper Leg: Fast connection and immediate identification"""
        try:
            # Create a socket and try to connect
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1.5) # Fast timeout to avoid hanging
            result = sock.connect_ex((self.target, port))
            
            if result == 0:
                service_info = self.critical_ports.get(port, "Unknown Service")
                banner = self.grab_banner(sock, port)
                
                self.found_ports.append({
                    "port": port,
                    "service": service_info,
                    "banner": banner
                })
                
                status = "crit" if port in [21, 445, 3306, 27017, 3389] else "found"
                self.log(f"Port {port} OPEN | {service_info}", status)
                if banner != "No response (Protected/Filtered)":
                    print(f"    {Fore.WHITE}└── Identity: {Fore.YELLOW}{banner}")
            
            sock.close()
        except:
            pass

    def run(self):
        print(f"\n{Fore.WHITE}--- [ REDDOT SNIPER PORT SCANNER ] ---")
        self.log(f"Scanning target: {self.target}", "info")
        self.log(f"Checking {len(self.critical_ports)} critical entry points...", "info")

        # Multi-threading (100 legs logic) for high speed
        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            executor.map(self.scan_port, self.critical_ports.keys())

        if not self.found_ports:
            self.log("No critical ports exposed. Target has decent perimeter security.", "warn")
        else:
            print(f"\n{Fore.RED}SCAN SUMMARY FOR {self.target}:")
            for p in self.found_ports:
                print(f"{Fore.WHITE}- Port {p['port']}: {p['service']}")

if __name__ == "__main__":
    target = input(f"{Fore.WHITE}Enter Target IP/Domain: ")
    if target:
        scanner = ReddotScanner(target)
        scanner.run()

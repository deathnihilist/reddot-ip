import os
from datetime import datetime
from colorama import Fore

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def save_result(target, data):
    """Fungsi otomatis untuk menyimpan hasil scan ke file teks"""
    filename = f"logs/scan_{target}.txt"
    os.makedirs('logs', exist_ok=True)
    with open(filename, "a") as f:
        f.write(f"[{datetime.now()}] - {data}\n")

def print_status(message, type="info"):
    if type == "info":
        print(f"{Fore.BLUE}[*] {message}")
    elif type == "success":
        print(f"{Fore.GREEN}[+] {message}")
    elif type == "error":
        print(f"{Fore.RED}[!] {message}")
    elif type == "warning":
        print(f"{Fore.YELLOW}[#] {message}")
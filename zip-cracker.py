#!/usr/bin/env python3
import zipfile
import os
import threading
from tqdm import tqdm
import requests
from termcolor import colored, cprint
import pyfiglet
import time
import sys
import random
from concurrent.futures import ThreadPoolExecutor, as_completed

class HackerEffects:
    @staticmethod
    def typing_effect(text, color='green', delay=0.03):
        for char in text:
            sys.stdout.write(colored(char, color))
            sys.stdout.flush()
            time.sleep(delay)
        print()

    @staticmethod
    def random_color_text(text):
        colors = ['red', 'green', 'yellow', 'blue', 'magenta', 'cyan']
        return ''.join([colored(char, random.choice(colors)) for char in text])

    @staticmethod
    def flashing_text(text, color='red', attrs=['blink']):
        return colored(text, color, attrs=attrs)

    @staticmethod
    def show_progress(title):
        colors = ['red', 'green', 'yellow', 'blue', 'magenta', 'cyan']
        with tqdm(total=100, desc=colored(title, random.choice(colors)), 
                 bar_format="{l_bar}%s{bar}%s{r_bar}" % (colored("|", "white"), colored("|", "white"))) as pbar:
            for i in range(100):
                time.sleep(0.02)
                pbar.update(1)

def show_banner():
    os.system('cls' if os.name == 'nt' else 'clear')
    colors = ['red', 'green', 'yellow', 'blue', 'magenta', 'cyan']
    banner_text = "ZIP CRACKER"
    banner = pyfiglet.figlet_format(banner_text, font="slant")
    
    colored_banner = []
    for line in banner.split('\n'):
        colored_banner.append(colored(line, random.choice(colors)))
    print('\n'.join(colored_banner))
    
    print(colored("="*60, "yellow"))
    cprint("Created by: Sunil [Prince4you]", "cyan", attrs=["bold"])
    print(colored("="*60, "yellow"))
    print(HackerEffects.flashing_text("WARNING: For educational purposes only!", "red"))
    print()

class ZipCracker:
    def __init__(self):
        self.found = False
        self.result = None
        self.lock = threading.Lock()
        self.stop_event = threading.Event()
        self.wordlists = {
            '1': ('rockyou.txt', 'https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt'),
            '2': ('10k-most-common.txt', 'https://raw.githubusercontent.com/danielmiessler/SecLists/master/Passwords/Common-Credentials/10k-most-common.txt')
        }

    def download_wordlist(self, url, filename):
        try:
            HackerEffects.typing_effect("[*] Initializing wordlist download...", "cyan")
            
            # Create session with proper headers
            session = requests.Session()
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            })
            
            # Download with streaming and timeout
            response = session.get(url, stream=True, timeout=60)
            response.raise_for_status()
            
            # Get total size for progress bar
            total_size = int(response.headers.get('content-length', 0))
            block_size = 8192  # 8KB chunks
            
            # Create progress bar
            progress = tqdm(total=total_size, unit='iB', unit_scale=True,
                          desc=colored("Downloading", "yellow"),
                          bar_format="{l_bar}%s{bar}%s{r_bar}" % (colored("|", "green"), colored("|", "green")))
            
            # Save file
            with open(filename, 'wb') as f:
                for data in response.iter_content(block_size):
                    progress.update(len(data))
                    f.write(data)
            progress.close()
            
            # Verify download completed
            if total_size != 0 and progress.n != total_size:
                cprint("[-] Download incomplete", "red")
                return False
                
            HackerEffects.typing_effect(f"[+] Wordlist saved: {filename}", "green")
            return True
            
        except requests.exceptions.RequestException as e:
            cprint(f"[-] Download failed: {e}", "red")
            return False
        except Exception as e:
            cprint(f"[-] Error: {e}", "red")
            return False

    def try_password(self, zip_file, password):
        try:
            with zipfile.ZipFile(zip_file) as zf:
                file_in_zip = zf.namelist()[0]
                with zf.open(file_in_zip, pwd=password.encode()) as f:
                    f.read(1)
                return True
        except:
            return False

    def crack_chunk(self, zip_file, chunk):
        for pwd in chunk:
            if self.stop_event.is_set():
                return None
            if self.try_password(zip_file, pwd):
                self.stop_event.set()
                return pwd
        return None

    def crack(self, zip_file, wordlist_file=None, custom_password=None, threads=8):
        try:
            if not zipfile.is_zipfile(zip_file):
                cprint("[-] Not a valid ZIP file", "red")
                return False

            if custom_password:
                HackerEffects.typing_effect("[*] Testing custom password...", "blue")
                if self.try_password(zip_file, custom_password):
                    cprint(f"\n[+] Password found: {custom_password}", "green", attrs=["bold"])
                    with open("cracked.txt", "a") as f:
                        f.write(f"{zip_file}:{custom_password}\n")
                    return True
                else:
                    cprint("\n[-] Custom password incorrect", "red")
                    return False

            try:
                with open(wordlist_file, 'r', errors='ignore') as f:
                    passwords = [line.strip() for line in f if line.strip()]
            except:
                try:
                    with open(wordlist_file, 'rb') as f:
                        passwords = [line.strip().decode('latin-1') for line in f if line.strip()]
                except Exception as e:
                    cprint(f"[-] Error reading wordlist: {e}", "red")
                    return False

            if not passwords:
                cprint("[-] Wordlist is empty", "red")
                return False

            cprint(f"[*] Loaded {len(passwords):,} passwords", "blue")
            cprint(f"[*] Starting attack with {threads} threads...", "magenta")
            print()

            chunk_size = len(passwords) // threads
            chunks = [passwords[i:i + chunk_size] for i in range(0, len(passwords), chunk_size)]

            start_time = time.time()
            found_password = None

            with ThreadPoolExecutor(max_workers=threads) as executor:
                futures = [executor.submit(self.crack_chunk, zip_file, chunk) for chunk in chunks]
                
                with tqdm(total=len(passwords), desc=colored("Brute Force Attack", "red"), 
                         bar_format="{l_bar}%s{bar}%s{r_bar}" % (colored("|", "yellow"), colored("|", "yellow"))) as pbar:
                    for future in as_completed(futures):
                        result = future.result()
                        if result:
                            found_password = result
                            self.stop_event.set()
                            break
                        pbar.update(chunk_size)

            self.stop_event.set()
            
            if found_password:
                cprint(f"\n[+] Password cracked successfully!", "green", attrs=["bold"])
                cprint(f"[+] Password: {found_password}", "green")
                cprint(f"[+] Time taken: {time.time()-start_time:.2f} seconds", "cyan")
                with open("cracked.txt", "a") as f:
                    f.write(f"{zip_file}:{found_password}\n")
                return True
            else:
                cprint("\n[-] Password not found in wordlist", "red")
                return False

        except Exception as e:
            cprint(f"[-] Error: {e}", "red")
            return False

def select_wordlist(cracker):
    print(colored("\nAvailable Wordlists:", "cyan"))
    for key, (name, url) in cracker.wordlists.items():
        print(colored(f"[{key}] {name}", "yellow"))
    
    print(colored("[3] Custom wordlist path", "yellow"))
    choice = input(colored("\n[?] Select wordlist (1-3): ", "cyan")).strip()

    if choice == '3':
        custom_path = input(colored("[?] Enter custom wordlist path: ", "yellow")).strip()
        if not os.path.exists(custom_path):
            cprint("[-] File not found", "red")
            return None
        return custom_path
    
    if choice in cracker.wordlists:
        filename, url = cracker.wordlists[choice]
        if not os.path.exists(filename):
            if not cracker.download_wordlist(url, filename):
                return None
        return filename
    
    cprint("[-] Invalid selection", "red")
    return None

if __name__ == "__main__":
    show_banner()

    cracker = ZipCracker()

    zip_path = input(colored("\n[?] Enter ZIP file path: ", "yellow")).strip()
    if not os.path.exists(zip_path):
        cprint("[-] File not found", "red")
        sys.exit(1)

    print(colored("\nAttack Methods:", "cyan"))
    print(colored("[1] Custom password attack", "yellow"))
    print(colored("[2] Wordlist attack", "yellow"))
    choice = input(colored("\n[?] Select attack method (1/2): ", "cyan")).strip()

    if choice == "1":
        custom_pass = input(colored("[?] Enter custom password: ", "yellow")).strip()
        HackerEffects.show_progress("Launching attack")
        start = time.time()
        cracker.crack(zip_path, custom_password=custom_pass)
    else:
        wordlist = select_wordlist(cracker)
        if not wordlist:
            sys.exit(1)
        
        threads = input(colored("[?] Enter number of threads (default 8): ", "yellow")).strip()
        threads = int(threads) if threads.isdigit() else 8
        
        HackerEffects.show_progress("Initializing cracking engine")
        start = time.time()
        cracker.crack(zip_path, wordlist, threads=threads)

    print()
    HackerEffects.typing_effect("Terminating session...", "red")
    time.sleep(1)
    HackerEffects.typing_effect(HackerEffects.random_color_text("System secure. Goodbye!"), "red")

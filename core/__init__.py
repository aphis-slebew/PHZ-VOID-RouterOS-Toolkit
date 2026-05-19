# PHZ//VOID - Core Package
# Core modules untuk scanning, attack, dan utility

__version__ = "2.1.0"
__author__ = "PHZ//VOID"
__license__ = "MIT"
__description__ = "MikroTik RouterOS Security Testing Framework"

# Core imports
from .utils import ConfigLoader, HackerStyle, Logger
from .scanner import ServiceScanner
from .network_scanner import NetworkScanner

# Version info function
def get_version_info() -> str:
    """Return formatted version information"""
    return f"""
{HackerStyle.GREEN}PHZ//VOID MikroTik Framework{HackerStyle.RESET}
Version     : {__version__}
Author      : {__author__}
Description : {__description__}
License     : {__license__}
"""

# Package metadata
__all__ = [
    'ConfigLoader',
    'HackerStyle', 
    'Logger',
    'ServiceScanner',
    'NetworkScanner',
    'get_version_info'
]
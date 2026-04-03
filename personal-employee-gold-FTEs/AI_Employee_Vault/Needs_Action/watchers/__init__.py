# AI Employee Watchers Package
"""
Watcher modules for AI Employee automation.

This package contains all the watcher implementations that monitor
external data sources and create action files in the vault.
"""

from .base_watcher import BaseWatcher
from .filesystem_watcher import FileSystemWatcher
from .gmail_watcher import GmailWatcher

__all__ = ['BaseWatcher', 'FileSystemWatcher', 'GmailWatcher']

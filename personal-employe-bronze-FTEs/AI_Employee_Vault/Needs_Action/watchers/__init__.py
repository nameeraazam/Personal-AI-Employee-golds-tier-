"""
Watchers package - Monitor external data sources and create action files.

Available watchers:
- GmailWatcher: Monitor Gmail for new important unread emails
- FileSystemWatcher: Monitor a folder for new files
- Orchestrator: Central control for all watchers

Note: Imports are lazy to avoid circular import warnings when running as module.
"""

# Lazy imports to avoid RuntimeWarning when running as python -m watchers.*
def __getattr__(name):
    if name == 'BaseWatcher':
        from .base_watcher import BaseWatcher
        return BaseWatcher
    elif name == 'GmailWatcher':
        from .gmail_watcher import GmailWatcher
        return GmailWatcher
    elif name == 'FileSystemWatcher':
        from .filesystem_watcher import FileSystemWatcher
        return FileSystemWatcher
    elif name == 'Orchestrator':
        from .orchestrator import Orchestrator
        return Orchestrator
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = ['BaseWatcher', 'GmailWatcher', 'FileSystemWatcher', 'Orchestrator']

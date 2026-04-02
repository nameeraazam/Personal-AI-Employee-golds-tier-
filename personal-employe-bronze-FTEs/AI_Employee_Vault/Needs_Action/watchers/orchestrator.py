#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Employee Orchestrator

Central control for all watchers. Start, stop, and monitor all AI Employee services.

Usage:
    python -m watchers.orchestrator start      # Start all watchers
    python -m watchers.orchestrator stop       # Stop all watchers
    python -m watchers.orchestrator status     # Check status
    python -m watchers.orchestrator start gmail    # Start only Gmail watcher
    python -m watchers.orchestrator start file     # Start only File System watcher
"""

import os
import sys
import time
import signal
import subprocess
import json
from datetime import datetime
from typing import Dict, List, Optional


class Orchestrator:
    """
    Orchestrates multiple watchers and AI Employee services.
    """
    
    def __init__(self, vault_path: str):
        """
        Initialize the orchestrator.
        
        Args:
            vault_path: Path to the AI_Employee_Vault
        """
        self.vault_path = os.path.abspath(vault_path)
        self.pid_file = os.path.join(self.vault_path, ".orchestrator.pid")
        self.status_file = os.path.join(self.vault_path, "Logs", "orchestrator_status.json")
        self.log_path = os.path.join(self.vault_path, "Logs")
        
        os.makedirs(self.log_path, exist_ok=True)
        
        # Available watchers
        self.watchers = {
            'gmail': {
                'module': 'watchers.gmail_watcher',
                'name': 'Gmail Watcher',
                'pid': None,
                'status': 'stopped'
            },
            'file': {
                'module': 'watchers.filesystem_watcher',
                'name': 'File System Watcher',
                'pid': None,
                'status': 'stopped'
            }
        }
        
        # Load existing status
        self._load_status()
    
    def _load_status(self):
        """Load status from file."""
        if os.path.exists(self.status_file):
            try:
                with open(self.status_file, 'r') as f:
                    status = json.load(f)
                    for key, watcher in self.watchers.items():
                        if key in status:
                            watcher['status'] = status[key].get('status', 'stopped')
                            watcher['pid'] = status[key].get('pid')
                            watcher['started_at'] = status[key].get('started_at')
            except Exception as e:
                print(f"Warning: Could not load status: {e}")
    
    def _save_status(self):
        """Save status to file."""
        status = {}
        for key, watcher in self.watchers.items():
            status[key] = {
                'status': watcher['status'],
                'pid': watcher['pid'],
                'started_at': watcher.get('started_at'),
                'last_check': datetime.now().isoformat()
            }
        
        try:
            with open(self.status_file, 'w') as f:
                json.dump(status, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save status: {e}")
    
    def _is_process_running(self, pid: int) -> bool:
        """Check if a process is running."""
        if pid is None:
            return False
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            return False
    
    def start(self, watcher_name: Optional[str] = None):
        """
        Start watcher(s).
        
        Args:
            watcher_name: Specific watcher to start, or None for all
        """
        # Set UTF-8 encoding for Windows console
        if sys.platform == 'win32':
            sys.stdout.reconfigure(encoding='utf-8')
        
        print(f"AI Employee Orchestrator - Starting watchers")
        print(f"Vault: {self.vault_path}\n")
        
        watchers_to_start = [watcher_name] if watcher_name else list(self.watchers.keys())
        
        for name in watchers_to_start:
            if name not in self.watchers:
                print(f"ERROR: Unknown watcher: {name}")
                continue
            
            watcher = self.watchers[name]
            
            # Check if already running
            if watcher['status'] == 'running' and self._is_process_running(watcher['pid']):
                print(f"[OK] {watcher['name']} already running (PID: {watcher['pid']})")
                continue
            
            # Start the watcher
            print(f"[*] Starting {watcher['name']}...")
            
            try:
                # Start as background process using Windows start command
                cmd = f'start /B "{watcher["name"]}" {sys.executable} -m {watcher["module"]} {self.vault_path}'
                
                # Log file for the watcher
                log_file = os.path.join(self.log_path, f"{name}_orchestrator.log")
                
                # Open log file for output
                log = open(log_file, 'w')
                
                # Use shell=True for start command
                process = subprocess.Popen(
                    cmd,
                    cwd=self.vault_path,
                    stdout=log,
                    stderr=log,
                    shell=True
                )
                
                # Give it a moment to start
                time.sleep(0.5)
                
                # Find the actual Python process
                import re
                try:
                    result = subprocess.run(
                        ['tasklist', '/FI', f'IMAGENAME eq python.exe', '/FO', 'CSV', '/NH'],
                        capture_output=True, text=True
                    )
                    # Get the most recent python process
                    pids = [int(m.group(1)) for m in re.finditer(r'"python.exe",(\d+)', result.stdout)]
                    if pids:
                        watcher['pid'] = pids[-1]  # Most recent
                except:
                    watcher['pid'] = process.pid
                
                watcher['status'] = 'running'
                watcher['started_at'] = datetime.now().isoformat()
                watcher['_log_handle'] = log
                
                print(f"[OK] {watcher['name']} started")
                print(f"     Log file: {log_file}")
                
            except Exception as e:
                print(f"ERROR: Failed to start {watcher['name']}: {e}")
                watcher['status'] = 'error'
        
        self._save_status()
        print(f"\n[OK] Orchestrator complete. Use 'status' to check running watchers.")
    
    def stop(self, watcher_name: Optional[str] = None):
        """
        Stop watcher(s).
        
        Args:
            watcher_name: Specific watcher to stop, or None for all
        """
        # Set UTF-8 encoding for Windows console
        if sys.platform == 'win32':
            sys.stdout.reconfigure(encoding='utf-8')
        
        print(f"AI Employee Orchestrator - Stopping watchers\n")
        
        watchers_to_stop = [watcher_name] if watcher_name else list(self.watchers.keys())
        
        for name in watchers_to_stop:
            if name not in self.watchers:
                print(f"ERROR: Unknown watcher: {name}")
                continue
            
            watcher = self.watchers[name]
            
            if watcher['status'] != 'running' or not self._is_process_running(watcher['pid']):
                print(f"[OK] {watcher['name']} not running")
                watcher['status'] = 'stopped'
                watcher['pid'] = None
                continue
            
            # Stop the watcher
            print(f"[*] Stopping {watcher['name']} (PID: {watcher['pid']})...")
            
            try:
                os.kill(watcher['pid'], signal.CTRL_C_EVENT)
                
                # Wait for process to terminate
                time.sleep(2)
                
                if self._is_process_running(watcher['pid']):
                    # Force kill if still running
                    os.kill(watcher['pid'], signal.SIGTERM)
                
                print(f"[OK] {watcher['name']} stopped")
                
            except Exception as e:
                print(f"WARNING: Error stopping {watcher['name']}: {e}")
            
            watcher['status'] = 'stopped'
            watcher['pid'] = None
        
        self._save_status()
        print(f"\n[OK] All watchers stopped.")
    
    def status(self):
        """Show status of all watchers."""
        # Set UTF-8 encoding for Windows console
        if sys.platform == 'win32':
            sys.stdout.reconfigure(encoding='utf-8')
        
        print(f"AI Employee Orchestrator - Status\n")
        print(f"Vault: {self.vault_path}")
        print(f"Last Check: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        print("-" * 60)
        print(f"{'Watcher':<25} {'Status':<12} {'PID':<10} {'Started At'}")
        print("-" * 60)
        
        for name, watcher in self.watchers.items():
            status_icon = "[RUN]" if watcher['status'] == 'running' else "[STOP]"
            pid_str = str(watcher['pid']) if watcher['pid'] else "-"
            started = watcher.get('started_at', '-')
            if started != '-':
                try:
                    started = datetime.fromisoformat(started).strftime('%H:%M:%S')
                except:
                    pass
            
            # Verify process is actually running
            if watcher['status'] == 'running' and not self._is_process_running(watcher['pid']):
                status_icon = "[ERR]"
                watcher['status'] = 'crashed'
            
            print(f"{status_icon} {watcher['name']:<22} {watcher['status']:<12} {pid_str:<10} {started}")
        
        print("-" * 60)
        
        # Count running
        running = sum(1 for w in self.watchers.values() if w['status'] == 'running')
        print(f"\n{running}/{len(self.watchers)} watchers running")
        
        self._save_status()


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("AI Employee Orchestrator")
        print("\nUsage:")
        print("  python -m watchers.orchestrator start [watcher]  - Start watchers")
        print("  python -m watchers.orchestrator stop [watcher]   - Stop watchers")
        print("  python -m watchers.orchestrator status           - Show status")
        print("\nWatchers: gmail, file")
        print("\nExamples:")
        print("  python -m watchers.orchestrator start          - Start all watchers")
        print("  python -m watchers.orchestrator start gmail    - Start only Gmail")
        print("  python -m watchers.orchestrator stop           - Stop all watchers")
        print("  python -m watchers.orchestrator status         - Check status")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    watcher_name = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Get vault path (current directory or parent)
    vault_path = os.getcwd()
    
    orchestrator = Orchestrator(vault_path)
    
    if command == 'start':
        orchestrator.start(watcher_name)
    elif command == 'stop':
        orchestrator.stop(watcher_name)
    elif command == 'status':
        orchestrator.status()
    else:
        print(f"Unknown command: {command}")
        print("Use 'start', 'stop', or 'status'")
        sys.exit(1)


if __name__ == "__main__":
    main()

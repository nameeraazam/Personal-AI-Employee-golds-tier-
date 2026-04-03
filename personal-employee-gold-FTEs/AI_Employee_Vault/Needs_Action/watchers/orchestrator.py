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

    def _stop_process(self, pid: int):
        """Stop a process by PID."""
        if self._is_process_running(pid):
            try:
                if sys.platform == 'win32':
                    os.system(f'taskkill /F /PID {pid}')
                else:
                    os.kill(pid, signal.SIGTERM)
                print(f"Stopped process {pid}")
            except Exception as e:
                print(f"Error stopping process {pid}: {e}")

    def start_watcher(self, watcher_key: str):
        """Start a specific watcher."""
        if watcher_key not in self.watchers:
            print(f"Error: Unknown watcher '{watcher_key}'")
            print(f"Available watchers: {', '.join(self.watchers.keys())}")
            return

        watcher = self.watchers[watcher_key]

        # Check if already running
        if watcher['status'] == 'running' and self._is_process_running(watcher['pid']):
            print(f"{watcher['name']} is already running (PID: {watcher['pid']})")
            return

        # Stop existing process if running
        if watcher['pid']:
            print(f"Stopping existing {watcher['name']} (PID: {watcher['pid']})...")
            self._stop_process(watcher['pid'])

        # Start new process
        print(f"Starting {watcher['name']}...")

        try:
            # Start as subprocess
            process = subprocess.Popen(
                [sys.executable, '-m', watcher['module'], self.vault_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == 'win32' else 0
            )

            watcher['pid'] = process.pid
            watcher['status'] = 'running'
            watcher['started_at'] = datetime.now().isoformat()
            watcher['process'] = process

            self._save_status()

            print(f"✓ {watcher['name']} started (PID: {process.pid})")

        except Exception as e:
            print(f"✗ Error starting {watcher['name']}: {e}")
            watcher['status'] = 'error'

    def stop_watcher(self, watcher_key: str):
        """Stop a specific watcher."""
        if watcher_key not in self.watchers:
            print(f"Error: Unknown watcher '{watcher_key}'")
            return

        watcher = self.watchers[watcher_key]

        if watcher['status'] != 'running' or not watcher['pid']:
            print(f"{watcher['name']} is not running")
            return

        print(f"Stopping {watcher['name']} (PID: {watcher['pid']})...")
        self._stop_process(watcher['pid'])

        watcher['status'] = 'stopped'
        watcher['pid'] = None
        watcher['started_at'] = None

        self._save_status()

        print(f"✓ {watcher['name']} stopped")

    def start_all(self):
        """Start all watchers."""
        print("\n" + "="*60)
        print("  AI EMPLOYEE ORCHESTRATOR - STARTING ALL WATCHERS")
        print("="*60 + "\n")

        for key in self.watchers:
            self.start_watcher(key)
            time.sleep(2)  # Stagger starts

        print("\n✓ All watchers started\n")

    def stop_all(self):
        """Stop all watchers."""
        print("\n" + "="*60)
        print("  AI EMPLOYEE ORCHESTRATOR - STOPPING ALL WATCHERS")
        print("="*60 + "\n")

        for key in self.watchers:
            self.stop_watcher(key)

        print("\n✓ All watchers stopped\n")

    def status(self):
        """Show status of all watchers."""
        print("\n" + "="*60)
        print("  AI EMPLOYEE ORCHESTRATOR - STATUS")
        print("="*60)
        print(f"\nVault Path: {self.vault_path}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        for key, watcher in self.watchers.items():
            is_running = watcher['status'] == 'running' and self._is_process_running(watcher['pid'])

            status_icon = "✓" if is_running else "✗"
            status_text = "RUNNING" if is_running else "STOPPED"

            print(f"{status_icon} {watcher['name']}: {status_text}")
            if watcher['pid']:
                print(f"   PID: {watcher['pid']}")
            if watcher.get('started_at'):
                started = datetime.fromisoformat(watcher['started_at'])
                print(f"   Started: {started.strftime('%Y-%m-%d %H:%M:%S')}")
            print()

        print("="*60 + "\n")


def main():
    """Main entry point for CLI."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python -m watchers.orchestrator start [watcher]")
        print("  python -m watchers.orchestrator stop [watcher]")
        print("  python -m watchers.orchestrator status")
        print("\nAvailable watchers: gmail, file")
        sys.exit(1)

    # Get vault path
    vault_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
    vault_path = os.path.abspath(vault_path)

    orchestrator = Orchestrator(vault_path)

    command = sys.argv[1].lower()

    if command == 'start':
        if len(sys.argv) > 2:
            # Start specific watcher
            orchestrator.start_watcher(sys.argv[2])
        else:
            # Start all watchers
            orchestrator.start_all()

    elif command == 'stop':
        if len(sys.argv) > 2:
            # Stop specific watcher
            orchestrator.stop_watcher(sys.argv[2])
        else:
            # Stop all watchers
            orchestrator.stop_all()

    elif command == 'status':
        orchestrator.status()

    else:
        print(f"Unknown command: {command}")
        print("Usage: python -m watchers.orchestrator {start|stop|status} [watcher]")
        sys.exit(1)


if __name__ == "__main__":
    main()

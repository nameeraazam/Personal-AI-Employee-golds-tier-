#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Base Watcher Class - Abstract base for all watcher implementations.

All watchers must inherit from this class and implement the required methods.
"""

import os
import time
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict, Any, Optional


class BaseWatcher(ABC):
    """
    Abstract base class for all watcher implementations.
    
    Watchers monitor external data sources (Gmail, file system, etc.)
    and create action files in the vault when new items are detected.
    """
    
    def __init__(self, vault_path: str, check_interval: int = 120):
        """
        Initialize the watcher.
        
        Args:
            vault_path: Path to the AI_Employee_Vault root directory
            check_interval: Seconds between checks (default: 120)
        """
        self.vault_path = os.path.abspath(vault_path)
        self.check_interval = check_interval
        self.running = False
        self.last_check: Optional[datetime] = None
        self.items_processed = 0
        self.errors: List[str] = []
        
        # Setup logging
        self.log_path = os.path.join(self.vault_path, "Logs")
        os.makedirs(self.log_path, exist_ok=True)
        
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)
        
        # File handler for watcher logs
        log_file = os.path.join(self.log_path, f"watcher-{datetime.now().strftime('%Y-%m-%d')}.log")
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        if not self.logger.handlers:
            self.logger.addHandler(file_handler)
        
        self.logger.info(f"Watcher initialized. Vault: {self.vault_path}, Interval: {check_interval}s")
    
    @abstractmethod
    def check_for_updates(self) -> List[Dict[str, Any]]:
        """
        Check for new items from the data source.
        
        Returns:
            List of new items, each item is a dictionary with:
            - id: Unique identifier
            - title: Item title/subject
            - content: Full content
            - source: Source identifier (email address, file path, etc.)
            - timestamp: When the item was created/received
            - priority: high, medium, or low
            - metadata: Additional metadata
        """
        pass
    
    @abstractmethod
    def create_action_file(self, item: Dict[str, Any]) -> str:
        """
        Create an action file in the Needs_Action folder.
        
        Args:
            item: Item dictionary from check_for_updates()
            
        Returns:
            Path to the created action file
        """
        pass
    
    def run(self):
        """
        Main loop - continuously monitor for new items.
        
        This method runs until stopped. It checks for updates at the
        configured interval and creates action files for new items.
        """
        self.running = True
        self.logger.info("Watcher started")
        
        try:
            while self.running:
                try:
                    # Check for new items
                    new_items = self.check_for_updates()
                    self.last_check = datetime.now()
                    
                    # Create action files for each new item
                    for item in new_items:
                        try:
                            file_path = self.create_action_file(item)
                            self.items_processed += 1
                            self.logger.info(f"Created action file: {file_path}")
                        except Exception as e:
                            error_msg = f"Error creating action file: {e}"
                            self.errors.append(error_msg)
                            self.logger.error(error_msg)
                    
                    # Wait for next check
                    if self.running:
                        time.sleep(self.check_interval)
                        
                except Exception as e:
                    error_msg = f"Error in check cycle: {e}"
                    self.errors.append(error_msg)
                    self.logger.error(error_msg)
                    
                    # Wait before retrying
                    if self.running:
                        time.sleep(30)
                        
        except KeyboardInterrupt:
            self.logger.info("Watcher interrupted by user")
        finally:
            self.running = False
            self.logger.info("Watcher stopped")
    
    def stop(self):
        """Stop the watcher gracefully."""
        self.logger.info("Stopping watcher...")
        self.running = False
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current watcher status.
        
        Returns:
            Dictionary with status information
        """
        return {
            "running": self.running,
            "last_check": self.last_check.isoformat() if self.last_check else None,
            "items_processed": self.items_processed,
            "errors": len(self.errors),
            "check_interval": self.check_interval
        }
    
    def _sanitize_filename(self, name: str) -> str:
        """
        Sanitize a string for use as a filename.
        
        Args:
            name: Original name
            
        Returns:
            Sanitized filename-safe string
        """
        # Remove or replace invalid characters
        invalid_chars = '<>:"/\\|？*'
        for char in invalid_chars:
            name = name.replace(char, '_')
        return name.strip()
    
    def _generate_frontmatter(self, item: Dict[str, Any]) -> str:
        """
        Generate YAML frontmatter for an action file.
        
        Args:
            item: Item dictionary
            
        Returns:
            YAML frontmatter string
        """
        timestamp = item.get('timestamp', datetime.now())
        if isinstance(timestamp, str):
            timestamp_str = timestamp
        else:
            timestamp_str = timestamp.strftime('%Y-%m-%d %H:%M:%S')
        
        tags = item.get('tags', [])
        tags_str = ', '.join(tags) if tags else ''
        
        return f"""---
created: {timestamp_str}
source: {item.get('source', 'unknown')}
priority: {item.get('priority', 'medium')}
status: pending
tags: [{tags_str}]
---
"""

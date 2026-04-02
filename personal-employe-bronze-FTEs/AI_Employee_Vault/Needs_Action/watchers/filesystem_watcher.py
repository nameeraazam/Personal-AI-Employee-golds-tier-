#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File System Watcher - Monitors a folder for new files.

Uses the watchdog library to detect new files dropped into a monitored folder.
Creates action files in the Needs_Action folder for new files.
"""

import os
import time
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional

from .base_watcher import BaseWatcher


class FileSystemWatcher(BaseWatcher):
    """
    Watcher that monitors a folder for new files.
    
    Uses watchdog library for efficient file system monitoring.
    """
    
    def __init__(
        self,
        vault_path: str,
        watch_path: Optional[str] = None,
        check_interval: int = 60,
        file_patterns: Optional[List[str]] = None,
        recursive: bool = False
    ):
        """
        Initialize the File System watcher.
        
        Args:
            vault_path: Path to the AI_Employee_Vault root directory
            watch_path: Path to folder to monitor (default: ./drop_folder)
            check_interval: Seconds between checks (default: 60)
            file_patterns: List of file patterns to watch (default: ['*.md', '*.txt'])
            recursive: Watch subdirectories too (default: False)
        """
        super().__init__(vault_path, check_interval)
        
        # Set watch path
        if watch_path:
            self.watch_path = os.path.abspath(watch_path)
        else:
            self.watch_path = os.path.join(self.vault_path, "drop_folder")
        
        # Create watch folder if it doesn't exist
        os.makedirs(self.watch_path, exist_ok=True)
        
        self.file_patterns = file_patterns or ['*.md', '*.txt', '*.pdf']
        self.recursive = recursive
        
        self._processed_files: set = set()
        self._file_hashes: Dict[str, str] = {}
        
        # Load previously processed files
        self._load_processed_files()
    
    def _load_processed_files(self):
        """Load list of previously processed files."""
        processed_file = os.path.join(self.log_path, "processed_files.txt")
        if os.path.exists(processed_file):
            try:
                with open(processed_file, 'r') as f:
                    for line in f:
                        if '|' in line:
                            filepath, filehash = line.strip().split('|', 1)
                            self._processed_files.add(filepath)
                            self._file_hashes[filepath] = filehash
                self.logger.info(f"Loaded {len(self._processed_files)} previously processed files")
            except Exception as e:
                self.logger.warning(f"Could not load processed files: {e}")
                self._processed_files = set()
    
    def _save_processed_file(self, filepath: str, filehash: str):
        """Save a processed file record."""
        self._processed_files.add(filepath)
        self._file_hashes[filepath] = filehash
        
        processed_file = os.path.join(self.log_path, "processed_files.txt")
        try:
            with open(processed_file, 'a') as f:
                f.write(f"{filepath}|{filehash}\n")
        except Exception as e:
            self.logger.warning(f"Could not save processed file: {e}")
    
    def _get_file_hash(self, filepath: str) -> str:
        """
        Calculate MD5 hash of a file.
        
        Args:
            filepath: Path to the file
            
        Returns:
            MD5 hash string
        """
        try:
            hasher = hashlib.md5()
            with open(filepath, 'rb') as f:
                # Read in chunks for large files
                for chunk in iter(lambda: f.read(4096), b''):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception as e:
            self.logger.error(f"Error hashing file {filepath}: {e}")
            return ""
    
    def _matches_pattern(self, filename: str) -> bool:
        """
        Check if filename matches any of the watched patterns.
        
        Args:
            filename: Name of the file to check
            
        Returns:
            True if file matches a pattern
        """
        import fnmatch
        
        for pattern in self.file_patterns:
            if fnmatch.fnmatch(filename, pattern):
                return True
        return False
    
    def _classify_priority(self, filename: str, content: str = "") -> str:
        """
        Classify file priority based on filename and content.
        
        Args:
            filename: Name of the file
            content: File content (optional)
            
        Returns:
            Priority level: 'high', 'medium', or 'low'
        """
        text = f"{filename} {content}".lower()
        
        # High priority keywords
        high_keywords = ['urgent', 'asap', 'deadline', 'emergency', 'critical', 
                        'immediate', 'action required', 'important']
        
        # Medium priority keywords
        medium_keywords = ['review', 'feedback', 'meeting', 'schedule', 
                          'call', 'discuss', 'update', 'reminder']
        
        for keyword in high_keywords:
            if keyword in text:
                return 'high'
        
        for keyword in medium_keywords:
            if keyword in text:
                return 'medium'
        
        return 'low'
    
    def _get_file_content(self, filepath: str) -> str:
        """
        Read file content (text files only).
        
        Args:
            filepath: Path to the file
            
        Returns:
            File content as string
        """
        try:
            # Check if it's a text file
            text_extensions = ['.md', '.txt', '.csv', '.json', '.xml', '.html']
            ext = os.path.splitext(filepath)[1].lower()
            
            if ext in text_extensions:
                with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                    return f.read(2000)  # Read first 2000 chars
            else:
                return f"[Binary file: {ext}]"
        except Exception as e:
            self.logger.warning(f"Error reading file {filepath}: {e}")
            return f"[Error reading file: {e}]"
    
    def check_for_updates(self) -> List[Dict[str, Any]]:
        """
        Check the watched folder for new files.
        
        Returns:
            List of new file items
        """
        new_items = []
        
        try:
            if not os.path.exists(self.watch_path):
                self.logger.warning(f"Watch folder does not exist: {self.watch_path}")
                return []
            
            # Scan the watch folder
            for filename in os.listdir(self.watch_path):
                filepath = os.path.join(self.watch_path, filename)
                
                # Skip directories
                if os.path.isdir(filepath):
                    continue
                
                # Check if file matches patterns
                if not self._matches_pattern(filename):
                    continue
                
                # Skip already processed files
                if filepath in self._processed_files:
                    continue
                
                # Calculate file hash to detect changes
                file_hash = self._get_file_hash(filepath)
                if not file_hash:
                    continue
                
                # Get file info
                stat = os.stat(filepath)
                
                # Read content for priority classification
                content = self._get_file_content(filepath)
                
                # Classify priority
                priority = self._classify_priority(filename, content)
                
                # Create item
                item = {
                    'id': file_hash,
                    'title': os.path.splitext(filename)[0],
                    'content': content,
                    'source': f"FileSystem: {filepath}",
                    'timestamp': datetime.fromtimestamp(stat.st_mtime),
                    'priority': priority,
                    'metadata': {
                        'filepath': filepath,
                        'filename': filename,
                        'size': stat.st_size,
                        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                        'file_hash': file_hash
                    },
                    'tags': ['file', 'filesystem']
                }
                
                new_items.append(item)
                self._save_processed_file(filepath, file_hash)
                self.logger.info(f"Found new file: {filename}")
            
            if new_items:
                self.logger.info(f"Found {len(new_items)} new files")
            else:
                self.logger.debug("No new files found")
                
        except Exception as e:
            self.logger.error(f"Error checking file system: {e}")
            self.errors.append(f"File system check failed: {e}")
        
        return new_items
    
    def create_action_file(self, item: Dict[str, Any]) -> str:
        """
        Create an action file in Needs_Action folder for the new file.
        
        Args:
            item: File item dictionary
            
        Returns:
            Path to the created action file
        """
        needs_action_path = os.path.join(self.vault_path, "Needs_Action")
        os.makedirs(needs_action_path, exist_ok=True)
        
        # Generate filename
        timestamp = item['timestamp']
        safe_title = self._sanitize_filename(item['title'][:50])
        filename = f"{timestamp.strftime('%Y-%m-%d')}_file_{safe_title}.md"
        file_path = os.path.join(needs_action_path, filename)
        
        # Generate frontmatter
        frontmatter = self._generate_frontmatter(item)
        
        # Generate content
        metadata = item.get('metadata', {})
        content = f"""{frontmatter}
# 📄 {item['title']}

## Summary
New file detected in the drop folder.

## File Details

| Field | Value |
|-------|-------|
| **Filename** | {metadata.get('filename', 'unknown')} |
| **Path** | {metadata.get('filepath', 'unknown')} |
| **Size** | {metadata.get('size', 0)} bytes |
| **Modified** | {metadata.get('modified', 'unknown')} |
| **Priority** | {item['priority']} |
| **Source** | File System |

## Content Preview

```
{item['content'][:1500] if item['content'] else '(No content available)'}
```

---

## Action Required

- [ ] Review file content
- [ ] Determine required action
- [ ] Process or archive the original file
- [ ] Move to Done when complete

## Metadata

- **File Hash**: {metadata.get('file_hash', 'N/A')}
- **Processed**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        # Write file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return file_path


def main():
    """Run the File System watcher standalone."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python -m watchers.filesystem_watcher . [watch_path]")
        print("  vault_path: Path to AI_Employee_Vault")
        print("  watch_path: Optional path to watch folder (default: ./drop_folder)")
        sys.exit(1)
    
    vault_path = sys.argv[1]
    watch_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    watcher = FileSystemWatcher(
        vault_path=vault_path,
        watch_path=watch_path,
        check_interval=60
    )
    
    print(f"File System Watcher starting.")
    print(f"Vault: {vault_path}")
    print(f"Watching: {watcher.watch_path}")
    print("Press Ctrl+C to stop")
    
    try:
        watcher.run()
    except KeyboardInterrupt:
        print("\nStopping watcher...")
        watcher.stop()


if __name__ == "__main__":
    main()

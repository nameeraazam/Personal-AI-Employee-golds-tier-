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
        super().__init__(vault_path, check_interval)

        if watch_path:
            self.watch_path = os.path.abspath(watch_path)
        else:
            self.watch_path = os.path.join(self.vault_path, "drop_folder")

        os.makedirs(self.watch_path, exist_ok=True)

        self.file_patterns = file_patterns or ['*.md', '*.txt', '*.pdf']
        self.recursive = recursive

        self._processed_files: set = set()
        self._file_hashes: Dict[str, str] = {}

        self._load_processed_files()

    def _load_processed_files(self):
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
        self._processed_files.add(filepath)
        self._file_hashes[filepath] = filehash

        processed_file = os.path.join(self.log_path, "processed_files.txt")
        try:
            with open(processed_file, 'a') as f:
                f.write(f"{filepath}|{filehash}\n")
        except Exception as e:
            self.logger.warning(f"Could not save processed file: {e}")

    def _get_file_hash(self, filepath: str) -> str:
        try:
            hasher = hashlib.md5()
            with open(filepath, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception as e:
            self.logger.error(f"Error hashing file {filepath}: {e}")
            return ""

    def _matches_pattern(self, filename: str) -> bool:
        import fnmatch

        for pattern in self.file_patterns:
            if fnmatch.fnmatch(filename, pattern):
                return True
        return False

    def _classify_priority(self, filename: str, content: str = "") -> str:
        text = f"{filename} {content}".lower()

        high_keywords = ['urgent', 'asap', 'deadline', 'emergency', 'critical',
                        'immediate', 'action required', 'important']

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
        try:
            text_extensions = ['.md', '.txt', '.csv', '.json', '.xml', '.html']
            ext = os.path.splitext(filepath)[1].lower()

            if ext in text_extensions:
                with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                    return f.read(2000)
            else:
                return f"[Binary file: {ext}]"
        except Exception as e:
            self.logger.warning(f"Error reading file {filepath}: {e}")
            return f"[Error reading file: {e}]"

    def check_for_updates(self) -> List[Dict[str, Any]]:
        new_items = []

        try:
            if not os.path.exists(self.watch_path):
                self.logger.warning(f"Watch folder does not exist: {self.watch_path}")
                return []

            for filename in os.listdir(self.watch_path):
                filepath = os.path.join(self.watch_path, filename)

                if os.path.isdir(filepath):
                    continue

                if not self._matches_pattern(filename):
                    continue

                if filepath in self._processed_files:
                    continue

                file_hash = self._get_file_hash(filepath)
                if not file_hash:
                    continue

                stat = os.stat(filepath)
                content = self._get_file_content(filepath)
                priority = self._classify_priority(filename, content)

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
        needs_action_path = os.path.join(self.vault_path, "Needs_Action")
        os.makedirs(needs_action_path, exist_ok=True)

        timestamp = item['timestamp']
        safe_title = self._sanitize_filename(item['title'][:50])
        filename = f"{timestamp.strftime('%Y-%m-%d')}_file_{safe_title}.md"
        file_path = os.path.join(needs_action_path, filename)

        frontmatter = self._generate_frontmatter(item)

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

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return file_path


def main():
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m watchers.filesystem_watcher . [watch_path]")
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

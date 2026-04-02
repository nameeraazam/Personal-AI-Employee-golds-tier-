#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WhatsApp Watcher - Monitors WhatsApp Web for new messages with important keywords.

Uses Playwright for browser automation with persistent session.
Creates action files in the Needs_Action folder for matching messages.
"""

import os
import sys
import time
import logging
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path


class BaseWatcher:
    """
    Abstract base class for all watcher implementations.

    All watchers must inherit from this class and implement the required methods.
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
        raise NotImplementedError("Subclasses must implement check_for_updates()")

    def create_action_file(self, item: Dict[str, Any]) -> str:
        """
        Create an action file in the Needs_Action folder.

        Args:
            item: Item dictionary from check_for_updates()

        Returns:
            Path to the created action file
        """
        raise NotImplementedError("Subclasses must implement create_action_file()")

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


class WhatsAppWatcher(BaseWatcher):
    """
    Watcher that monitors WhatsApp Web for new messages with important keywords.

    Uses Playwright for browser automation with persistent session.
    """

    def __init__(
        self,
        vault_path: str,
        session_path: Optional[str] = None,
        check_interval: int = 30,
        keywords: Optional[List[str]] = None,
        headless: bool = False
    ):
        """
        Initialize the WhatsApp watcher.

        Args:
            vault_path: Path to the AI_Employee_Vault root directory
            session_path: Path to store persistent browser session
            check_interval: Seconds between checks (default: 30)
            keywords: List of keywords to monitor (default: ['urgent', 'asap', 'invoice', 'payment'])
            headless: Run browser in headless mode (default: False for QR scan)
        """
        super().__init__(vault_path, check_interval)

        # Session path in user's home directory or relative to vault
        if session_path:
            self.session_path = os.path.expanduser(session_path)
        else:
            self.session_path = os.path.join(
                os.path.dirname(os.path.dirname(self.vault_path)), "whatsapp_session"
            )
        
        self.keywords = keywords or ['urgent', 'asap', 'invoice', 'payment']
        self.headless = headless

        self._browser = None
        self._context = None
        self._page = None
        self._processed_messages: set = set()

        # Load previously processed message IDs
        self._load_processed_messages()

    def _load_processed_messages(self):
        """Load IDs of already processed messages from file."""
        processed_file = os.path.join(self.log_path, "processed_whatsapp_messages.txt")
        if os.path.exists(processed_file):
            try:
                with open(processed_file, 'r') as f:
                    self._processed_messages = set(line.strip() for line in f if line.strip())
                self.logger.info(f"Loaded {len(self._processed_messages)} previously processed message IDs")
            except Exception as e:
                self.logger.warning(f"Could not load processed messages: {e}")
                self._processed_messages = set()

    def _save_processed_message(self, msg_id: str):
        """Save a processed message ID to file."""
        self._processed_messages.add(msg_id)
        processed_file = os.path.join(self.log_path, "processed_whatsapp_messages.txt")
        try:
            with open(processed_file, 'a') as f:
                f.write(msg_id + '\n')
        except Exception as e:
            self.logger.warning(f"Could not save processed message ID: {e}")

    async def _initialize_browser(self):
        """
        Initialize Playwright browser with persistent context.

        Returns:
            Page object for WhatsApp Web
        """
        try:
            from playwright.async_api import async_playwright

            playwright = await async_playwright().start()
            
            # Create session directory
            os.makedirs(self.session_path, exist_ok=True)
            self.logger.info(f"Session path: {self.session_path}")

            # Launch browser with persistent context
            self._browser = await playwright.chromium.launch(
                headless=self.headless,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-accelerated-2d-canvas',
                    '--disable-gpu'
                ]
            )

            # Create persistent context
            self._context = await self._browser.new_context(
                viewport={'width': 1280, 'height': 720},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )

            self._page = await self._context.new_page()
            
            # Navigate to WhatsApp Web
            self.logger.info("Navigating to WhatsApp Web...")
            await self._page.goto('https://web.whatsapp.com', wait_until='networkidle')
            
            # Check if QR code scan is needed
            await self._handle_qr_code()
            
            self.logger.info("WhatsApp Web initialized successfully")
            return self._page

        except ImportError as e:
            self.logger.error(f"Playwright not installed. Run: pip install playwright && playwright install")
            raise
        except Exception as e:
            self.logger.error(f"Browser initialization failed: {e}")
            raise

    async def _handle_qr_code(self):
        """
        Handle QR code authentication for first-time login.
        """
        try:
            # Wait for page to load
            await self._page.wait_for_load_state('domcontentloaded')
            await asyncio.sleep(3)

            # Check if QR code is present (first-time login)
            qr_selector = 'div[data-ref="data-ref"]'
            
            try:
                qr_element = await self._page.wait_for_selector(qr_selector, timeout=10000)
                if qr_element:
                    print("\n" + "="*70)
                    print("WHATSAPP AUTHENTICATION REQUIRED")
                    print("="*70)
                    print("\nQR Code detected. Please follow these steps:")
                    print("\n1. Open WhatsApp on your phone")
                    print("2. Go to Settings > Linked Devices")
                    print("3. Tap 'Link a Device'")
                    print("4. Scan the QR code displayed in the browser window")
                    print("\nWaiting for QR code scan...")
                    print("(The browser window will show WhatsApp after successful scan)")
                    
                    # Wait for QR code to be scanned (max 60 seconds)
                    await self._page.wait_for_selector('div[data-ref="data-ref"]', state='detached', timeout=60000)
                    
                    print("\n✓ QR code scanned successfully!")
                    self.logger.info("QR code authentication completed")
                    
                    # Wait for chat list to load
                    await asyncio.sleep(5)
                    
            except asyncio.TimeoutError:
                # QR code not found or already logged in
                self.logger.info("No QR code detected - may already be logged in")
                
            # Verify we're logged in by checking for chat list
            try:
                await self._page.wait_for_selector('div[role="navigation"]', timeout=15000)
                self.logger.info("Successfully logged into WhatsApp Web")
            except asyncio.TimeoutError:
                self.logger.warning("Chat list not found - authentication may have failed")
                
        except Exception as e:
            self.logger.error(f"QR code handling failed: {e}")
            raise

    def _classify_priority(self, text: str) -> str:
        """
        Classify message priority based on keywords.

        Args:
            text: Message text

        Returns:
            Priority level: 'high', 'medium', or 'low'
        """
        text_lower = text.lower()

        # High priority keywords
        high_keywords = ['urgent', 'asap', 'emergency', 'critical', 'immediate']

        # Medium priority keywords  
        medium_keywords = ['invoice', 'payment', 'deadline', 'reminder']

        for keyword in high_keywords:
            if keyword in text_lower:
                return 'high'

        for keyword in medium_keywords:
            if keyword in text_lower:
                return 'medium'

        return 'low'

    async def _get_unread_chats(self) -> List[Dict[str, Any]]:
        """
        Get unread chats from WhatsApp Web.

        Returns:
            List of unread chat information
        """
        unread_chats = []

        try:
            # Wait for chat list to be available
            await self._page.wait_for_selector('div[role="navigation"] div[tabindex="0"] > div > div', timeout=10000)
            await asyncio.sleep(2)

            # Get all chat elements
            chat_elements = await self._page.query_selector_all(
                'div[role="navigation"] div[tabindex="0"] > div > div'
            )

            for chat_elem in chat_elements:
                try:
                    # Get chat name
                    name_elem = await chat_elem.query_selector('span[title]')
                    if not name_elem:
                        continue
                    
                    chat_name = await name_elem.get_attribute('title')
                    if not chat_name:
                        continue

                    # Check for unread indicator
                    unread_badge = await chat_elem.query_selector('span[aria-label*="unread"]')
                    if not unread_badge:
                        # Also check for common unread indicators
                        unread_check = await chat_elem.query_selector('span[aria-label]')
                        is_unread = False
                        if unread_check:
                            label = await unread_check.get_attribute('aria-label')
                            is_unread = label and 'unread' in label.lower()
                        
                        if not is_unread:
                            continue

                    # Get last message
                    message_elem = await chat_elem.query_selector('span[title*=":"], span[dir="auto"]')
                    last_message = ""
                    if message_elem:
                        last_message = await message_elem.text_content()
                        last_message = last_message.strip() if last_message else ""

                    # Get timestamp if available
                    time_elem = await chat_elem.query_selector('span[title]')
                    timestamp_str = ""
                    if time_elem:
                        timestamp_str = await time_elem.get_attribute('title')

                    # Check if message contains keywords
                    message_lower = last_message.lower()
                    matched_keywords = [kw for kw in self.keywords if kw.lower() in message_lower]

                    if matched_keywords:
                        # Generate unique ID
                        msg_id = f"{chat_name}_{timestamp_str}_{last_message[:20]}"
                        msg_id = msg_id.replace(' ', '_').replace('/', '_')

                        unread_chats.append({
                            'id': msg_id,
                            'chat_name': chat_name,
                            'last_message': last_message,
                            'timestamp': timestamp_str,
                            'matched_keywords': matched_keywords,
                            'priority': self._classify_priority(last_message)
                        })

                        self.logger.info(f"Found matching message from {chat_name}: {last_message[:50]}")

                except Exception as e:
                    self.logger.debug(f"Error processing chat element: {e}")
                    continue

            if unread_chats:
                self.logger.info(f"Found {len(unread_chats)} unread chats with keywords")
            else:
                self.logger.debug("No unread chats with keywords found")

        except Exception as e:
            self.logger.error(f"Error getting unread chats: {e}")
            self.errors.append(f"WhatsApp chat check failed: {e}")

        return unread_chats

    def check_for_updates(self) -> List[Dict[str, Any]]:
        """
        Check WhatsApp Web for new messages with important keywords.

        Returns:
            List of new message items
        """
        new_items = []

        try:
            # Run async code in sync context
            import asyncio
            
            async def get_messages():
                # Initialize browser if needed
                if self._page is None:
                    await self._initialize_browser()
                
                # Get unread chats
                unread_chats = await self._get_unread_chats()
                return unread_chats

            # Run the async function
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                unread_chats = loop.run_until_complete(get_messages())
            finally:
                loop.close()

            # Process unread chats
            for chat in unread_chats:
                msg_id = chat['id']

                # Skip already processed
                if msg_id in self._processed_messages:
                    continue

                # Create item
                item = {
                    'id': msg_id,
                    'title': f"WhatsApp: {chat['chat_name']}",
                    'content': chat['last_message'],
                    'source': f"WhatsApp: {chat['chat_name']}",
                    'timestamp': datetime.now(),
                    'priority': chat['priority'],
                    'metadata': {
                        'chat_name': chat['chat_name'],
                        'whatsapp_id': msg_id,
                        'matched_keywords': chat['matched_keywords'],
                        'original_timestamp': chat['timestamp']
                    },
                    'tags': ['whatsapp', 'message']
                }

                new_items.append(item)
                self._save_processed_message(msg_id)
                self.logger.info(f"Found new message: {item['title']}")

            if new_items:
                self.logger.info(f"Found {len(new_items)} new messages")
            else:
                self.logger.debug("No new messages found")

        except Exception as e:
            self.logger.error(f"Error checking WhatsApp: {e}")
            self.errors.append(f"WhatsApp check failed: {e}")

        return new_items

    def create_action_file(self, item: Dict[str, Any]) -> str:
        """
        Create an action file in Needs_Action folder for the message.

        Args:
            item: Message item dictionary

        Returns:
            Path to the created action file
        """
        needs_action_path = os.path.join(self.vault_path, "Needs_Action")
        os.makedirs(needs_action_path, exist_ok=True)

        # Generate filename
        timestamp = item['timestamp']
        safe_title = self._sanitize_filename(item['title'][:50])
        filename = f"{timestamp.strftime('%Y-%m-%d')}_whatsapp_{safe_title}.md"
        file_path = os.path.join(needs_action_path, filename)

        # Generate frontmatter
        frontmatter = self._generate_frontmatter(item)

        # Generate content
        metadata = item.get('metadata', {})
        matched_keywords = metadata.get('matched_keywords', [])
        
        content = f"""{frontmatter}
# 💬 {item['title']}

## Summary
New WhatsApp message received from {metadata.get('chat_name', 'unknown')}

## Message Details

| Field | Value |
|-------|-------|
| **From** | {metadata.get('chat_name', 'unknown')} |
| **Priority** | {item['priority']} |
| **Source** | WhatsApp Web |
| **Matched Keywords** | {', '.join(matched_keywords)} |

## Message Content

{item['content'] if item['content'] else '(No content)'}

---

## Action Required

- [ ] Review message content
- [ ] Determine required response
- [ ] Reply via WhatsApp if needed
- [ ] Take appropriate action
- [ ] Move to Done when complete

## Metadata

- **WhatsApp ID**: {metadata.get('whatsapp_id', 'N/A')}
- **Original Timestamp**: {metadata.get('original_timestamp', 'N/A')}
- **Processed**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

        # Write file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return file_path

    def stop(self):
        """Stop the watcher and close browser."""
        self.logger.info("Stopping watcher and closing browser...")
        self.running = False
        
        # Close browser
        if self._browser:
            try:
                # Run async close in sync context
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    loop.run_until_complete(self._browser.close())
                finally:
                    loop.close()
                self.logger.info("Browser closed successfully")
            except Exception as e:
                self.logger.warning(f"Error closing browser: {e}")


def main():
    """Run the WhatsApp watcher standalone."""
    # Set UTF-8 encoding for Windows console
    if sys.platform == 'win32':
        sys.stdout.reconfigure(encoding='utf-8')

    # Get vault path from argument or use default
    if len(sys.argv) >= 2:
        vault_path = sys.argv[1]
    else:
        # Default to AI_Employee_Vault in same directory as script
        vault_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "AI_Employee_Vault")

    # Parse optional arguments
    headless = '--headless' in sys.argv
    keywords = ['urgent', 'asap', 'invoice', 'payment']
    
    print(f"WhatsApp Watcher starting. Vault: {vault_path}")
    print(f"Check interval: 30 seconds")
    print(f"Monitoring keywords: {', '.join(keywords)}")
    if headless:
        print("Running in headless mode")
    else:
        print("Browser window will open for QR code scan (first run only)")
    print("Press Ctrl+C to stop")

    watcher = WhatsAppWatcher(
        vault_path=vault_path,
        session_path="~/whatsapp_session",
        check_interval=30,
        keywords=keywords,
        headless=headless
    )

    try:
        watcher.run()
    except KeyboardInterrupt:
        print("\nStopping watcher...")
        watcher.stop()


if __name__ == "__main__":
    main()

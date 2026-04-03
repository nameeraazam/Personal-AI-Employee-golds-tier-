#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn Watcher - Silver Tier
Monitors LinkedIn for new messages, notifications, and sales leads.
Uses Playwright for browser automation with session persistence.

Features:
- Check every 60 seconds for new activity
- Detect new messages, connection requests, notifications
- Focus on sales leads (keywords: interested, demo, pricing, buy, purchase)
- Create markdown files in Needs_Action/ folder
- Log all activity to console
- Session persistence for auto-login
"""

import os
import sys
import json
import time
import hashlib
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Try to import playwright
try:
    from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext
    from playwright._impl._errors import TargetClosedError, TimeoutError as PlaywrightTimeout
except ImportError:
    print("❌ Playwright not installed!")
    print("   Run: pip install playwright")
    print("   Then: playwright install")
    sys.exit(1)


# ============================================================================
# CONFIGURATION
# ============================================================================

class Config:
    """LinkedIn Watcher Configuration"""

    SCRIPT_DIR = Path(__file__).parent
    PROJECT_ROOT = SCRIPT_DIR.parent
    SESSION_PATH = os.getenv(
        'LINKEDIN_SESSION_PATH',
        str(PROJECT_ROOT / 'linkedin_session.json')
    )
    NEEDS_ACTION_PATH = PROJECT_ROOT / 'Needs_Action'
    LOG_PATH = PROJECT_ROOT / 'linkedin_watcher.log'

    LINKEDIN_EMAIL = os.getenv('LINKEDIN_EMAIL', '')
    LINKEDIN_PASSWORD = os.getenv('LINKEDIN_PASSWORD', '')

    CHECK_INTERVAL = int(os.getenv('LINKEDIN_CHECK_INTERVAL', '60'))
    HEADLESS = os.getenv('LINKEDIN_HEADLESS', 'false').lower() == 'true'

    LINKEDIN_URL = 'https://www.linkedin.com'
    LINKEDIN_LOGIN_URL = 'https://www.linkedin.com/login'
    LINKEDIN_MESSAGING_URL = 'https://www.linkedin.com/messaging'
    LINKEDIN_NOTIFICATIONS_URL = 'https://www.linkedin.com/notifications'
    LINKEDIN_FEED_URL = 'https://www.linkedin.com/feed'

    SALES_KEYWORDS = [
        'interested', 'interest', 'demo', 'pricing', 'price', 'buy',
        'purchase', 'quote', 'proposal', 'contract', 'deal', 'opportunity',
        'budget', 'decision', 'timeline', 'requirements', 'rfp', 'rfi',
        'vendor', 'solution', 'partnership', 'collaboration', 'meeting',
        'call', 'discuss', 'explore', 'services', 'product', 'enterprise'
    ]

    MONITOR_MESSAGES = os.getenv('LINKEDIN_MONITOR_MESSAGES', 'true').lower() == 'true'
    MONITOR_CONNECTIONS = os.getenv('LINKEDIN_MONITOR_CONNECTIONS', 'true').lower() == 'true'
    MONITOR_NOTIFICATIONS = os.getenv('LINKEDIN_MONITOR_NOTIFICATIONS', 'true').lower() == 'true'
    MONITOR_FEED = os.getenv('LINKEDIN_MONITOR_FEED', 'false').lower() == 'true'


class Logger:
    """Simple file and console logger"""

    def __init__(self, log_path: Path):
        self.log_path = log_path
        self._ensure_log_file()

    def _ensure_log_file(self):
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.log_path.exists():
            self.log_path.touch()

    def _timestamp(self) -> str:
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def log(self, message: str, level: str = 'INFO'):
        timestamp = self._timestamp()
        log_line = f"[{timestamp}] [{level}] {message}"

        if level == 'ERROR':
            print(f"\033[91m{log_line}\033[0m")
        elif level == 'WARNING':
            print(f"\033[93m{log_line}\033[0m")
        elif level == 'SUCCESS':
            print(f"\033[92m{log_line}\033[0m")
        elif level == 'SALES':
            print(f"\033[94m{log_line}\033[0m")
        else:
            print(log_line)

        with open(self.log_path, 'a', encoding='utf-8') as f:
            f.write(log_line + '\n')

    def info(self, message: str):
        self.log(message, 'INFO')

    def warning(self, message: str):
        self.log(message, 'WARNING')

    def error(self, message: str):
        self.log(message, 'ERROR')

    def success(self, message: str):
        self.log(message, 'SUCCESS')

    def sales(self, message: str):
        self.log(message, 'SALES')


class LinkedInWatcher:
    """Main LinkedIn monitoring class using Playwright"""

    def __init__(self):
        self.config = Config()
        self.logger = Logger(self.config.LOG_PATH)
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.seen_items: set = set()
        self.stats = {
            'messages': 0,
            'connections': 0,
            'notifications': 0,
            'sales_leads': 0,
            'errors': 0
        }

        self.config.NEEDS_ACTION_PATH.mkdir(parents=True, exist_ok=True)

    def _generate_item_id(self, content: str, sender: str) -> str:
        unique_str = f"{sender}:{content}:{datetime.now().strftime('%Y%m%d')}"
        return hashlib.md5(unique_str.encode()).hexdigest()[:12]

    def _is_sales_lead(self, content: str) -> bool:
        content_lower = content.lower()
        for keyword in self.config.SALES_KEYWORDS:
            if keyword in content_lower:
                return True
        return False

    def _create_action_item(self, item_type: str, sender: str, content: str,
                           extra_data: Optional[Dict] = None) -> str:

        item_id = self._generate_item_id(content, sender)
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

        priority = 'high' if self._is_sales_lead(content) else 'normal'

        frontmatter = f"""---
type: {item_type}
from: {sender}
content: {content[:100]}{'...' if len(content) > 100 else ''}
status: pending
priority: {priority}
created: {datetime.now().isoformat()}
item_id: {item_id}
"""

        if extra_data:
            for key, value in extra_data.items():
                frontmatter += f"{key}: {value}\n"

        frontmatter += "---\n\n"

        full_content = f"""{frontmatter}
# LinkedIn {item_type.title()} - {sender}

**Received:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Priority:** {priority}
**Status:** pending

---

## Content

{content}

---

## Action Required

- [ ] Review and respond
- [ ] Update status when complete

---
*Generated by LinkedIn Watcher - Silver Tier*
"""

        safe_sender = re.sub(r'[^\w\s-]', '', sender)[:30]
        filename = f"LINKEDIN_{item_type.upper()}_{safe_sender}_{timestamp}.md"
        filepath = self.config.NEEDS_ACTION_PATH / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(full_content)

        return str(filepath)

    def _save_session(self):
        try:
            cookies = self.context.cookies()
            session_data = {
                'cookies': cookies,
                'timestamp': datetime.now().isoformat(),
                'email': self.config.LINKEDIN_EMAIL
            }

            with open(self.config.SESSION_PATH, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2)

            self.logger.info(f"Session saved to: {self.config.SESSION_PATH}")
        except Exception as e:
            self.logger.error(f"Failed to save session: {e}")

    def _load_session(self) -> bool:
        try:
            if not os.path.exists(self.config.SESSION_PATH):
                self.logger.info("No saved session found")
                return False

            with open(self.config.SESSION_PATH, 'r', encoding='utf-8') as f:
                session_data = json.load(f)

            saved_time = datetime.fromisoformat(session_data['timestamp'])
            age_hours = (datetime.now() - saved_time).total_seconds() / 3600

            if age_hours > 24:
                self.logger.warning(f"Session is {age_hours:.1f} hours old, may be expired")

            self.context.add_cookies(session_data['cookies'])
            self.logger.success("Session loaded successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to load session: {e}")
            return False

    def _is_logged_in(self) -> bool:
        try:
            self.page.wait_for_selector('div.global-nav', timeout=5000)
            current_url = self.page.url
            if 'login' in current_url or 'checkpoint' in current_url:
                return False
            return True
        except:
            return False

    async def _login(self):
        self.logger.info("Logging in to LinkedIn...")

        try:
            await self.page.goto(self.config.LINKEDIN_LOGIN_URL, wait_until='networkidle')
            await self.page.wait_for_timeout(3000)

            email_input = await self.page.wait_for_selector('input[id="username"]', timeout=10000)
            await email_input.fill(self.config.LINKEDIN_EMAIL)

            password_input = await self.page.wait_for_selector('input[id="password"]', timeout=5000)
            await password_input.fill(self.config.LINKEDIN_PASSWORD)

            sign_in_button = await self.page.wait_for_selector('button[type="submit"]', timeout=5000)
            await sign_in_button.click()

            await self.page.wait_for_load_state('networkidle')
            await self.page.wait_for_timeout(5000)

            if await self._is_logged_in():
                self.logger.success("Login successful!")
                self._save_session()
                return True
            else:
                self.logger.error("Login may have failed - checking...")
                try:
                    error = await self.page.query_selector('.alert')
                    if error:
                        error_text = await error.text_content()
                        self.logger.error(f"Login error: {error_text}")
                except:
                    pass
                return False

        except Exception as e:
            self.logger.error(f"Login failed: {e}")
            self.stats['errors'] += 1
            return False

    def _check_messages(self) -> List[Dict]:
        new_messages = []

        try:
            self.logger.info("Checking messages...")
            self.page.goto(self.config.LINKEDIN_MESSAGING_URL, wait_until='networkidle')
            self.page.wait_for_timeout(3000)

            conversations = self.page.query_selector_all('div.conversation')

            for conv in conversations[:10]:
                try:
                    sender_elem = conv.query_selector('span.visually-hidden')
                    sender = sender_elem.text_content().strip() if sender_elem else 'Unknown'

                    message_elem = conv.query_selector('p.message-body')
                    message = message_elem.text_content().strip() if message_elem else ''

                    if sender and message:
                        item_id = self._generate_item_id(message, sender)

                        if item_id not in self.seen_items:
                            self.seen_items.add(item_id)
                            new_messages.append({
                                'sender': sender,
                                'content': message,
                                'is_sales': self._is_sales_lead(message)
                            })
                except:
                    continue

            if new_messages:
                self.logger.success(f"Found {len(new_messages)} new message(s)")
            else:
                self.logger.info("No new messages")

        except Exception as e:
            self.logger.error(f"Error checking messages: {e}")
            self.stats['errors'] += 1

        return new_messages

    def _check_notifications(self) -> List[Dict]:
        new_notifications = []

        try:
            self.logger.info("Checking notifications...")
            self.page.goto(self.config.LINKEDIN_NOTIFICATIONS_URL, wait_until='networkidle')
            self.page.wait_for_timeout(3000)

            notifications = self.page.query_selector_all('li.notification-item')

            for notif in notifications[:15]:
                try:
                    content_elem = notif.query_selector('span.notification-content')
                    content = content_elem.text_content().strip() if content_elem else ''

                    if content:
                        item_id = hashlib.md5(content.encode()).hexdigest()[:12]

                        if item_id not in self.seen_items:
                            self.seen_items.add(item_id)

                            notif_type = 'general'
                            if 'connection' in content.lower():
                                notif_type = 'connection'
                            elif 'message' in content.lower():
                                notif_type = 'message'
                            elif any(k in content.lower() for k in ['job', 'hiring']):
                                notif_type = 'job'

                            new_notifications.append({
                                'content': content,
                                'type': notif_type,
                                'is_sales': self._is_sales_lead(content)
                            })
                except:
                    continue

            if new_notifications:
                self.logger.success(f"Found {len(new_notifications)} new notification(s)")
            else:
                self.logger.info("No new notifications")

        except Exception as e:
            self.logger.error(f"Error checking notifications: {e}")
            self.stats['errors'] += 1

        return new_notifications

    def _check_connections(self) -> List[Dict]:
        new_connections = []

        try:
            self.logger.info("Checking connection requests...")
            self.page.goto(f"{self.config.LINKEDIN_URL}/mynetwork/", wait_until='networkidle')
            self.page.wait_for_timeout(3000)

            requests = self.page.query_selector_all('div.invitation-card')

            for req in requests[:10]:
                try:
                    name_elem = req.query_selector('span.invitation-link__name')
                    name = name_elem.text_content().strip() if name_elem else 'Unknown'

                    title_elem = req.query_selector('span.invitation-link__occupation')
                    title = title_elem.text_content().strip() if title_elem else ''

                    if name:
                        item_id = hashlib.md5(name.encode()).hexdigest()[:12]

                        if item_id not in self.seen_items:
                            self.seen_items.add(item_id)
                            new_connections.append({
                                'name': name,
                                'title': title,
                                'content': f"New connection request from {name} - {title}"
                            })
                except:
                    continue

            if new_connections:
                self.logger.success(f"Found {len(new_connections)} new connection request(s)")
            else:
                self.logger.info("No new connection requests")

        except Exception as e:
            self.logger.error(f"Error checking connections: {e}")
            self.stats['errors'] += 1

        return new_connections

    def process_new_items(self, messages: List[Dict], notifications: List[Dict],
                         connections: List[Dict]):
        total_created = 0

        for msg in messages:
            filepath = self._create_action_item(
                item_type='message',
                sender=msg['sender'],
                content=msg['content'],
                extra_data={'is_sales_lead': msg['is_sales']}
            )

            self.stats['messages'] += 1

            if msg['is_sales']:
                self.stats['sales_leads'] += 1
                self.logger.sales(f"🎯 SALES LEAD: {msg['sender']}")
                self.logger.sales(f"   Content: {msg['content'][:100]}...")
            else:
                self.logger.info(f"📧 New message from {msg['sender']}")

            self.logger.info(f"   Created: {filepath}")
            total_created += 1

        for notif in notifications:
            filepath = self._create_action_item(
                item_type='notification',
                sender='LinkedIn',
                content=notif['content'],
                extra_data={'notification_type': notif['type']}
            )

            self.stats['notifications'] += 1

            if notif['is_sales']:
                self.stats['sales_leads'] += 1
                self.logger.sales(f"🎯 SALES LEAD in notification")
            else:
                self.logger.info(f"🔔 New notification: {notif['content'][:50]}...")

            self.logger.info(f"   Created: {filepath}")
            total_created += 1

        for conn in connections:
            filepath = self._create_action_item(
                item_type='connection',
                sender=conn['name'],
                content=conn['content'],
                extra_data={'title': conn['title']}
            )

            self.stats['connections'] += 1
            self.logger.info(f"🤝 New connection request: {conn['name']}")
            self.logger.info(f"   Created: {filepath}")
            total_created += 1

        if total_created > 0:
            self.logger.success(f"✨ Created {total_created} action item(s) in Needs_Action/")

    def start(self):
        self.logger.info("="*70)
        self.logger.info("LINKEDIN WATCHER - SILVER TIER")
        self.logger.info("="*70)
        self.logger.info(f"Check interval: {self.config.CHECK_INTERVAL}s")
        self.logger.info(f"Session path: {self.config.SESSION_PATH}")
        self.logger.info(f"Needs Action: {self.config.NEEDS_ACTION_PATH}")
        self.logger.info("="*70)

        if not self.config.LINKEDIN_EMAIL or not self.config.LINKEDIN_PASSWORD:
            self.logger.error("❌ LinkedIn credentials not found in .env!")
            self.logger.error("   Please add LINKEDIN_EMAIL and LINKEDIN_PASSWORD")
            return

        self.playwright = sync_playwright().start()

        try:
            self.browser = self.playwright.chromium.launch(
                headless=self.config.HEADLESS,
                args=['--disable-blink-features=AutomationControlled']
            )

            self.context = self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )

            self.page = self.context.new_page()

            session_loaded = self._load_session()

            if session_loaded:
                self.page.goto(self.config.LINKEDIN_URL, wait_until='networkidle')
                self.page.wait_for_timeout(3000)

                if not self._is_logged_in():
                    self.logger.warning("Session expired, re-authenticating...")
                    import asyncio
                    asyncio.get_event_loop().run_until_complete(self._login())
            else:
                import asyncio
                asyncio.get_event_loop().run_until_complete(self._login())

            self.page.wait_for_timeout(5000)

            self.logger.success("✅ LinkedIn Watcher started successfully!")
            self.logger.info("Monitoring for new activity...")
            self.logger.info("Press Ctrl+C to stop")
            print()

            check_count = 0
            while True:
                check_count += 1
                self.logger.info(f"\n{'='*50}")
                self.logger.info(f"Check #{check_count} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

                messages = []
                notifications = []
                connections = []

                if self.config.MONITOR_MESSAGES:
                    messages = self._check_messages()

                if self.config.MONITOR_NOTIFICATIONS:
                    notifications = self._check_notifications()

                if self.config.MONITOR_CONNECTIONS:
                    connections = self._check_connections()

                if messages or notifications or connections:
                    self.process_new_items(messages, notifications, connections)

                self._save_session()

                self.logger.info(f"\n📊 Stats: Messages={self.stats['messages']}, "
                               f"Connections={self.stats['connections']}, "
                               f"Notifications={self.stats['notifications']}, "
                               f"Sales Leads={self.stats['sales_leads']}")

                next_check = datetime.now().strftime('%H:%M:%S')
                self.logger.info(f"⏳ Next check at {next_check} ({self.config.CHECK_INTERVAL}s)")
                time.sleep(self.config.CHECK_INTERVAL)

        except KeyboardInterrupt:
            self.logger.info("\n\n👋 Stopping LinkedIn Watcher...")
        except Exception as e:
            self.logger.error(f"Fatal error: {e}")
            self.stats['errors'] += 1
        finally:
            self.logger.info("Saving session and closing...")
            self._save_session()

            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()

            print()
            self.logger.info("="*70)
            self.logger.info("FINAL STATS")
            self.logger.info("="*70)
            self.logger.info(f"Messages processed: {self.stats['messages']}")
            self.logger.info(f"Connections processed: {self.stats['connections']}")
            self.logger.info(f"Notifications processed: {self.stats['notifications']}")
            self.logger.info(f"Sales leads detected: {self.stats['sales_leads']}")
            self.logger.info(f"Errors encountered: {self.stats['errors']}")
            self.logger.info("="*70)


def main():
    if sys.platform == 'win32':
        sys.stdout.reconfigure(encoding='utf-8')

    watcher = LinkedInWatcher()
    watcher.start()


if __name__ == "__main__":
    main()

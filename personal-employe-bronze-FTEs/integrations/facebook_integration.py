#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Facebook Integration - Bronze Tier
Complete Facebook automation using Graph API ONLY.

Features:
- Post to Facebook Page using Graph API
- Monitor comments and messages via API
- Auto-response to comments/messages
- Lead detection from comments

Usage:
    python scripts\facebook_integration.py --post "Your message here"
    python scripts\facebook_integration.py --monitor
    python scripts\facebook_integration.py --insights
"""

import os
import sys
import json
import time
import hashlib
import re
import requests
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


# ============================================================================
# CONFIGURATION
# ============================================================================

class FacebookConfig:
    """Facebook Integration Configuration"""

    # Paths
    SCRIPT_DIR = Path(__file__).parent
    PROJECT_ROOT = SCRIPT_DIR.parent
    LOG_PATH = PROJECT_ROOT / 'AI_Employee_Vault' / 'Logs' / 'facebook.log'
    NEEDS_ACTION_PATH = PROJECT_ROOT / 'Needs_Action'

    # Facebook Graph API
    FACEBOOK_API_VERSION = os.getenv('FACEBOOK_API_VERSION', 'v18.0')
    FACEBOOK_GRAPH_URL = f'https://graph.facebook.com/{FACEBOOK_API_VERSION}'

    # API Credentials
    FACEBOOK_ACCESS_TOKEN = os.getenv('FACEBOOK_ACCESS_TOKEN', '')
    FACEBOOK_PAGE_ID = os.getenv('FACEBOOK_PAGE_ID', '')
    FACEBOOK_APP_ID = os.getenv('FACEBOOK_APP_ID', '')
    FACEBOOK_APP_SECRET = os.getenv('FACEBOOK_APP_SECRET', '')

    # Monitoring settings
    CHECK_INTERVAL = int(os.getenv('FACEBOOK_CHECK_INTERVAL', '120'))  # seconds

    # Monitoring options
    MONITOR_COMMENTS = os.getenv('FACEBOOK_MONITOR_COMMENTS', 'true').lower() == 'true'
    MONITOR_MESSAGES = os.getenv('FACEBOOK_MONITOR_MESSAGES', 'true').lower() == 'true'

    # Auto-response settings
    AUTO_RESPONSE_ENABLED = os.getenv('FACEBOOK_AUTO_RESPONSE', 'false').lower() == 'true'
    AUTO_RESPONSE_MESSAGE = os.getenv('FACEBOOK_AUTO_RESPONSE_MESSAGE', 'Thank you for your message! We will get back to you soon.')

    # Sales keywords
    SALES_KEYWORDS = [
        'interested', 'interest', 'demo', 'pricing', 'price', 'buy',
        'purchase', 'quote', 'proposal', 'contract', 'deal', 'opportunity',
        'budget', 'decision', 'timeline', 'requirements', 'rfp', 'rfi',
        'vendor', 'solution', 'partnership', 'collaboration', 'meeting',
        'call', 'discuss', 'explore', 'services', 'product', 'enterprise'
    ]


# ============================================================================
# LOGGER
# ============================================================================

class Logger:
    """Simple file and console logger"""

    def __init__(self, log_path: Path):
        self.log_path = log_path
        self._ensure_log_file()

    def _ensure_log_file(self):
        """Create log file if it doesn't exist"""
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.log_path.exists():
            self.log_path.touch()

    def _timestamp(self) -> str:
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def log(self, message: str, level: str = 'INFO'):
        """Log message to file and console"""
        timestamp = self._timestamp()
        log_line = f"[{timestamp}] [{level}] {message}"

        # Console output with colors
        if level == 'ERROR':
            print(f"\033[91m{log_line}\033[0m")  # Red
        elif level == 'WARNING':
            print(f"\033[93m{log_line}\033[0m")  # Yellow
        elif level == 'SUCCESS':
            print(f"\033[92m{log_line}\033[0m")  # Green
        elif level == 'SALES':
            print(f"\033[94m{log_line}\033[0m")  # Blue
        else:
            print(log_line)

        # File output
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


# ============================================================================
# FACEBOOK GRAPH API INTEGRATION
# ============================================================================

class FacebookGraphAPI:
    """Facebook Graph API integration for posting and analytics"""

    def __init__(self, access_token: str = None, page_id: str = None):
        self.config = FacebookConfig()
        self.access_token = access_token or self.config.FACEBOOK_ACCESS_TOKEN
        self.page_id = page_id or self.config.FACEBOOK_PAGE_ID
        self.base_url = self.config.FACEBOOK_GRAPH_URL

    def _make_request(self, endpoint: str, method: str = 'GET', data: dict = None) -> dict:
        """Make request to Facebook Graph API"""
        url = f"{self.base_url}/{endpoint}"
        params = {'access_token': self.access_token}

        try:
            if method == 'GET':
                response = requests.get(url, params=params, timeout=30)
            elif method == 'POST':
                params.update(data or {})
                response = requests.post(url, params=params, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, params=params, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            return {'error': str(e)}

    def post_to_page(self, message: str, link: str = None) -> dict:
        """Post to Facebook Page"""
        data = {'message': message}
        if link:
            data['link'] = link

        endpoint = f"{self.page_id}/feed"
        result = self._make_request(endpoint, method='POST', data=data)
        return result

    def get_page_info(self) -> dict:
        """Get Facebook Page info"""
        endpoint = f"{self.page_id}"
        params = {'fields': 'name,about,category,followers_count'}
        result = self._make_request(endpoint)
        return result

    def get_page_insights(self) -> dict:
        """Get Facebook Page insights/analytics"""
        metrics = ['page_impressions', 'page_engaged_users', 'page_post_engagements',
                  'page_likes', 'page_follows', 'page_views']
        metrics_str = ','.join(metrics)
        endpoint = f"{self.page_id}/insights"
        params = {'metric': metrics_str}
        result = self._make_request(endpoint)
        return result

    def get_page_posts(self, limit: int = 10) -> list:
        """Get recent posts from page"""
        endpoint = f"{self.page_id}/posts"
        params = {'limit': limit}
        result = self._make_request(endpoint)
        return result.get('data', [])

    def get_post_comments(self, post_id: str) -> list:
        """Get comments for a specific post"""
        endpoint = f"{post_id}/comments"
        result = self._make_request(endpoint)
        return result.get('data', [])

    def get_page_messages(self) -> list:
        """Get messages from page inbox"""
        endpoint = f"{self.page_id}/conversations"
        params = {'fields': 'messages{message,from,created_time}', 'limit': 50}
        result = self._make_request(endpoint)
        return result.get('data', [])

    def reply_to_comment(self, comment_id: str, message: str) -> dict:
        """Reply to a comment"""
        endpoint = f"{comment_id}/comments"
        data = {'message': message}
        result = self._make_request(endpoint, method='POST', data=data)
        return result

    def send_message(self, recipient_id: str, message: str) -> dict:
        """Send a message via Page"""
        endpoint = f"{self.page_id}/messages"
        data = {
            'recipient': {'id': recipient_id},
            'message': {'text': message}
        }
        result = self._make_request(endpoint, method='POST', data=data)
        return result


# ============================================================================
# MAIN FACEBOOK INTEGRATION CLASS
# ============================================================================

class FacebookIntegration:
    """Main Facebook Integration - Graph API ONLY"""

    def __init__(self):
        self.config = FacebookConfig()
        self.logger = Logger(self.config.LOG_PATH)
        self.graph_api = FacebookGraphAPI()
        self.seen_items: set = set()
        self.stats = {
            'posts': 0,
            'comments': 0,
            'messages': 0,
            'sales_leads': 0,
            'errors': 0
        }

        # Validate API credentials on init
        if not self.config.FACEBOOK_ACCESS_TOKEN:
            self.logger.error("❌ FACEBOOK_ACCESS_TOKEN not set in .env!")
        if not self.config.FACEBOOK_PAGE_ID:
            self.logger.error("❌ FACEBOOK_PAGE_ID not set in .env!")

    def _is_sales_lead(self, content: str) -> bool:
        """Check if content contains sales-related keywords"""
        content_lower = content.lower()
        for keyword in self.config.SALES_KEYWORDS:
            if keyword in content_lower:
                return True
        return False

    def _generate_item_id(self, content: str, sender: str) -> str:
        """Generate unique ID for an item"""
        unique_str = f"{sender}:{content}:{datetime.now().strftime('%Y%m%d')}"
        return hashlib.md5(unique_str.encode()).hexdigest()[:12]

    def _create_action_item(self, item_type: str, sender: str, content: str,
                           extra_data: dict = None) -> str:
        """Create markdown file in Needs_Action folder"""
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
# Facebook {item_type.title()} - {sender}

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
*Generated by Facebook Integration*
"""

        safe_sender = re.sub(r'[^\w\s-]', '', sender)[:30]
        filename = f"FACEBOOK_{item_type.upper()}_{safe_sender}_{timestamp}.md"
        filepath = self.config.NEEDS_ACTION_PATH / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(full_content)

        return str(filepath)

    def post_update(self, message: str, link: str = None) -> dict:
        """Post update to Facebook using Graph API"""
        self.logger.info("Posting to Facebook via Graph API...")

        # Validate credentials
        if not self.graph_api.access_token:
            self.logger.error("❌ Facebook Access Token not configured!")
            self.stats['errors'] += 1
            return {'error': 'No access token configured'}

        if not self.graph_api.page_id:
            self.logger.error("❌ Facebook Page ID not configured!")
            self.stats['errors'] += 1
            return {'error': 'No page ID configured'}

        # Post via API
        result = self.graph_api.post_to_page(message, link)

        if 'id' in result:
            self.stats['posts'] += 1
            self.logger.success(f"✅ Posted to Facebook! ID: {result['id']}")
            self._log_post_to_vault(message, result['id'])
            return result
        else:
            self.stats['errors'] += 1
            self.logger.error(f"❌ Failed to post: {result}")
            return {'error': 'Failed to post', 'details': result}

    def _log_post_to_vault(self, message: str, post_id: str):
        """Log post to AI Employee Vault"""
        vault_path = self.config.PROJECT_ROOT / 'AI_Employee_Vault' / 'Logs'
        vault_path.mkdir(parents=True, exist_ok=True)
        log_file = vault_path / 'facebook_posts.log'

        log_entry = f"""
{'='*60}
POST ID: {post_id}
TIMESTAMP: {datetime.now().isoformat()}
MESSAGE: {message[:200]}{'...' if len(message) > 200 else ''}
{'='*60}
"""
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)

    def monitor_comments(self) -> list:
        """Monitor comments on recent posts"""
        new_comments = []

        try:
            self.logger.info("Monitoring comments...")

            if not self.graph_api.access_token:
                self.logger.warning("No API token, skipping comment monitoring")
                return new_comments

            posts = self.graph_api.get_page_posts(limit=5)

            for post in posts:
                post_id = post.get('id')
                if not post_id:
                    continue

                comments = self.graph_api.get_post_comments(post_id)

                for comment in comments:
                    comment_id = comment.get('id', '')
                    message = comment.get('message', '')
                    sender = comment.get('from', {}).get('name', 'Unknown')

                    if not message or comment_id in self.seen_items:
                        continue

                    self.seen_items.add(comment_id)
                    is_sales = self._is_sales_lead(message)

                    new_comments.append({
                        'post_id': post_id,
                        'comment_id': comment_id,
                        'sender': sender,
                        'message': message,
                        'is_sales': is_sales
                    })

                    # Auto-response if enabled
                    if self.config.AUTO_RESPONSE_ENABLED and not is_sales:
                        self.graph_api.reply_to_comment(comment_id, self.config.AUTO_RESPONSE_MESSAGE)

                    # Create action item for sales leads
                    if is_sales:
                        self._create_action_item(
                            item_type='comment',
                            sender=sender,
                            content=message,
                            extra_data={'post_id': post_id, 'comment_id': comment_id}
                        )
                        self.stats['sales_leads'] += 1
                        self.logger.sales(f"🎯 SALES LEAD from comment: {sender}")
                    else:
                        self.stats['comments'] += 1
                        self.logger.info(f"💬 New comment from {sender}")

            if new_comments:
                self.logger.success(f"Found {len(new_comments)} new comment(s)")

        except Exception as e:
            self.logger.error(f"Error monitoring comments: {e}")
            self.stats['errors'] += 1

        return new_comments

    def monitor_messages(self) -> list:
        """Monitor messages from page inbox"""
        new_messages = []

        try:
            self.logger.info("Monitoring messages...")

            if not self.graph_api.access_token:
                self.logger.warning("No API token, skipping message monitoring")
                return new_messages

            conversations = self.graph_api.get_page_messages()

            for conv in conversations:
                messages = conv.get('messages', {}).get('data', [])

                for msg in messages:
                    message_id = msg.get('id', '')
                    message_text = msg.get('message', '')
                    sender = msg.get('from', {}).get('name', 'Unknown')
                    created_time = msg.get('created_time', '')

                    if not message_text or message_id in self.seen_items:
                        continue

                    self.seen_items.add(message_id)
                    is_sales = self._is_sales_lead(message_text)

                    new_messages.append({
                        'message_id': message_id,
                        'sender': sender,
                        'message': message_text,
                        'created_time': created_time,
                        'is_sales': is_sales
                    })

                    # Auto-response if enabled
                    if self.config.AUTO_RESPONSE_ENABLED and not is_sales:
                        sender_id = msg.get('from', {}).get('id', '')
                        if sender_id:
                            self.graph_api.send_message(sender_id, self.config.AUTO_RESPONSE_MESSAGE)

                    # Create action item
                    self._create_action_item(
                        item_type='message',
                        sender=sender,
                        content=message_text,
                        extra_data={'message_id': message_id}
                    )

                    if is_sales:
                        self.stats['sales_leads'] += 1
                        self.logger.sales(f"🎯 SALES LEAD from message: {sender}")
                    else:
                        self.stats['messages'] += 1
                        self.logger.info(f"📩 New message from {sender}")

            if new_messages:
                self.logger.success(f"Found {len(new_messages)} new message(s)")

        except Exception as e:
            self.logger.error(f"Error monitoring messages: {e}")
            self.stats['errors'] += 1

        return new_messages

    def get_insights(self) -> dict:
        """Get Facebook Page insights"""
        return self.graph_api.get_page_insights()

    def start_monitoring(self):
        """Start continuous monitoring using Graph API"""
        self.logger.info("="*70)
        self.logger.info("FACEBOOK MONITOR")
        self.logger.info("="*70)
        self.logger.info(f"Check interval: {self.config.CHECK_INTERVAL}s")
        self.logger.info(f"Auto-response: {self.config.AUTO_RESPONSE_ENABLED}")
        self.logger.info("="*70)

        # Validate credentials
        if not self.graph_api.access_token:
            self.logger.error("❌ No Facebook API token found!")
            self.logger.error("   Set FACEBOOK_ACCESS_TOKEN in .env")
            return

        if not self.graph_api.page_id:
            self.logger.error("❌ No Facebook Page ID found!")
            self.logger.error("   Set FACEBOOK_PAGE_ID in .env")
            return

        self.logger.success("✅ Facebook API credentials configured")

        try:
            check_count = 0

            while True:
                check_count += 1
                self.logger.info(f"\n{'='*50}")
                self.logger.info(f"Check #{check_count} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

                # Monitor comments and messages
                if self.config.MONITOR_COMMENTS:
                    self.monitor_comments()

                if self.config.MONITOR_MESSAGES:
                    self.monitor_messages()

                # Print stats
                self.logger.info(f"\n📊 Stats: Posts={self.stats['posts']}, "
                               f"Comments={self.stats['comments']}, "
                               f"Messages={self.stats['messages']}, "
                               f"Sales Leads={self.stats['sales_leads']}")

                next_check = datetime.now().strftime('%H:%M:%S')
                self.logger.info(f"⏳ Next check at {next_check} ({self.config.CHECK_INTERVAL}s)")
                time.sleep(self.config.CHECK_INTERVAL)

        except KeyboardInterrupt:
            self.logger.info("\n\n👋 Stopping Facebook Monitor...")
        finally:
            # Print final stats
            self.logger.info("="*70)
            self.logger.info("FINAL STATS")
            self.logger.info("="*70)
            self.logger.info(f"Posts created: {self.stats['posts']}")
            self.logger.info(f"Comments processed: {self.stats['comments']}")
            self.logger.info(f"Messages processed: {self.stats['messages']}")
            self.logger.info(f"Sales leads detected: {self.stats['sales_leads']}")
            self.logger.info(f"Errors: {self.stats['errors']}")


# ============================================================================
# CLI INTERFACE
# ============================================================================

def main():
    """CLI interface for Facebook Integration"""
    import argparse

    parser = argparse.ArgumentParser(description='Facebook Integration')
    parser.add_argument('--post', type=str, help='Post a message to Facebook')
    parser.add_argument('--link', type=str, help='Link to include in post')
    parser.add_argument('--monitor', action='store_true', help='Start monitoring mode')
    parser.add_argument('--insights', action='store_true', help='Get page insights')

    args = parser.parse_args()

    fb = FacebookIntegration()

    if args.post:
        result = fb.post_update(args.post, args.link)
        print(f"\nPost result: {json.dumps(result, indent=2)}")

    elif args.monitor:
        fb.start_monitoring()

    elif args.insights:
        insights = fb.get_insights()
        print(f"\nPage insights: {json.dumps(insights, indent=2, default=str)}")

    else:
        parser.print_help()


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gmail Watcher - Monitors Gmail for new important unread emails.

Uses Gmail API with OAuth 2.0 authentication.
Creates action files in the Needs_Action folder for new emails.
"""

import os
import sys
import base64
import time
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from email import message_from_bytes


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


class GmailWatcher(BaseWatcher):
    """
    Watcher that monitors Gmail for new important unread emails.

    Requires Gmail API credentials and OAuth 2.0 setup.
    """

    def __init__(
        self,
        vault_path: str,
        credentials_path: Optional[str] = None,
        token_path: Optional[str] = None,
        check_interval: int = 120,
        only_unread: bool = True,
        only_important: bool = True,
        max_results: int = 10
    ):
        """
        Initialize the Gmail watcher.

        Args:
            vault_path: Path to the AI_Employee_Vault root directory
            credentials_path: Path to Gmail API credentials JSON
            token_path: Path to OAuth token file
            check_interval: Seconds between checks (default: 120)
            only_unread: Only process unread emails (default: True)
            only_important: Only process important emails (default: True)
            max_results: Maximum emails to process per check (default: 10)
        """
        super().__init__(vault_path, check_interval)

        # Look for credentials.json in multiple locations
        if credentials_path:
            self.credentials_path = credentials_path
        else:
            # Try root directory first, then parent of vault
            root_credentials = os.path.join(
                os.path.dirname(os.path.dirname(self.vault_path)), "credentials.json"
            )
            parent_credentials = os.path.join(
                os.path.dirname(self.vault_path), "credentials.json"
            )
            self.credentials_path = root_credentials if os.path.exists(root_credentials) else parent_credentials
        
        self.token_path = token_path or os.path.join(
            self.vault_path, ".credentials", "gmail_token.json"
        )
        self.only_unread = only_unread
        self.only_important = only_important
        self.max_results = max_results

        self._service = None
        self._processed_ids: set = set()

        # Load previously processed email IDs
        self._load_processed_ids()

    def _load_processed_ids(self):
        """Load IDs of already processed emails from file."""
        processed_file = os.path.join(self.log_path, "processed_emails.txt")
        if os.path.exists(processed_file):
            try:
                with open(processed_file, 'r') as f:
                    self._processed_ids = set(line.strip() for line in f if line.strip())
                self.logger.info(f"Loaded {len(self._processed_ids)} previously processed email IDs")
            except Exception as e:
                self.logger.warning(f"Could not load processed emails: {e}")
                self._processed_ids = set()

    def _save_processed_id(self, email_id: str):
        """Save a processed email ID to file."""
        self._processed_ids.add(email_id)
        processed_file = os.path.join(self.log_path, "processed_emails.txt")
        try:
            with open(processed_file, 'a') as f:
                f.write(email_id + '\n')
        except Exception as e:
            self.logger.warning(f"Could not save processed email ID: {e}")

    def _authenticate(self):
        """
        Authenticate with Gmail API.

        Returns:
            Authenticated Gmail service object
        """
        try:
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow
            from google.auth.transport.requests import Request
            from googleapiclient.discovery import build
            import webbrowser

            SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

            creds = None

            # Load existing token
            if os.path.exists(self.token_path):
                creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)
                self.logger.info("Loaded existing OAuth token")

            # Refresh or get new credentials
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    self.logger.info("Refreshing expired token...")
                    creds.refresh(Request())
                elif os.path.exists(self.credentials_path):
                    self.logger.info("Starting OAuth flow...")
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, SCOPES
                    )
                    # Try to run local server with browser open
                    try:
                        # Attempt to open browser automatically
                        creds = flow.run_local_server(port=0, open_browser=True)
                    except Exception as browser_error:
                        # If browser fails, provide manual auth URL
                        self.logger.warning(f"Browser auto-open failed: {browser_error}")
                        self.logger.info("Attempting manual authentication...")
                        
                        # Get auth URL manually
                        auth_url, _ = flow.authorization_url(prompt='consent')
                        
                        print("\n" + "="*70)
                        print("AUTHENTICATION REQUIRED")
                        print("="*70)
                        print("\nBrowser auto-open failed. Please follow these steps:")
                        print(f"\n1. Open this URL in your browser:")
                        print(f"   {auth_url}")
                        print(f"\n2. Sign in with your Google account")
                        print(f"3. Grant permissions to the application")
                        print(f"4. You will be redirected to http://localhost/?code=...")
                        print(f"5. Copy the entire redirected URL")
                        print(f"\n6. Paste the URL here and press Enter:")
                        
                        redirect_response = input("\nRedirect URL: ").strip()
                        
                        if redirect_response:
                            # Fetch the code from the redirect URL
                            flow.fetch_token(code=redirect_response.split('code=')[1].split('&')[0] if 'code=' in redirect_response else redirect_response)
                            creds = flow.credentials
                            self.logger.info("Manual authentication successful")
                        else:
                            raise Exception("No authorization code provided")
                else:
                    raise FileNotFoundError(
                        f"Credentials not found at: {self.credentials_path}\n"
                        f"Please ensure credentials.json exists in the root directory."
                    )

                # Save token for future use
                os.makedirs(os.path.dirname(self.token_path), exist_ok=True)
                with open(self.token_path, 'w') as token:
                    token.write(creds.to_json())
                self.logger.info(f"OAuth token saved to: {self.token_path}")

            self._service = build('gmail', 'v1', credentials=creds)
            self.logger.info("Successfully authenticated with Gmail API")
            return self._service

        except ImportError as e:
            self.logger.error(f"Missing required packages. Run: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
            raise
        except Exception as e:
            self.logger.error(f"Authentication failed: {e}")
            raise

    def _get_service(self):
        """Get or create Gmail API service."""
        if self._service is None:
            self._authenticate()
        return self._service

    def _classify_priority(self, subject: str, snippet: str) -> str:
        """
        Classify email priority based on keywords.

        Args:
            subject: Email subject
            snippet: Email snippet/preview

        Returns:
            Priority level: 'high', 'medium', or 'low'
        """
        text = f"{subject} {snippet}".lower()

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

    def _decode_email(self, raw_message: str) -> Dict[str, Any]:
        """
        Decode raw Gmail message.

        Args:
            raw_message: Base64 encoded message

        Returns:
            Decoded email data
        """
        try:
            message_bytes = base64.urlsafe_b64decode(raw_message)
            mime_msg = message_from_bytes(message_bytes)

            subject = ""
            from_email = ""
            body = ""

            # Get headers
            for header in ['subject', 'from', 'to', 'date']:
                value = mime_msg.get(header, '')
                if header == 'subject':
                    subject = value
                elif header == 'from':
                    from_email = value

            # Get body
            if mime_msg.is_multipart():
                for part in mime_msg.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))

                    if content_type == "text/plain" and "attachment" not in content_disposition:
                        try:
                            body = part.get_payload(decode=True).decode('utf-8', errors='replace')
                        except:
                            pass
                        break
            else:
                try:
                    body = mime_msg.get_payload(decode=True).decode('utf-8', errors='replace')
                except:
                    body = mime_msg.get_payload()

            return {
                'subject': subject,
                'from': from_email,
                'body': body,
                'date': mime_msg.get('date', '')
            }

        except Exception as e:
            self.logger.error(f"Error decoding email: {e}")
            return {
                'subject': 'Error decoding email',
                'from': 'unknown',
                'body': str(e),
                'date': ''
            }

    def check_for_updates(self) -> List[Dict[str, Any]]:
        """
        Check Gmail for new important unread emails.

        Returns:
            List of new email items
        """
        new_items = []

        try:
            service = self._get_service()

            # Build query
            query_parts = []
            if self.only_unread:
                query_parts.append('is:unread')
            if self.only_important:
                query_parts.append('is:important')

            query = ' '.join(query_parts) if query_parts else ''

            # List messages
            results = service.users().messages().list(
                userId='me',
                q=query,
                maxResults=self.max_results
            ).execute()

            messages = results.get('messages', [])

            for message in messages:
                msg_id = message['id']

                # Skip already processed
                if msg_id in self._processed_ids:
                    continue

                # Get full message
                msg = service.users().messages().get(
                    userId='me',
                    id=msg_id,
                    format='raw'
                ).execute()

                # Decode email
                email_data = self._decode_email(msg['raw'])

                # Classify priority
                priority = self._classify_priority(email_data['subject'], email_data['body'][:200])

                # Create item
                item = {
                    'id': msg_id,
                    'title': email_data['subject'] or '(No Subject)',
                    'content': email_data['body'],
                    'source': f"Gmail: {email_data['from']}",
                    'timestamp': datetime.now(),
                    'priority': priority,
                    'metadata': {
                        'email_from': email_data['from'],
                        'email_date': email_data['date'],
                        'gmail_id': msg_id,
                        'snippet': msg.get('snippet', '')
                    },
                    'tags': ['email', 'gmail']
                }

                new_items.append(item)
                self._save_processed_id(msg_id)
                self.logger.info(f"Found new email: {item['title']}")

            if new_items:
                self.logger.info(f"Found {len(new_items)} new emails")
            else:
                self.logger.debug("No new emails found")

        except Exception as e:
            self.logger.error(f"Error checking Gmail: {e}")
            self.errors.append(f"Gmail check failed: {e}")

        return new_items

    def create_action_file(self, item: Dict[str, Any]) -> str:
        """
        Create an action file in Needs_Action folder for the email.

        Args:
            item: Email item dictionary

        Returns:
            Path to the created action file
        """
        needs_action_path = os.path.join(self.vault_path, "Needs_Action")
        os.makedirs(needs_action_path, exist_ok=True)

        # Generate filename
        timestamp = item['timestamp']
        safe_title = self._sanitize_filename(item['title'][:50])
        filename = f"{timestamp.strftime('%Y-%m-%d')}_gmail_{safe_title}.md"
        file_path = os.path.join(needs_action_path, filename)

        # Generate frontmatter
        frontmatter = self._generate_frontmatter(item)

        # Generate content
        metadata = item.get('metadata', {})
        content = f"""{frontmatter}
# 📧 {item['title']}

## Summary
New email received from {metadata.get('email_from', 'unknown')}

## Email Details

| Field | Value |
|-------|-------|
| **From** | {metadata.get('email_from', 'unknown')} |
| **Date** | {metadata.get('email_date', 'unknown')} |
| **Priority** | {item['priority']} |
| **Source** | Gmail |

## Content

{item['content'][:2000] if item['content'] else '(No content)'}

---

## Action Required

- [ ] Review email content
- [ ] Determine required response
- [ ] Take appropriate action
- [ ] Move to Done when complete

## Metadata

- **Gmail ID**: {metadata.get('gmail_id', 'N/A')}
- **Processed**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

        # Write file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return file_path


def main():
    """Run the Gmail watcher standalone."""
    # Set UTF-8 encoding for Windows console
    if sys.platform == 'win32':
        sys.stdout.reconfigure(encoding='utf-8')

    # Get vault path from argument or use default
    if len(sys.argv) >= 2:
        vault_path = sys.argv[1]
    else:
        # Default to AI_Employee_Vault in same directory as script
        vault_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "AI_Employee_Vault")

    watcher = GmailWatcher(
        vault_path=vault_path,
        check_interval=120  # Check every 2 minutes
    )

    print(f"Gmail Watcher starting. Vault: {vault_path}")
    print(f"Check interval: 120 seconds")
    print("Press Ctrl+C to stop")

    try:
        watcher.run()
    except KeyboardInterrupt:
        print("\nStopping watcher...")
        watcher.stop()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gmail Watcher for AI Employee Vault

Monitors Gmail for new important unread emails.
Uses Gmail API with OAuth 2.0 authentication.
"""

import os
import sys
import base64
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
from email import message_from_bytes

from .base_watcher import BaseWatcher


class GmailWatcher(BaseWatcher):
    """
    Watcher that monitors Gmail for new important unread emails.
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
        super().__init__(vault_path, check_interval)

        if credentials_path:
            self.credentials_path = credentials_path
        else:
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

        self._load_processed_ids()

    def _load_processed_ids(self):
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
        self._processed_ids.add(email_id)
        processed_file = os.path.join(self.log_path, "processed_emails.txt")
        try:
            with open(processed_file, 'a') as f:
                f.write(email_id + '\n')
        except Exception as e:
            self.logger.warning(f"Could not save processed email ID: {e}")

    def _authenticate(self):
        try:
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow
            from google.auth.transport.requests import Request
            from googleapiclient.discovery import build
            import webbrowser

            SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

            creds = None

            if os.path.exists(self.token_path):
                creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)
                self.logger.info("Loaded existing OAuth token")

            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    self.logger.info("Refreshing expired token...")
                    creds.refresh(Request())
                elif os.path.exists(self.credentials_path):
                    self.logger.info("Starting OAuth flow...")
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, SCOPES
                    )
                    try:
                        creds = flow.run_local_server(port=0, open_browser=True)
                    except Exception as browser_error:
                        self.logger.warning(f"Browser auto-open failed: {browser_error}")
                        self.logger.info("Attempting manual authentication...")

                        auth_url, _ = flow.authorization_url(prompt='consent')

                        print("\n" + "="*70)
                        print("AUTHENTICATION REQUIRED")
                        print("="*70)
                        print(f"\n1. Open this URL in your browser:")
                        print(f"   {auth_url}")
                        print(f"\n2. Sign in and grant permissions")
                        print(f"3. Copy the redirected URL")
                        print(f"\n4. Paste the URL here and press Enter:")

                        redirect_response = input("\nRedirect URL: ").strip()

                        if redirect_response:
                            flow.fetch_token(code=redirect_response.split('code=')[1].split('&')[0] if 'code=' in redirect_response else redirect_response)
                            creds = flow.credentials
                            self.logger.info("Manual authentication successful")
                        else:
                            raise Exception("No authorization code provided")
                else:
                    raise FileNotFoundError(
                        f"Credentials not found at: {self.credentials_path}"
                    )

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
        if self._service is None:
            self._authenticate()
        return self._service

    def _classify_priority(self, subject: str, snippet: str) -> str:
        text = f"{subject} {snippet}".lower()

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

    def _decode_email(self, raw_message: str) -> Dict[str, Any]:
        try:
            message_bytes = base64.urlsafe_b64decode(raw_message)
            mime_msg = message_from_bytes(message_bytes)

            subject = ""
            from_email = ""
            body = ""

            for header in ['subject', 'from', 'to', 'date']:
                value = mime_msg.get(header, '')
                if header == 'subject':
                    subject = value
                elif header == 'from':
                    from_email = value

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
        new_items = []

        try:
            service = self._get_service()

            query_parts = []
            if self.only_unread:
                query_parts.append('is:unread')
            if self.only_important:
                query_parts.append('is:important')

            query = ' '.join(query_parts) if query_parts else ''

            results = service.users().messages().list(
                userId='me',
                q=query,
                maxResults=self.max_results
            ).execute()

            messages = results.get('messages', [])

            for message in messages:
                msg_id = message['id']

                if msg_id in self._processed_ids:
                    continue

                msg = service.users().messages().get(
                    userId='me',
                    id=msg_id,
                    format='raw'
                ).execute()

                email_data = self._decode_email(msg['raw'])
                priority = self._classify_priority(email_data['subject'], email_data['body'][:200])

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
        needs_action_path = os.path.join(self.vault_path, "Needs_Action")
        os.makedirs(needs_action_path, exist_ok=True)

        timestamp = item['timestamp']
        safe_title = self._sanitize_filename(item['title'][:50])
        filename = f"{timestamp.strftime('%Y-%m-%d')}_gmail_{safe_title}.md"
        file_path = os.path.join(needs_action_path, filename)

        frontmatter = self._generate_frontmatter(item)

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

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return file_path

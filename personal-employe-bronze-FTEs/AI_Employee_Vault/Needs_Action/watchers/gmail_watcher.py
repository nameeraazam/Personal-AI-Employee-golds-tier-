#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gmail Watcher - Monitors Gmail for new important unread emails.

Uses Gmail API with OAuth 2.0 authentication.
Creates action files in the Needs_Action folder for new emails.
"""

import os
import base64
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from email import message_from_bytes

from .base_watcher import BaseWatcher


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
        
        self.credentials_path = credentials_path or os.path.join(
            self.vault_path, ".credentials", "gmail_credentials.json"
        )
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
            
            SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
            
            creds = None
            
            # Load existing token
            if os.path.exists(self.token_path):
                creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)
            
            # Refresh or get new credentials
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                elif os.path.exists(self.credentials_path):
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, SCOPES
                    )
                    creds = flow.run_local_server(port=0)
                else:
                    raise FileNotFoundError(
                        f"Credentials not found. Please place Gmail API credentials at: {self.credentials_path}"
                    )
                
                # Save token
                os.makedirs(os.path.dirname(self.token_path), exist_ok=True)
                with open(self.token_path, 'w') as token:
                    token.write(creds.to_json())
            
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
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python gmail_watcher.py <vault_path>")
        sys.exit(1)
    
    vault_path = sys.argv[1]
    
    watcher = GmailWatcher(
        vault_path=vault_path,
        check_interval=120
    )
    
    print(f"Gmail Watcher starting. Vault: {vault_path}")
    print("Press Ctrl+C to stop")
    
    try:
        watcher.run()
    except KeyboardInterrupt:
        print("\nStopping watcher...")
        watcher.stop()


if __name__ == "__main__":
    main()

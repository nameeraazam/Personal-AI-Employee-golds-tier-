#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn Post - Posts updates to LinkedIn using LinkedIn API v2.

Uses OAuth 2.0 authentication with manual first-time authorization.
Supports persistent token storage for reuse.
"""

import os
import sys
import json
import time
import logging
import webbrowser
from datetime import datetime
from typing import Optional, Dict, Any
from urllib.parse import urlencode
from http.server import HTTPServer, BaseHTTPRequestHandler


# Load .env file first (before class definition)
def load_dotenv(env_path=None):
    """Load environment variables from .env file."""
    if env_path is None:
        env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
        return True
    return False


# Load .env file
load_dotenv()


class LinkedInPoster:
    """
    Posts updates to LinkedIn using LinkedIn API v2.

    Requires LinkedIn Developer App credentials and OAuth 2.0 setup.
    """

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        access_token: Optional[str] = None,
        redirect_uri: str = "http://localhost:3000",
        token_path: Optional[str] = None
    ):
        """
        Initialize the LinkedIn poster.

        Args:
            client_id: LinkedIn App Client ID
            client_secret: LinkedIn App Client Secret
            access_token: Pre-existing access token (optional)
            redirect_uri: OAuth redirect URI (default: http://localhost:8080)
            token_path: Path to store OAuth token (default: script_dir/.linkedin_token.json)
        """
        # Get credentials from environment (loaded from .env)
        self.client_id = client_id or os.getenv('LINKEDIN_CLIENT_ID')
        self.client_secret = client_secret or os.getenv('LINKEDIN_CLIENT_SECRET')
        self.access_token = access_token or os.getenv('LINKEDIN_ACCESS_TOKEN')
        self.redirect_uri = redirect_uri
        
        # Token storage path - use script directory for easier access
        if token_path:
            self.token_path = token_path
        else:
            self.token_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".linkedin_token.json")
        
        # LinkedIn API endpoints
        self.auth_url = "https://www.linkedin.com/oauth/v2/authorization"
        self.token_url = "https://www.linkedin.com/oauth/v2/accessToken"
        self.api_base = "https://api.linkedin.com/v2"

        # Required scopes for posting (w_member_social only - others need special approval)
        self.scopes = ['w_member_social']

        
        # Setup logging
        self.logger = logging.getLogger("LinkedInPoster")
        self.logger.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        
        if not self.logger.handlers:
            self.logger.addHandler(console_handler)
        
        # Log credential status (not values for security)
        self.logger.debug(f"Client ID present: {bool(self.client_id)}")
        self.logger.debug(f"Client Secret present: {bool(self.client_secret)}")
        self.logger.debug(f"Access Token present: {bool(self.access_token)}")

    def _load_token(self) -> Optional[str]:
        """Load access token from storage."""
        if os.path.exists(self.token_path):
            try:
                with open(self.token_path, 'r') as f:
                    token_data = json.load(f)
                    access_token = token_data.get('access_token')
                    expires_at = token_data.get('expires_at', 0)
                    
                    # Check if token is still valid (with 5 minute buffer)
                    if access_token and time.time() < expires_at - 300:
                        self.logger.info("✓ Loaded valid access token from storage")
                        return access_token
                    else:
                        self.logger.info("⚠ Token expired, will re-authenticate")
            except Exception as e:
                self.logger.warning(f"Error loading token: {e}")
        
        return None

    def _save_token(self, access_token: str, expires_in: int):
        """Save access token to storage."""
        try:
            os.makedirs(os.path.dirname(self.token_path), exist_ok=True)
            token_data = {
                'access_token': access_token,
                'expires_at': time.time() + expires_in,
                'created_at': datetime.now().isoformat()
            }
            with open(self.token_path, 'w') as f:
                json.dump(token_data, f, indent=2)
            self.logger.info(f"✓ Access token saved to {self.token_path}")
        except Exception as e:
            self.logger.warning(f"Error saving token: {e}")

    def authenticate(self) -> str:
        """
        Perform OAuth 2.0 authentication with LinkedIn.

        Returns:
            Access token string
        """
        # Check for existing valid token
        existing_token = self._load_token()
        if existing_token:
            self.access_token = existing_token
            return existing_token

        # Validate credentials
        if not self.client_id:
            raise ValueError(
                "LINKEDIN_CLIENT_ID not found!\n\n"
                "Please check your .env file or set the environment variable.\n"
                f"Looking for .env at: {os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')}"
            )
        
        if not self.client_secret:
            raise ValueError(
                "LINKEDIN_CLIENT_SECRET not found!\n\n"
                "Please check your .env file or set the environment variable."
            )

        print("\n" + "="*70)
        print("LINKEDIN AUTHENTICATION")
        print("="*70)
        print(f"\nClient ID: {self.client_id[:10]}...")
        print(f"Client Secret: {self.client_secret[:10]}...")
        print("\nStarting OAuth 2.0 authorization flow...")
        
        # Build authorization URL
        auth_params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': ' '.join(self.scopes),
            'state': datetime.now().strftime('%Y%m%d%H%M%S')
        }
        
        auth_url = f"{self.auth_url}?{urlencode(auth_params)}"
        
        print(f"\nOpening browser for authorization...")
        print(f"If browser doesn't open, visit:")
        print(f"{auth_url}")
        
        # Open browser
        webbrowser.open(auth_url)
        
        # Start local server to capture callback
        print(f"\n✓ Listening on {self.redirect_uri} for authorization code...")
        print("\nPlease authorize the application in your browser.")
        print("Press Ctrl+C to cancel\n")
        
        # Capture authorization code
        auth_code = self._capture_auth_code()
        
        if not auth_code:
            raise Exception("Authorization cancelled or failed")
        
        # Exchange code for access token
        self.logger.info("Exchanging authorization code for access token...")
        access_token = self._exchange_code_for_token(auth_code)
        
        if access_token:
            self.access_token = access_token
            print("\n" + "="*70)
            print("✓ AUTHENTICATION SUCCESSFUL!")
            print("="*70)
            print(f"\nAccess token saved to: {self.token_path}")
            print("\nYou can now post updates using:")
            print(f'  python linkedin_post.py -m "Your message"')
            return access_token
        else:
            raise Exception("Failed to obtain access token")

    def _capture_auth_code(self) -> Optional[str]:
        """
        Capture authorization code from local server callback.

        Returns:
            Authorization code or None if cancelled
        """
        auth_code_container = {'code': None, 'error': None}
        
        class CallbackHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                from urllib.parse import parse_qs, urlparse
                
                parsed = urlparse(self.path)
                params = parse_qs(parsed.query)
                
                if 'code' in params:
                    auth_code_container['code'] = params['code'][0]
                    
                    # Send success response
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    
                    response = """
                    <html>
                        <head><title>Authorization Successful</title></head>
                        <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                            <h1 style="color: #0077b5;">✓ Authorization Successful!</h1>
                            <p>You can close this window and return to the application.</p>
                            <script>setTimeout(() => window.close(), 3000);</script>
                        </body>
                    </html>
                    """
                    self.wfile.write(response.encode())
                elif 'error' in params:
                    auth_code_container['error'] = params.get('error_description', ['Unknown error'])[0]
                    
                    self.send_response(400)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    
                    response = f"""
                    <html>
                        <head><title>Authorization Failed</title></head>
                        <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                            <h1 style="color: red;">✗ Authorization Failed</h1>
                            <p>Error: {auth_code_container['error']}</p>
                            <p>You can close this window.</p>
                        </body>
                    </html>
                    """
                    self.wfile.write(response.encode())
                else:
                    self.send_response(404)
                    self.end_headers()
            
            def log_message(self, format, *args):
                pass  # Suppress server logs
        
        # Start server on the redirect_uri port
        from urllib.parse import urlparse
        parsed = urlparse(self.redirect_uri)
        port = parsed.port or 8080
        
        server = HTTPServer(('localhost', port), CallbackHandler)
        server.timeout = 120  # 2 minute timeout
        
        try:
            server.handle_request()
        except Exception as e:
            self.logger.error(f"Server error: {e}")
            return None
        finally:
            server.server_close()
        
        if auth_code_container['error']:
            self.logger.error(f"Authorization error: {auth_code_container['error']}")
            return None
        
        return auth_code_container['code']

    def _exchange_code_for_token(self, auth_code: str) -> Optional[str]:
        """
        Exchange authorization code for access token.

        Args:
            auth_code: Authorization code from LinkedIn

        Returns:
            Access token or None
        """
        import requests
        from urllib.parse import quote

        token_data = {
            'grant_type': 'authorization_code',
            'code': auth_code,
            'redirect_uri': self.redirect_uri,
            'client_id': self.client_id,
            'client_secret': quote(self.client_secret, safe='')
        }

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        try:
            response = requests.post(self.token_url, data=token_data, headers=headers)
            response.raise_for_status()
            
            result = response.json()
            access_token = result.get('access_token')
            expires_in = result.get('expires_in', 5184000)  # Default 60 days
            
            if access_token:
                # Save token for future use
                self._save_token(access_token, expires_in)
                return access_token
            else:
                self.logger.error(f"Token response missing access_token: {result}")
                return None
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Token exchange failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                self.logger.error(f"Response: {e.response.text}")
            return None

    def post_update(self, message_text: str, visibility: str = "PUBLIC") -> Dict[str, Any]:
        """
        Post an update to LinkedIn.

        Args:
            message_text: The text content to post (max 3000 characters)
            visibility: Post visibility - PUBLIC, CONNECTIONS, or PRIVATE

        Returns:
            API response dictionary with post ID and status
        """
        import requests
        
        # Ensure we have an access token
        if not self.access_token:
            self.access_token = self._load_token()
        
        if not self.access_token:
            raise Exception("No access token. Run 'python linkedin_post.py --auth' first.")
        
        # Validate message length
        if len(message_text) > 3000:
            raise ValueError("Message text exceeds 3000 character limit")
        
        if len(message_text) == 0:
            raise ValueError("Message text cannot be empty")
        
        # Build API request
        url = f"{self.api_base}/shares"
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'X-Restli-Protocol-Version': '2.0.0',
            'Content-Type': 'application/json'
        }
        
        # LinkedIn API v2 share format
        payload = {
            "text": {
                "text": message_text
            },
            "visibility": visibility
        }
        
        self.logger.info(f"Posting update to LinkedIn (visibility: {visibility})...")
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            result = response.json()
            
            # Extract post ID from response
            post_id = result.get('id', 'unknown')
            status = result.get('status', 'PUBLISHED')
            
            self.logger.info(f"✓ Post successful! ID: {post_id}")
            
            return {
                'success': True,
                'id': post_id,
                'status': status,
                'message': message_text[:100] + '...' if len(message_text) > 100 else message_text,
                'timestamp': datetime.now().isoformat()
            }
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"✗ Post failed: {e}")
            error_response = {
                'success': False,
                'error': str(e)
            }
            
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    error_response['serviceErrorCode'] = error_data.get('serviceErrorCode')
                    error_response['message'] = error_data.get('message')
                    error_response['status'] = e.response.status_code
                    
                    self.logger.error(f"LinkedIn API Error: {error_data}")
                except:
                    error_response['status'] = e.response.status_code
                    error_response['message'] = e.response.text
            
            return error_response

    def get_profile(self) -> Optional[Dict[str, Any]]:
        """
        Get current user's basic profile information.

        Returns:
            Profile dictionary or None
        """
        import requests
        
        if not self.access_token:
            self.access_token = self._load_token()
        
        if not self.access_token:
            raise Exception("No access token. Run 'python linkedin_post.py --auth' first.")
        
        url = f"{self.api_base}/me"
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'X-Restli-Protocol-Version': '2.0.0'
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            profile = response.json()
            return profile
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to get profile: {e}")
            return None

    @classmethod
    def from_env(cls) -> 'LinkedInPoster':
        """
        Create LinkedInPoster instance from environment variables.

        Returns:
            Configured LinkedInPoster instance
        """
        return cls(
            client_id=os.getenv('LINKEDIN_CLIENT_ID'),
            client_secret=os.getenv('LINKEDIN_CLIENT_SECRET'),
            access_token=os.getenv('LINKEDIN_ACCESS_TOKEN')
        )


def main():
    """Main entry point for CLI usage."""
    import argparse
    
    # Set UTF-8 encoding for Windows console
    if sys.platform == 'win32':
        sys.stdout.reconfigure(encoding='utf-8')
    
    parser = argparse.ArgumentParser(
        description='Post updates to LinkedIn',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # First-time authentication
  python linkedin_post.py --auth
  
  # Post an update
  python linkedin_post.py --message "Your professional update here"
  
  # Check profile
  python linkedin_post.py --profile
        """
    )
    
    parser.add_argument(
        '--auth', '-a',
        action='store_true',
        help='Run OAuth authentication flow'
    )
    
    parser.add_argument(
        '--message', '-m',
        type=str,
        help='Message text to post (max 3000 characters)'
    )
    
    parser.add_argument(
        '--visibility', '-v',
        type=str,
        choices=['PUBLIC', 'CONNECTIONS', 'PRIVATE'],
        default='PUBLIC',
        help='Post visibility (default: PUBLIC)'
    )
    
    parser.add_argument(
        '--profile', '-p',
        action='store_true',
        help='Display current LinkedIn profile'
    )
    
    parser.add_argument(
        '--client-id',
        type=str,
        help='LinkedIn Client ID (overrides .env)'
    )
    
    parser.add_argument(
        '--client-secret',
        type=str,
        help='LinkedIn Client Secret (overrides .env)'
    )
    
    args = parser.parse_args()
    
    # Initialize poster
    poster = LinkedInPoster(
        client_id=args.client_id,
        client_secret=args.client_secret
    )
    
    # Handle authentication
    if args.auth:
        try:
            print("\n" + "="*70)
            print("LINKEDIN CREDENTIALS CHECK")
            print("="*70)
            print(f"Client ID: {poster.client_id[:10] + '...' if poster.client_id else 'NOT FOUND'}")
            print(f"Client Secret: {poster.client_secret[:10] + '...' if poster.client_secret else 'NOT FOUND'}")
            print(f"Access Token: {poster.access_token[:10] + '...' if poster.access_token else 'NOT FOUND'}")
            print("="*70)
            
            if not poster.client_id or not poster.client_secret:
                print("\n✗ ERROR: Credentials not found!")
                print("\nPlease check your .env file at:")
                print(f"  {os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')}")
                print("\nIt should contain:")
                print("  LINKEDIN_CLIENT_ID=your_client_id")
                print("  LINKEDIN_CLIENT_SECRET=your_client_secret")
                sys.exit(1)
            
            token = poster.authenticate()
            
        except Exception as e:
            print(f"\n✗ Authentication failed: {e}")
            sys.exit(1)
    
    # Display profile
    elif args.profile:
        try:
            if not poster.access_token:
                poster.access_token = poster._load_token()
            
            if not poster.access_token:
                print("No access token. Run 'python linkedin_post.py --auth' first.")
                sys.exit(1)
            
            profile = poster.get_profile()
            if profile:
                print("\nLinkedIn Profile:")
                print(f"  ID: {profile.get('id', 'N/A')}")
                print(f"  First Name: {profile.get('firstName', 'N/A')}")
                print(f"  Last Name: {profile.get('lastName', 'N/A')}")
            else:
                print("Failed to retrieve profile")
        except Exception as e:
            print(f"\n✗ Error: {e}")
            sys.exit(1)
    
    # Post message
    elif args.message:
        try:
            # Ensure we have a token
            if not poster.access_token:
                poster.access_token = poster._load_token()
            
            if not poster.access_token:
                print("No access token. Run 'python linkedin_post.py --auth' first.")
                sys.exit(1)
            
            result = poster.post_update(args.message, args.visibility)
            
            if result.get('success'):
                print("\n" + "="*70)
                print("✓ POST SUCCESSFUL!")
                print("="*70)
                print(f"  Post ID: {result['id']}")
                print(f"  Status: {result['status']}")
                print(f"  Message: {result['message']}")
                print("="*70)
            else:
                print("\n✗ Post failed!")
                print(f"  Error: {result.get('error', 'Unknown error')}")
                print(f"  Code: {result.get('serviceErrorCode', 'N/A')}")
                sys.exit(1)
                
        except Exception as e:
            print(f"\n✗ Error: {e}")
            sys.exit(1)
    
    else:
        parser.print_help()
        print("\n" + "="*70)
        print("Quick Start:")
        print("  1. First-time setup: python linkedin_post.py --auth")
        print("  2. Post update: python linkedin_post.py -m \"Your message\"")
        print("="*70)


if __name__ == "__main__":
    main()

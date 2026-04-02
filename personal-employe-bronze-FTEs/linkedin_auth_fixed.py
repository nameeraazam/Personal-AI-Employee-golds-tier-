#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn OAuth Authentication - Fixed Version
Resolves "Something went wrong" error
"""

import os
import sys
import json
import time
import logging
import webbrowser
from datetime import datetime
from typing import Optional, Dict, Any
from urllib.parse import urlencode, parse_qs, urlparse
from http.server import HTTPServer, BaseHTTPRequestHandler
import socket

# Load .env file
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

load_dotenv()

class LinkedInAuth:
    """LinkedIn OAuth 2.0 Authentication - Fixed Version"""

    def __init__(self):
        self.client_id = os.getenv('LINKEDIN_CLIENT_ID')
        self.client_secret = os.getenv('LINKEDIN_CLIENT_SECRET')
        self.access_token = os.getenv('LINKEDIN_ACCESS_TOKEN')
        
        # Use port 3000 instead (sometimes 8080 has issues)
        self.redirect_uri = "http://localhost:3000"
        self.token_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".linkedin_token.json")
        
        self.auth_url = "https://www.linkedin.com/oauth/v2/authorization"
        self.token_url = "https://www.linkedin.com/oauth/v2/accessToken"
        self.api_base = "https://api.linkedin.com/v2"
        
        # IMPORTANT: Use correct scopes - w_member_social is for posting
        self.scopes = ['r_basicprofile', 'w_member_social', 'r_emailaddress']
        
        self.logger = logging.getLogger("LinkedInAuth")
        self.logger.setLevel(logging.DEBUG)
        
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        
        if not self.logger.handlers:
            self.logger.addHandler(handler)

    def find_available_port(self, start_port=3000):
        """Find an available port"""
        for port in range(start_port, start_port + 100):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('localhost', port))
                    return port
            except OSError:
                continue
        return start_port

    def authenticate(self) -> str:
        """Perform OAuth 2.0 authentication"""
        
        # Check for existing token
        existing_token = self._load_token()
        if existing_token:
            print("\n✓ Valid token found!")
            return existing_token

        # Validate credentials
        print("\n" + "="*70)
        print("LINKEDIN AUTHENTICATION - FIXED VERSION")
        print("="*70)
        print(f"\nClient ID: {self.client_id}")
        print(f"Client Secret: {self.client_secret[:10]}...")
        print(f"Redirect URI: {self.redirect_uri}")
        print(f"Scopes: {', '.join(self.scopes)}")
        print("="*70)

        if not self.client_id or len(self.client_id) < 10:
            print("\n✗ ERROR: Invalid Client ID!")
            print("Check your .env file - LINKEDIN_CLIENT_ID must be set correctly")
            return None

        if not self.client_secret or len(self.client_secret) < 10:
            print("\n✗ ERROR: Invalid Client Secret!")
            print("Check your .env file - LINKEDIN_CLIENT_SECRET must be set correctly")
            return None

        # Build authorization URL with state parameter
        state = f"linkauth_{int(time.time())}"
        auth_params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': ' '.join(self.scopes),
            'state': state
        }

        auth_url = f"{self.auth_url}?{urlencode(auth_params)}"

        print(f"\n📋 STEP 1: Copy this URL and paste in browser:")
        print("="*70)
        print(auth_url)
        print("="*70)
        
        print(f"\n🌐 Opening browser... (if it doesn't open, paste the URL manually)")
        
        try:
            webbrowser.open(auth_url)
        except Exception as e:
            print(f"Browser open failed: {e}")

        # Find available port
        try:
            port = int(self.redirect_uri.split(':')[-1])
            actual_port = self.find_available_port(port)
            if actual_port != port:
                print(f"\n⚠ Port {port} busy, using {actual_port} instead")
                self.redirect_uri = f"http://localhost:{actual_port}"
        except:
            actual_port = 3000

        print(f"\n📡 STEP 2: Listening on {self.redirect_uri}...")
        print("⏳ Waiting for authorization callback...")
        print("💡 After authorizing in browser, you'll be redirected back")
        print("🛑 Press Ctrl+C to cancel\n")

        # Capture authorization code
        auth_code = self._capture_auth_code(actual_port)

        if not auth_code:
            print("\n✗ ERROR: No authorization code received")
            print("\nPossible issues:")
            print("  1. Redirect URI not configured in LinkedIn Developer App")
            print("  2. You clicked 'Cancel' instead of 'Allow'")
            print("  3. Browser blocked the redirect")
            return None

        print(f"\n✓ Authorization code received!")
        print(f"\n🔄 STEP 3: Exchanging code for access token...")

        # Exchange code for token
        access_token = self._exchange_code_for_token(auth_code)

        if access_token:
            print("\n" + "="*70)
            print("✅ AUTHENTICATION SUCCESSFUL!")
            print("="*70)
            print(f"\nToken saved to: {self.token_path}")
            print("\nYou can now post to LinkedIn!")
            return access_token
        else:
            print("\n✗ ERROR: Failed to get access token")
            return None

    def _capture_auth_code(self, port=3000) -> Optional[str]:
        """Capture authorization code from callback"""
        auth_code_container = {'code': None, 'error': None, 'state': None}

        class CallbackHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                parsed = urlparse(self.path)
                params = parse_qs(parsed.query)

                if 'code' in params:
                    auth_code_container['code'] = params['code'][0]
                    auth_code_container['state'] = params.get('state', [None])[0]

                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()

                    response = """
                    <!DOCTYPE html>
                    <html>
                    <head><title>LinkedIn Auth Success</title></head>
                    <body style="font-family: Arial; text-align: center; padding: 50px; background: #f0f0f0;">
                        <div style="background: white; padding: 30px; border-radius: 10px; display: inline-block;">
                            <h1 style="color: #0077b5;">✅ Authorization Successful!</h1>
                            <p>You can close this window and return to the application.</p>
                            <p style="color: #666; font-size: 12px;">Redirecting...</p>
                        </div>
                        <script>setTimeout(() => window.close(), 5000);</script>
                    </body>
                    </html>
                    """
                    self.wfile.write(response.encode())
                    print("\n✓ Authorization callback received!")
                    
                elif 'error' in params:
                    auth_code_container['error'] = params.get('error', ['Unknown'])[0]
                    error_desc = params.get('error_description', ['No description'])[0]

                    self.send_response(400)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()

                    response = f"""
                    <!DOCTYPE html>
                    <html>
                    <head><title>Authorization Failed</title></head>
                    <body style="font-family: Arial; text-align: center; padding: 50px;">
                        <h1 style="color: red;">✗ Authorization Failed</h1>
                        <p><b>Error:</b> {auth_code_container['error']}</p>
                        <p><b>Description:</b> {error_desc}</p>
                        <p>Please check your LinkedIn Developer App settings.</p>
                    </body>
                    </html>
                    """
                    self.wfile.write(response.encode())
                else:
                    self.send_response(404)
                    self.end_headers()

            def log_message(self, format, *args):
                pass

        server = HTTPServer(('localhost', port), CallbackHandler)
        server.timeout = 180  # 3 minute timeout

        try:
            server.handle_request()
        except Exception as e:
            self.logger.error(f"Server error: {e}")
            return None
        finally:
            server.server_close()

        if auth_code_container['error']:
            print(f"\n✗ Authorization error: {auth_code_container['error']}")
            if auth_code_container['error'] == 'access_denied':
                print("  You denied the authorization request.")
            elif auth_code_container['error'] == 'unauthorized_member':
                print("  Your LinkedIn account doesn't have API access.")
            return None

        return auth_code_container['code']

    def _exchange_code_for_token(self, auth_code: str) -> Optional[str]:
        """Exchange authorization code for access token"""
        try:
            import requests
        except ImportError:
            print("✗ ERROR: 'requests' library not installed")
            print("  Run: pip install requests")
            return None

        token_data = {
            'grant_type': 'authorization_code',
            'code': auth_code,
            'redirect_uri': self.redirect_uri,
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        print(f"\nSending token request to LinkedIn...")
        print(f"  Code: {auth_code[:20]}...")
        print(f"  Redirect URI: {self.redirect_uri}")

        try:
            response = requests.post(self.token_url, data=token_data, headers=headers, timeout=30)
            
            print(f"\nResponse status: {response.status_code}")
            
            if response.status_code != 200:
                print(f"\n✗ Token request failed!")
                print(f"  Status: {response.status_code}")
                print(f"  Response: {response.text}")
                return None

            result = response.json()
            print(f"\nToken response received:")
            print(f"  Access Token: {result.get('access_token', 'N/A')[:20]}...")
            print(f"  Expires In: {result.get('expires_in', 'N/A')} seconds")

            access_token = result.get('access_token')
            expires_in = result.get('expires_in', 5184000)

            if access_token:
                self._save_token(access_token, expires_in)
                return access_token
            else:
                print(f"✗ No access_token in response: {result}")
                return None

        except requests.exceptions.RequestException as e:
            print(f"\n✗ Token exchange failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"  Response: {e.response.text}")
            return None

    def _load_token(self) -> Optional[str]:
        """Load access token from storage"""
        if os.path.exists(self.token_path):
            try:
                with open(self.token_path, 'r') as f:
                    token_data = json.load(f)
                    access_token = token_data.get('access_token')
                    expires_at = token_data.get('expires_at', 0)

                    if access_token and time.time() < expires_at - 300:
                        return access_token
            except Exception as e:
                print(f"Error loading token: {e}")
        return None

    def _save_token(self, access_token: str, expires_in: int):
        """Save access token to storage"""
        try:
            token_data = {
                'access_token': access_token,
                'expires_at': time.time() + expires_in,
                'created_at': datetime.now().isoformat()
            }
            with open(self.token_path, 'w') as f:
                json.dump(token_data, f, indent=2)
            print(f"✓ Token saved to: {self.token_path}")
        except Exception as e:
            print(f"Error saving token: {e}")

    def test_connection(self) -> bool:
        """Test if the access token works"""
        try:
            import requests
        except ImportError:
            return False

        token = self._load_token()
        if not token:
            print("No valid token found")
            return False

        url = f"{self.api_base}/me"
        headers = {
            'Authorization': f'Bearer {token}',
            'X-Restli-Protocol-Version': '2.0.0'
        }

        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                profile = response.json()
                print("\n✓ Connection test successful!")
                print(f"  Profile ID: {profile.get('id', 'N/A')}")
                return True
            else:
                print(f"\n✗ Connection test failed: {response.status_code}")
                print(f"  Response: {response.text}")
                return False
        except Exception as e:
            print(f"\n✗ Connection test error: {e}")
            return False


def main():
    """Main function"""
    if sys.platform == 'win32':
        sys.stdout.reconfigure(encoding='utf-8')

    print("\n" + "="*70)
    print("LINKEDIN OAUTH AUTHENTICATION TOOL")
    print("="*70)

    auth = LinkedInAuth()

    print("\n📝 CHECKING CONFIGURATION...")
    print(f"  .env file exists: {os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env'))}")
    print(f"  Client ID: {auth.client_id if auth.client_id else 'MISSING'}")
    print(f"  Client Secret: {'Present' if auth.client_secret else 'MISSING'}")
    print(f"  Existing Token: {'Found' if auth.access_token else 'Not found'}")

    print("\n⚙️  REQUIRED LINKEDIN APP SETTINGS:")
    print("  1. Go to: https://www.linkedin.com/developer/apps")
    print("  2. Select your app")
    print("  3. Go to 'Auth' tab")
    print(f"  4. Add Redirect URL: {auth.redirect_uri}")
    print("  5. Under 'Default Scope' add:")
    print("     - r_basicprofile")
    print("     - w_member_social")
    print("     - r_emailaddress")
    print("  6. Make sure app status is 'Live'")
    print("  7. Click 'Save'")

    input("\nPress Enter after you've configured the LinkedIn app...")

    print("\n🚀 Starting authentication...")
    token = auth.authenticate()

    if token:
        print("\n✅ Testing connection...")
        if auth.test_connection():
            print("\n🎉 SUCCESS! You can now use LinkedIn posting!")
            print("\nUsage:")
            print('  python linkedin_post.py -m "Your message here"')
        else:
            print("\n⚠ Token obtained but connection test failed")
            print("  Token might need time to activate, or scopes might be incorrect")
    else:
        print("\n❌ Authentication failed!")
        print("\nTroubleshooting:")
        print("  1. Verify Client ID and Secret are correct")
        print("  2. Make sure redirect URI is added in LinkedIn Developer App")
        print("  3. Check that required scopes are added")
        print("  4. Try clearing browser cache and cookies")
        print("  5. Try in incognito/private browsing mode")


if __name__ == "__main__":
    main()

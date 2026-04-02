#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn OAuth - Auto Run Version
No manual Enter required
"""

import os
import sys
import json
import time
import logging
import webbrowser
from datetime import datetime
from typing import Optional
from urllib.parse import urlencode, parse_qs, urlparse
from http.server import HTTPServer, BaseHTTPRequestHandler
import socket

def load_dotenv(env_path=None):
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
    def __init__(self):
        self.client_id = os.getenv('LINKEDIN_CLIENT_ID')
        self.client_secret = os.getenv('LINKEDIN_CLIENT_SECRET')
        self.access_token = os.getenv('LINKEDIN_ACCESS_TOKEN')
        self.redirect_uri = "http://localhost:3000"
        self.token_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".linkedin_token.json")
        self.auth_url = "https://www.linkedin.com/oauth/v2/authorization"
        self.token_url = "https://www.linkedin.com/oauth/v2/accessToken"
        self.api_base = "https://api.linkedin.com/v2"
        self.scopes = ['r_basicprofile', 'w_member_social', 'r_emailaddress']
        
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger()

    def _load_token(self) -> Optional[str]:
        if os.path.exists(self.token_path):
            try:
                with open(self.token_path, 'r') as f:
                    token_data = json.load(f)
                    access_token = token_data.get('access_token')
                    expires_at = token_data.get('expires_at', 0)
                    if access_token and time.time() < expires_at - 300:
                        return access_token
            except:
                pass
        return None

    def _save_token(self, access_token: str, expires_in: int):
        token_data = {
            'access_token': access_token,
            'expires_at': time.time() + expires_in,
            'created_at': datetime.now().isoformat()
        }
        with open(self.token_path, 'w') as f:
            json.dump(token_data, f, indent=2)
        self.logger.info(f"Token saved to: {self.token_path}")

    def _capture_auth_code(self, port=3000) -> Optional[str]:
        auth_code_container = {'code': None, 'error': None}

        class CallbackHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                parsed = urlparse(self.path)
                params = parse_qs(parsed.query)
                if 'code' in params:
                    auth_code_container['code'] = params['code'][0]
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    response = """
                    <!DOCTYPE html>
                    <html>
                    <head><title>Success</title></head>
                    <body style="font-family:Arial;text-align:center;padding:50px;">
                        <h1 style="color:#0077b5;">✓ Success!</h1>
                        <p>Authorization complete. Close this window.</p>
                        <script>setTimeout(() => window.close(), 3000);</script>
                    </body>
                    </html>
                    """
                    self.wfile.write(response.encode())
                elif 'error' in params:
                    auth_code_container['error'] = params.get('error', ['Unknown'])[0]
                    self.send_response(400)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    response = f"<html><body><h1>Error: {auth_code_container['error']}</h1></body></html>"
                    self.wfile.write(response.encode())
                else:
                    self.send_response(404)
                    self.end_headers()
            def log_message(self, format, *args):
                pass

        server = HTTPServer(('localhost', port), CallbackHandler)
        server.timeout = 180
        try:
            server.handle_request()
        except Exception as e:
            self.logger.error(f"Server error: {e}")
            return None
        finally:
            server.server_close()

        if auth_code_container['error']:
            self.logger.error(f"Auth error: {auth_code_container['error']}")
            return None
        return auth_code_container['code']

    def _exchange_code_for_token(self, auth_code: str) -> Optional[str]:
        try:
            import requests
        except ImportError:
            self.logger.error("Install requests: pip install requests")
            return None

        token_data = {
            'grant_type': 'authorization_code',
            'code': auth_code,
            'redirect_uri': self.redirect_uri,
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        try:
            response = requests.post(self.token_url, data=token_data, headers=headers, timeout=30)
            self.logger.info(f"Response status: {response.status_code}")
            
            if response.status_code != 200:
                self.logger.error(f"Token request failed: {response.text}")
                return None

            result = response.json()
            access_token = result.get('access_token')
            expires_in = result.get('expires_in', 5184000)

            if access_token:
                self._save_token(access_token, expires_in)
                return access_token
            else:
                self.logger.error(f"No access_token in response: {result}")
                return None
        except Exception as e:
            self.logger.error(f"Token exchange failed: {e}")
            return None

    def authenticate(self) -> Optional[str]:
        existing_token = self._load_token()
        if existing_token:
            self.logger.info("✓ Valid token found!")
            return existing_token

        print("\n" + "="*70)
        print("LINKEDIN AUTHENTICATION")
        print("="*70)
        print(f"Client ID: {self.client_id}")
        print(f"Redirect URI: {self.redirect_uri}")
        print(f"Scopes: {', '.join(self.scopes)}")
        print("="*70)

        if not self.client_id or len(self.client_id) < 10:
            print("\n✗ ERROR: Invalid Client ID!")
            return None

        # Build auth URL
        state = f"auth_{int(time.time())}"
        auth_params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': ' '.join(self.scopes),
            'state': state
        }
        auth_url = f"{self.auth_url}?{urlencode(auth_params)}"

        print(f"\n📋 OPENING BROWSER...")
        print(f"\nIf browser doesn't open, copy this URL:")
        print("="*70)
        print(auth_url)
        print("="*70)

        webbrowser.open(auth_url)

        print(f"\n📡 Listening on {self.redirect_uri}...")
        print("⏳ Waiting for authorization...")

        auth_code = self._capture_auth_code(3000)
        if not auth_code:
            print("\n✗ No authorization code received")
            return None

        print("\n✓ Code received, exchanging for token...")
        access_token = self._exchange_code_for_token(auth_code)
        
        if access_token:
            print("\n" + "="*70)
            print("✅ AUTHENTICATION SUCCESSFUL!")
            print("="*70)
            return access_token
        else:
            print("\n✗ Failed to get access token")
            return None

def main():
    if sys.platform == 'win32':
        sys.stdout.reconfigure(encoding='utf-8')

    print("\n" + "="*70)
    print("LINKEDIN OAUTH - AUTO RUN")
    print("="*70)
    
    auth = LinkedInAuth()
    
    print("\n⚠️  IMPORTANT: Configure LinkedIn Developer App first!")
    print("   URL: https://www.linkedin.com/developer/apps")
    print(f"   Redirect URL: {auth.redirect_uri}")
    print("   Scopes: r_basicprofile, w_member_social, r_emailaddress")
    print("="*70)
    
    time.sleep(2)
    print("\n🚀 Starting authentication in 3 seconds...")
    time.sleep(3)
    
    token = auth.authenticate()
    
    if token:
        print("\n🎉 SUCCESS! Token obtained.")
    else:
        print("\n❌ Authentication failed!")
        print("\nFix steps:")
        print("  1. Go to https://www.linkedin.com/developer/apps")
        print("  2. Select your app (Client ID: 776cjxrw9m5yyq)")
        print("  3. Go to 'Auth' tab")
        print(f"  4. Add Redirect URL: {auth.redirect_uri}")
        print("  5. Add scopes: r_basicprofile, w_member_social, r_emailaddress")
        print("  6. Save and try again")

if __name__ == "__main__":
    main()

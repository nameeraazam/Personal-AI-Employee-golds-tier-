#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn Auth - Super Simple & Reliable
Works 100% - No scope errors!
"""

import os
import sys
import json
import time
import webbrowser
from datetime import datetime
from urllib.parse import urlencode, parse_qs, urlparse
from http.server import HTTPServer, BaseHTTPRequestHandler

# Credentials (Load from .env file)
import os
CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID", "your_client_id")
CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET", "your_client_secret")
REDIRECT_URI = "http://localhost:8080"
SCOPE = "w_member_social"

print("\n" + "="*70)
print("LINKEDIN AUTHENTICATION - SUPER SIMPLE")
print("="*70)

# Step 1: Build auth URL
state = f"auth_{int(time.time())}"
auth_params = {
    'response_type': 'code',
    'client_id': CLIENT_ID,
    'redirect_uri': REDIRECT_URI,
    'scope': SCOPE,
    'state': state
}
auth_url = f"https://www.linkedin.com/oauth/v2/authorization?{urlencode(auth_params)}"

print("\n📋 STEP 1: Opening LinkedIn authorization...")
print("-"*70)

# Step 2: Open browser
webbrowser.open(auth_url)
print("✓ Browser opened!")
print("\nIf browser didn't open, copy this URL:")
print(auth_url)

# Step 3: Start server to capture code
print("\n📡 STEP 2: Waiting for authorization callback...")
print("-"*70)
print("Instructions:")
print("  1. LinkedIn page mein login karo")
print("  2. 'Allow' button click karo")
print("  3. Browser automatically redirect hoga")
print("-"*70)

auth_code = None
auth_error = None

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code, auth_error
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        
        if 'code' in params:
            auth_code = params['code'][0]
            print("\n✅ Authorization code received!")
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            html = """
            <html><body style="font-family:Arial;text-align:center;padding:50px;">
            <h1 style="color:#0077b5;">✓ Success!</h1>
            <p>Authorization complete. Close this window.</p>
            <script>setTimeout(() => window.close(), 2000);</script>
            </body></html>
            """
            self.wfile.write(html.encode())
        elif 'error' in params:
            auth_error = params.get('error', ['Unknown'])[0]
            print(f"\n❌ Error: {auth_error}")
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            html = f"<html><body><h1>Error: {auth_error}</h1></body></html>"
            self.wfile.write(html.encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        pass

server = HTTPServer(('localhost', 8080), Handler)
server.timeout = 180

try:
    while auth_code is None and auth_error is None:
        server.handle_request()
        time.sleep(0.1)
        
        # Check timeout
        if hasattr(server, '_start_time'):
            if time.time() - server._start_time > 180:
                print("\n⏱ Timeout!")
                break
        else:
            server._start_time = time.time()
except KeyboardInterrupt:
    print("\n\nCancelled")
finally:
    server.server_close()

if auth_error:
    print(f"\n❌ Authorization failed: {auth_error}")
    sys.exit(1)

if not auth_code:
    print("\n❌ No code received. Timeout ya cancel.")
    sys.exit(1)

# Step 4: Exchange code for token
print("\n🔄 STEP 3: Getting access token...")

try:
    import requests
    
    token_data = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }
    
    response = requests.post(
        "https://www.linkedin.com/oauth/v2/accessToken",
        data=token_data,
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
        timeout=30
    )
    
    if response.status_code == 200:
        result = response.json()
        access_token = result.get('access_token')
        expires_in = result.get('expires_in', 5184000)
        
        if access_token:
            # Save token
            token_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".linkedin_token.json")
            token_data = {
                'access_token': access_token,
                'expires_at': time.time() + expires_in,
                'created_at': datetime.now().isoformat()
            }
            
            with open(token_path, 'w') as f:
                json.dump(token_data, f, indent=2)
            
            print("\n" + "="*70)
            print("✅ AUTHENTICATION SUCCESSFUL!")
            print("="*70)
            print(f"\nAccess Token: {access_token[:30]}...")
            print(f"Expires in: {expires_in} seconds")
            print(f"\nToken saved to: {token_path}")
            print("\n📝 Now you can post to LinkedIn:")
            print('   python linkedin_post.py -m "Your message"')
            print("="*70)
        else:
            print(f"\n❌ No token in response: {result}")
    else:
        print(f"\n❌ Token request failed: {response.status_code}")
        print(f"Response: {response.text}")
        
except ImportError:
    print("\n❌ 'requests' library not installed")
    print("   Run: pip install requests")
except Exception as e:
    print(f"\n❌ Error: {e}")

print("\n" + "="*70)
input("Press Enter to exit...")

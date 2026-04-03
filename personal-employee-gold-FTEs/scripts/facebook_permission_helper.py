#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Facebook Permission Helper
Generates the URL to get the correct access token with all required permissions
"""

import os
import webbrowser

APP_ID = os.getenv('FACEBOOK_APP_ID', '1715548502768048')

print("\n" + "="*70)
print("  FACEBOOK PERMISSION HELPER")
print("="*70)

# Required permissions for our integration
REQUIRED_PERMISSIONS = [
    'pages_show_list',
    'pages_read_engagement',
    'pages_read_user_content',
    'pages_manage_posts',
    'pages_manage_engagement',
    'read_page_mailboxes'
]

print(f"""
📋 Your app needs these permissions to post and monitor Facebook:

{chr(10).join(f"   • {p}" for p in REQUIRED_PERMISSIONS)}

🔐 To get a new access token with all permissions:

1. Click this URL (or copy to browser):
   https://developers.facebook.com/tools/explorer/

2. Select your app: "Gold Tier FTE" (App ID: {APP_ID})

3. Click "Get Token" → "Get User Access Token"

4. Check ALL these permissions:
   ✓ pages_show_list
   ✓ pages_read_engagement
   ✓ pages_read_user_content
   ✓ pages_manage_posts
   ✓ pages_manage_engagement
   ✓ read_page_mailboxes

5. Click "Generate Token"

6. Facebook will ask you to authorize - click "Continue"

7. Copy the generated token

8. Update your .env file:
   FACEBOOK_ACCESS_TOKEN=<paste_new_token_here>

9. Also get your Page Access Token by querying: /me/accounts
   - Copy the "access_token" from the response (this never expires!)

10. Run the test again:
    python scripts\\test_facebook_api.py

{"="*70}
""")

# Generate direct link to Graph API Explorer
explorer_url = f"https://developers.facebook.com/tools/explorer/?app_id={APP_ID}"

print(f"\n🌐 Opening Graph API Explorer...")
print(f"   URL: {explorer_url}")

# Try to open browser
try:
    webbrowser.open(explorer_url)
    print("   → Browser opened! Follow the steps above.")
except:
    print("   → Copy the URL to your browser manually.")

print("\n" + "="*70 + "\n")

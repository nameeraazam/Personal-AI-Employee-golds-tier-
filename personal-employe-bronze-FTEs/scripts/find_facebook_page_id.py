#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Facebook Page ID Finder
Find the correct Page ID for your Facebook Page
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

ACCESS_TOKEN = os.getenv('FACEBOOK_ACCESS_TOKEN', '')

print("\n" + "="*60)
print("  FACEBOOK PAGE ID FINDER")
print("="*60)

if not ACCESS_TOKEN:
    print("❌ FACEBOOK_ACCESS_TOKEN not set in .env")
    exit(1)

# Query /me/accounts to find all pages you manage
print("\n📋 Querying /me/accounts to find your pages...\n")

url = "https://graph.facebook.com/v18.0/me/accounts"
params = {'access_token': ACCESS_TOKEN}

try:
    response = requests.get(url, params=params, timeout=30)
    data = response.json()

    if 'error' in data:
        print(f"❌ Error: {data['error']['message']}")
        print(f"\n💡 Your access token might be expired or invalid.")
        print(f"   Go to: https://developers.facebook.com/tools/explorer/")
        print(f"   1. Select your app")
        print(f"   2. Click 'Get Token' → 'Get User Access Token'")
        print(f"   3. Add permissions: pages_show_list, pages_read_engagement, pages_manage_posts")
        print(f"   4. Generate token and update .env")
    else:
        pages = data.get('data', [])
        if not pages:
            print("⚠️  No pages found. Make sure you admin at least one Facebook Page.")
        else:
            print(f"✅ Found {len(pages)} page(s) you manage:\n")
            for i, page in enumerate(pages, 1):
                print(f"   Page {i}:")
                print(f"   Name: {page.get('name', 'N/A')}")
                print(f"   ID: {page.get('id', 'N/A')}")
                print(f"   Access Token: {page.get('access_token', 'N/A')[:50]}...")
                print()
            
            print("="*60)
            print("  RECOMMENDED ACTION")
            print("="*60)
            print("\n📝 Update your .env file with:")
            print(f"\n   FACEBOOK_PAGE_ID={pages[0].get('id')}")
            print(f"   FACEBOOK_ACCESS_TOKEN={pages[0].get('access_token')}")
            print("\n💡 Use the page access_token (not user token) for production!")
            print("   Page tokens don't expire.")

except Exception as e:
    print(f"❌ Error: {e}")
    print("\n💡 Make sure your access token has 'pages_show_list' permission")

print("\n" + "="*60 + "\n")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Facebook API Connection Test
Test your Facebook Graph API credentials
"""

import os
import sys
import requests
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get credentials from .env
ACCESS_TOKEN = os.getenv('FACEBOOK_ACCESS_TOKEN', '')
PAGE_ID = os.getenv('FACEBOOK_PAGE_ID', '')
APP_ID = os.getenv('FACEBOOK_APP_ID', '')
APP_SECRET = os.getenv('FACEBOOK_APP_SECRET', '')
API_VERSION = os.getenv('FACEBOOK_API_VERSION', 'v18.0')

print("\n" + "="*60)
print("  FACEBOOK GRAPH API - CONNECTION TEST")
print("="*60)

# Check credentials
print("\n📋 Checking credentials...")

if not ACCESS_TOKEN:
    print("❌ FACEBOOK_ACCESS_TOKEN not set in .env")
    print("   → See FACEBOOK_SETUP.md for setup instructions")
    sys.exit(1)
else:
    print(f"✅ Access Token: {ACCESS_TOKEN[:20]}...")

if not PAGE_ID:
    print("❌ FACEBOOK_PAGE_ID not set in .env")
    print("   → Query /me/accounts in Graph API Explorer")
    sys.exit(1)
else:
    print(f"✅ Page ID: {PAGE_ID}")

if APP_ID:
    print(f"✅ App ID: {APP_ID}")
if APP_SECRET:
    print(f"✅ App Secret: {'*' * 20}")

# Test 1: Get Page Info
print("\n" + "="*60)
print("  TEST 1: Get Page Information")
print("="*60)

url = f"https://graph.facebook.com/{API_VERSION}/{PAGE_ID}"
params = {
    'access_token': ACCESS_TOKEN,
    'fields': 'name,about,category,followers_count'
}

try:
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    page_data = response.json()
    
    if 'error' in page_data:
        print(f"❌ Error: {page_data['error']['message']}")
    else:
        print(f"\n✅ Page Found!")
        print(f"   Name: {page_data.get('name', 'N/A')}")
        print(f"   Category: {page_data.get('category', 'N/A')}")
        print(f"   About: {page_data.get('about', 'N/A')[:100]}")
        if 'followers_count' in page_data:
            print(f"   Followers: {page_data['followers_count']:,}")
            
except requests.exceptions.RequestException as e:
    print(f"❌ Request failed: {e}")

# Test 2: Get Page Insights
print("\n" + "="*60)
print("  TEST 2: Get Page Insights")
print("="*60)

url = f"https://graph.facebook.com/{API_VERSION}/{PAGE_ID}/insights"
params = {
    'access_token': ACCESS_TOKEN,
    'metric': 'page_impressions,page_follows,page_post_engagements',
    'period': 'day'
}

try:
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    insights_data = response.json()
    
    if 'error' in insights_data:
        print(f"❌ Error: {insights_data['error']['message']}")
    else:
        print(f"\n✅ Insights Retrieved!")
        for metric in insights_data.get('data', []):
            value = metric.get('values', [{}])[0].get('value', 0)
            print(f"   {metric['name']}: {value:,}")
            
except requests.exceptions.RequestException as e:
    print(f"❌ Request failed: {e}")

# Test 3: Get Recent Posts
print("\n" + "="*60)
print("  TEST 3: Get Recent Posts")
print("="*60)

url = f"https://graph.facebook.com/{API_VERSION}/{PAGE_ID}/posts"
params = {
    'access_token': ACCESS_TOKEN,
    'limit': 3,
    'fields': 'message,created_time,likes.summary(true),comments.summary(true)'
}

try:
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    posts_data = response.json()
    
    if 'error' in posts_data:
        print(f"❌ Error: {posts_data['error']['message']}")
    else:
        print(f"\n✅ Recent Posts Retrieved!")
        posts = posts_data.get('data', [])
        if not posts:
            print("   No posts found")
        else:
            for i, post in enumerate(posts, 1):
                message = post.get('message', 'No message')[:80]
                created = post.get('created_time', 'Unknown')
                likes = post.get('likes', {}).get('summary', {}).get('total_count', 0)
                comments = post.get('comments', {}).get('summary', {}).get('total_count', 0)
                print(f"\n   Post {i}:")
                print(f"   Date: {created}")
                print(f"   Message: {message}...")
                print(f"   Likes: {likes:,} | Comments: {comments:,}")
            
except requests.exceptions.RequestException as e:
    print(f"❌ Request failed: {e}")

# Test 4: Get Comments (for monitoring test)
print("\n" + "="*60)
print("  TEST 4: Get Recent Comments (Monitoring Test)")
print("="*60)

url = f"https://graph.facebook.com/{API_VERSION}/{PAGE_ID}/feed"
params = {
    'access_token': ACCESS_TOKEN,
    'limit': 1,
    'fields': 'comments.limit(5){message,from,created_time}'
}

try:
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    feed_data = response.json()
    
    if 'error' in feed_data:
        print(f"❌ Error: {feed_data['error']['message']}")
    else:
        print(f"\n✅ Comments Access Test!")
        posts = feed_data.get('data', [])
        if posts and 'comments' in posts[0]:
            comments = posts[0]['comments'].get('data', [])
            print(f"   Found {len(comments)} recent comments")
            for comment in comments[:3]:
                sender = comment.get('from', {}).get('name', 'Unknown')
                message = comment.get('message', 'No message')[:60]
                print(f"   - {sender}: {message}...")
        else:
            print("   No comments found (this is normal if page has no posts)")
            
except requests.exceptions.RequestException as e:
    print(f"❌ Request failed: {e}")

# Final Summary
print("\n" + "="*60)
print("  TEST SUMMARY")
print("="*60)
print("\n✅ All Facebook API tests completed!")
print("\n📊 Your credentials are working correctly.")
print("\n🚀 Next steps:")
print("   1. Run: python integrations\\facebook_integration.py --monitor")
print("   2. Or: python scripts\\gold_tier_orchestrator.py --start")
print("\n📖 For detailed setup, see: FACEBOOK_SETUP.md")
print("\n" + "="*60 + "\n")

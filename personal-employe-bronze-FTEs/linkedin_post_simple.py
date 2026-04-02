#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple LinkedIn Poster - Just paste your access token and post!
No OAuth flow needed if you already have a token.
"""

import requests
import json

# ============================================
# STEP 1: PASTE YOUR ACCESS TOKEN HERE
# ============================================
ACCESS_TOKEN = "PASTE_YOUR_LINKEDIN_ACCESS_TOKEN_HERE"

# ============================================
# STEP 2: Write your post message
# ============================================
MESSAGE = "Hello LinkedIn! This is my automated post."

# ============================================
# Don't edit below this line
# ============================================

def post_to_linkedin(token, message):
    """Post to LinkedIn API"""
    
    url = "https://api.linkedin.com/v2/shares"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Restli-Protocol-Version": "2.0.0",
        "Content-Type": "application/json"
    }
    
    data = {
        "text": {
            "text": message
        },
        "visibility": "PUBLIC"
    }
    
    print("📤 Posting to LinkedIn...")
    print(f"Message: {message}")
    print("-" * 50)
    
    try:
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS!")
            print(f"Post ID: {result.get('id', 'N/A')}")
            print(f"Status: {result.get('status', 'PUBLISHED')}")
            return True
        else:
            print("❌ FAILED!")
            print(f"Status Code: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    if ACCESS_TOKEN == "PASTE_YOUR_LINKEDIN_ACCESS_TOKEN_HERE":
        print("❌ ERROR: You need to add your access token!")
        print("\n📋 How to get access token:")
        print("  1. Run: python linkedin_auth_new.py")
        print("  2. Complete the authorization")
        print("  3. Token will be saved to .linkedin_token.json")
        print("  4. Copy the token and paste it in this script")
    else:
        post_to_linkedin(ACCESS_TOKEN, MESSAGE)

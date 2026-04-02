# Facebook Integration Setup Guide - COMPLETE

## ⚠️ IMPORTANT: You Need to Update Your Access Token

Your current access token is missing required permissions. Follow these steps:

---

## 🔐 Step-by-Step: Get Correct Access Token (10 minutes)

### Step 1: Open Graph API Explorer

**URL:** https://developers.facebook.com/tools/explorer/?app_id=1715548502768048

The browser should already be open from running the permission helper script.

---

### Step 2: Select Your App

1. At the top of the page, click the app dropdown
2. Select **"Gold Tier FTE"** (App ID: 1715548502768048)

---

### Step 3: Generate Access Token with ALL Permissions

1. Click **"Get Token"** button (top of page)
2. Select **"Get User Access Token"**
3. A popup will appear - click **"Advanced Options"** at bottom
4. **Check ALL these permissions:**

   ```
   ☑ pages_show_list
   ☑ pages_read_engagement  
   ☑ pages_read_user_content
   ☑ pages_manage_posts
   ☑ pages_manage_engagement
   ☑ read_page_mailboxes
   ```

5. Click **"Generate Access Token"**

---

### Step 4: Authorize the App

1. Facebook will show a dialog: "[Your App] would like to access..."
2. Review the permissions
3. Click **"Continue"** or **"Allow"**
4. If asked, log in to your Facebook account
5. Select your profile/page if prompted

---

### Step 5: Copy the Access Token

1. After authorization, the access token field will be populated
2. **Copy the entire token** (it's a long string starting with `EAAY...`)
3. This is your **User Access Token**

---

### Step 6: Get Page Access Token (RECOMMENDED - Never Expires!)

1. In the Graph API Explorer query box at the top, type:
   ```
   /me/accounts
   ```
2. Click **"Submit"** button
3. You'll see a response like:
   ```json
   {
     "data": [
       {
         "name": "Syeda",
         "id": "1096004620255520",
         "access_token": "EAAYYSEMaObABRMAX2gWud1AR9kCQuDz5GZCilZBBwEZCcHUtb..."
       }
     ]
   }
   ```
4. **Copy the `access_token` value** from this response
5. This is your **Page Access Token** - it NEVER expires! ✅

---

### Step 7: Update Your .env File

1. Open: `C:\gold tier 5\gold tier 5\personal-employe-bronze-FTEs\.env`

2. Replace the `FACEBOOK_ACCESS_TOKEN` and `FACEBOOK_PAGE_ID` with:
   ```bash
   FACEBOOK_ACCESS_TOKEN=<paste_the_page_access_token_from_step_6>
   FACEBOOK_PAGE_ID=1096004620255520
   ```

3. Save the file

---

### Step 8: Test Your Connection

Open a new terminal and run:

```bash
cd "C:\gold tier 5\gold tier 5\personal-employe-bronze-FTEs"
"C:\Users\Dell\AppData\Local\Programs\Python\Python313\python.exe" scripts\test_facebook_api.py
```

**Success!** You should see:
```
✅ Page Found!
   Name: Syeda
   Category: ...
```

---

## 🚀 How to Use Facebook Integration

### Post to Facebook

```bash
"C:\Users\Dell\AppData\Local\Programs\Python\Python313\python.exe" integrations\facebook_integration.py --post "Your message here"
```

**Example with link:**
```bash
"C:\Users\Dell\AppData\Local\Programs\Python\Python313\python.exe" integrations\facebook_integration.py --post "Check out our new product!" --link "https://example.com"
```

---

### Monitor Comments & Messages

```bash
"C:\Users\Dell\AppData\Local\Programs\Python\Python313\python.exe" integrations\facebook_integration.py --monitor
```

This will:
- Check for new comments every 120 seconds
- Check for new messages every 120 seconds
- Detect sales leads automatically
- Create action items in `Needs_Action/` folder
- Auto-respond if enabled

**Stop monitoring:** Press `Ctrl+C`

---

### Get Page Insights

```bash
"C:\Users\Dell\AppData\Local\Programs\Python\Python313\python.exe" integrations\facebook_integration.py --insights
```

Shows:
- Page impressions
- Post engagements
- Page likes and follows

---

## 📋 Quick Reference

### File Locations

```
personal-employe-bronze-FTEs/
├── .env                              # Your credentials (UPDATE THIS!)
├── integrations/
│   └── facebook_integration.py       # Main Facebook integration
└── scripts/
    ├── test_facebook_api.py          # Test connection
    ├── find_facebook_page_id.py      # Find your page ID
    └── facebook_permission_helper.py # Get correct permissions
```

### Commands

| Command | Description |
|---------|-------------|
| `python scripts\test_facebook_api.py` | Test API connection |
| `python integrations\facebook_integration.py --post "msg"` | Post to Facebook |
| `python integrations\facebook_integration.py --monitor` | Monitor comments/messages |
| `python integrations\facebook_integration.py --insights` | Get page analytics |
| `python scripts\find_facebook_page_id.py` | Find your page ID |

---

## 🐛 Troubleshooting

### Error: "Unsupported get request" or "Object does not exist"

**Solution:** Your Page ID is wrong or token doesn't have permissions
- Run: `python scripts\find_facebook_page_id.py`
- Update `.env` with correct Page ID and Page Access Token

### Error: "Missing permissions"

**Solution:** Your token needs more permissions
- Run: `python scripts\facebook_permission_helper.py`
- Follow steps to generate token with all required permissions

### Error: "Invalid access token"

**Solution:** Token expired or was revoked
- Generate a new token following Step 1-6 above
- Use Page Access Token (doesn't expire)

### No comments/messages detected

**Solution:** This is normal if your page has no activity
- Post something to your page first
- Ask a friend to comment or send a message
- The monitor checks every 120 seconds by default

---

## 🔐 Security Notes

- ✅ **Never commit `.env` to Git** (already in `.gitignore`)
- ✅ **Use Page Access Token** for production (never expires)
- ✅ Keep your App Secret private
- ✅ Regenerate tokens if compromised

---

## ✅ Checklist

Before using Facebook integration:

- [ ] Generated access token with all 6 permissions
- [ ] Got Page Access Token from `/me/accounts`
- [ ] Updated `.env` with correct token and Page ID
- [ ] Tested connection with `test_facebook_api.py`
- [ ] Successfully posted a test message

**All done?** You're ready to use Facebook integration! 🎉

---

*Gold Tier FTE - Facebook Integration*

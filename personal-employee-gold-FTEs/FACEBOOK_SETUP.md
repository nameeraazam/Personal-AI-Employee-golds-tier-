# Facebook Graph API Setup Guide - API ONLY

## ⚡ Quick Setup (5 minutes)

### Step 1: Open Facebook Graph API Explorer

**URL:** https://developers.facebook.com/tools/explorer/

---

### Step 2: Create/Select App

1. Click **"Add a New App"** (if you don't have one)
2. Select **"Business"** as app type
3. Fill in:
   - **App Name:** `Gold Tier FTE Integration`
   - **App Contact Email:** Your email
4. Click **"Create App"**

---

### Step 3: Add Required Permissions

Click **"Add a Permission"** and search for each:

| # | Permission | Why We Need It |
|---|------------|----------------|
| 1 | `pages_show_list` | See pages you manage |
| 2 | `read_page_mailboxes` | Read page messages |
| 3 | `pages_read_engagement` | Read posts, comments, insights |
| 4 | `pages_read_user_content` | Read user content on pages |
| 5 | `pages_manage_posts` | Create and manage posts |
| 6 | `pages_manage_engagement` | Manage comments and reactions |

---

### Step 4: Generate Access Token

1. Click **"Get Token"** button (top of page)
2. Select **"Get User Access Token"**
3. **Check all 6 permissions** you just added
4. Click **"Generate Token"**
5. Facebook will show authorization dialog
6. Click **"Continue as [Your Name]"**
7. Click **"Done"**

✅ **Copy the Access Token** that appears in the text box

---

### Step 5: Get Page ID

1. In the query box at top, type: `/me/accounts`
2. Click **"Submit"**
3. You'll see a response like:

```json
{
  "data": [
    {
      "name": "Your Page Name",
      "id": "123456789012345",
      "access_token": "page_access_token_xyz"
    }
  ]
}
```

✅ **Copy the `id` value** - this is your **PAGE_ID**  
✅ **Copy the `access_token` value** - this is your **PAGE_ACCESS_TOKEN** (never expires!)

---

### Step 6: Get App ID and Secret

1. Go to: https://developers.facebook.com/apps/
2. Click on your app
3. Go to **Settings → Basic**
4. Copy **App ID**
5. Click **"Show"** next to App Secret and copy it

---

### Step 7: Add to .env File

1. Copy `.env.example` to `.env`:
   ```bash
   copy .env.example .env
   ```

2. Edit `.env` and add your credentials:
   ```bash
   FACEBOOK_ACCESS_TOKEN=EAAG...your_token_here
   FACEBOOK_PAGE_ID=123456789012345
   FACEBOOK_APP_ID=your_app_id
   FACEBOOK_APP_SECRET=your_app_secret
   ```

3. Save the file

---

### Step 8: Test Connection

Run this command to test:

```bash
python integrations\facebook_integration.py --insights
```

**Success!** You should see your page insights like:

```json
{
  "data": [
    {
      "name": "page_impressions",
      "values": [{"value": 1234}]
    }
  ]
}
```

---

### Step 9: Start Facebook Monitor

```bash
# Monitor Facebook only
python integrations\facebook_integration.py --monitor

# Or start full Gold Tier
python scripts\gold_tier_orchestrator.py --start
```

---

## 📝 Quick Reference

### Test Commands

```bash
# Post to Facebook
python integrations\facebook_integration.py --post "Hello from Gold Tier!"

# Get page insights
python integrations\facebook_integration.py --insights

# Monitor comments/messages
python integrations\facebook_integration.py --monitor

# Create ad campaign
python integrations\facebook_integration.py --ad-campaign "Summer Sale" --budget 50
```

### File Locations

```
personal-employee-gold-FTEs/
├── .env                          # Your credentials (create this)
├── .env.example                  # Template
├── integrations/
│   └── facebook_integration.py   # Facebook API code
└── scripts/
    └── requirements.txt           # Python dependencies
```

---

## 🔐 Important Notes

### Token Types

| Token Type | Expires | Use For |
|------------|---------|---------|
| **User Token** | 1-2 hours | Testing |
| **Page Token** | **Never** | **Production** ✅ |
| **Long-lived Token** | 60 days | Extended testing |

**Use the Page Access Token** (from `/me/accounts` query) - it never expires!

### Required Permissions Summary

```
pages_show_list
read_page_mailboxes
pages_read_engagement
pages_read_user_content
pages_manage_posts
pages_manage_engagement
```

### Security

- ⚠️ **Never commit `.env` to Git** (already in `.gitignore`)
- ⚠️ Keep your App Secret private
- ⚠️ Use Page Token for production (doesn't expire)

---

## 🐛 Troubleshooting

### Error: "No Facebook API token found"

**Solution:** Add `FACEBOOK_ACCESS_TOKEN` to `.env`

### Error: "Unsupported get request"

**Solution:** Make sure you're using Page Token, not User Token

### Error: "Missing permissions"

**Solution:** Add the required permission in App Dashboard and regenerate token

### Error: "Page not found"

**Solution:** Make sure you're an admin of the Facebook Page

---

## 🔗 Useful Links

- **Graph API Explorer:** https://developers.facebook.com/tools/explorer/
- **App Dashboard:** https://developers.facebook.com/apps/
- **Access Token Debugger:** https://developers.facebook.com/tools/debug/access_token/
- **Graph API Docs:** https://developers.facebook.com/docs/graph-api

---

## ✅ Checklist

Before running Facebook integration:

- [ ] Created Facebook App
- [ ] Added all 6 required permissions
- [ ] Generated User Access Token
- [ ] Got Page ID from `/me/accounts`
- [ ] Got Page Access Token
- [ ] Got App ID and Secret
- [ ] Created `.env` file with credentials
- [ ] Tested with `--insights` command

**All done?** You're ready to use Facebook integration! 🎉

---

*Facebook Integration - Gold Tier FTE (API Only)*

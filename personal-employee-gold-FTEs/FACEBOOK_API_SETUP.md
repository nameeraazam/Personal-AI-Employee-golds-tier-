# Facebook Graph API Configuration - Complete ✅

## What Changed

Facebook integration has been updated to use **Graph API ONLY** - no browser automation, no Playwright needed!

---

## ✅ Benefits of API-Only Approach

| Feature | Before (Browser) | After (API) |
|---------|------------------|-------------|
| **Speed** | Slow (browser launch) | Fast (direct API) |
| **Reliability** | Can break with UI changes | Stable API |
| **Resources** | Heavy (Chromium browser) | Lightweight |
| **Dependencies** | Playwright required | Only `requests` |
| **Token Expiry** | Session expires | Page token never expires |
| **Production Ready** | ⚠️ Testing only | ✅ Yes |

---

## 📦 Updated Files

### 1. facebook_integration.py
- ❌ Removed: `FacebookBrowserAutomation` class
- ❌ Removed: Playwright imports
- ❌ Removed: Browser fallback code
- ✅ Updated: `post_update()` - API only
- ✅ Updated: `start_monitoring()` - API only with validation

### 2. requirements.txt
- ❌ Removed: `playwright>=1.40.0`
- ✅ Kept: `requests>=2.31.0`
- ✅ Kept: `python-dotenv>=1.0.0`

### 3. .env.example
- ❌ Removed: `FACEBOOK_EMAIL`, `FACEBOOK_PASSWORD`
- ✅ Added: Clear setup instructions
- ✅ Added: `FACEBOOK_ACCESS_TOKEN`, `FACEBOOK_PAGE_ID`
- ✅ Added: `FACEBOOK_APP_ID`, `FACEBOOK_APP_SECRET`

### 4. New Files Created
- ✅ `FACEBOOK_SETUP.md` - Step-by-step setup guide
- ✅ `scripts/test_facebook_api.py` - Connection test script

---

## 🚀 Quick Start

### Step 1: Install Dependencies

```bash
cd personal-employee-gold-FTEs
pip install -r scripts\requirements.txt
```

**Note:** No need to install Playwright anymore!

### Step 2: Configure Facebook API

1. Open: https://developers.facebook.com/tools/explorer/
2. Create/select your app
3. Add these 6 permissions:
   - `pages_show_list`
   - `read_page_mailboxes`
   - `pages_read_engagement`
   - `pages_read_user_content`
   - `pages_manage_posts`
   - `pages_manage_engagement`
4. Click "Get Token" → "Get User Access Token"
5. Generate token
6. Query `/me/accounts` to get Page ID and Page Token
7. Copy `.env.example` to `.env`
8. Add your credentials to `.env`

### Step 3: Test Connection

```bash
python scripts\test_facebook_api.py
```

**Expected output:**
```
✅ Access Token: EAAG...
✅ Page ID: 123456789012345
✅ Page Found!
   Name: Your Page Name
✅ Insights Retrieved!
✅ Recent Posts Retrieved!
✅ All Facebook API tests completed!
```

### Step 4: Start Monitoring

```bash
# Facebook only
python integrations\facebook_integration.py --monitor

# Full Gold Tier (with Odoo)
python scripts\gold_tier_orchestrator.py --start
```

---

## 📝 Required Credentials

Add these to your `.env` file:

```bash
# Get from Graph API Explorer
FACEBOOK_ACCESS_TOKEN=EAAG...your_page_access_token
FACEBOOK_PAGE_ID=your_page_id

# Get from App Dashboard
FACEBOOK_APP_ID=your_app_id
FACEBOOK_APP_SECRET=your_app_secret
```

---

## 🔑 Token Types Explained

### User Access Token
- **Expires:** 1-2 hours
- **Use:** Testing only
- **Get:** "Get Token" → "Get User Access Token"

### Page Access Token ⭐ (Recommended)
- **Expires:** **NEVER**
- **Use:** Production
- **Get:** Query `/me/accounts` and copy the `access_token` field

### Long-lived User Token
- **Expires:** 60 days
- **Use:** Extended testing
- **Get:** Use Access Token Debugger to extend

**Use Page Access Token for production!**

---

## 🧪 Test Commands

```bash
# Test connection
python scripts\test_facebook_api.py

# Get page insights
python integrations\facebook_integration.py --insights

# Post to Facebook
python integrations\facebook_integration.py --post "Hello from API!"

# Monitor comments/messages
python integrations\facebook_integration.py --monitor

# Create ad campaign
python integrations\facebook_integration.py --ad-campaign "Summer Sale" --budget 50
```

---

## 📖 Documentation

- **FACEBOOK_SETUP.md** - Detailed setup guide
- **README.md** - Full project documentation
- **Skills/SKILL_Gold_Tier_Integration.md** - Technical reference

---

## 🐛 Troubleshooting

### Error: "No Facebook API token found"

**Solution:**
```bash
# Check .env file exists
dir .env

# Check FACEBOOK_ACCESS_TOKEN is set
findstr "FACEBOOK_ACCESS_TOKEN" .env
```

### Error: "Invalid access token"

**Solution:**
1. Token may have expired
2. Get Page Token from `/me/accounts` query (doesn't expire)
3. Update `.env` with new token

### Error: "Missing permissions"

**Solution:**
1. Go to Graph API Explorer
2. Add missing permission
3. Regenerate token
4. Update `.env`

---

## ✅ Checklist

Before running:

- [ ] Dependencies installed (`pip install -r scripts\requirements.txt`)
- [ ] Facebook App created
- [ ] All 6 permissions added
- [ ] User Access Token generated
- [ ] Page ID obtained from `/me/accounts`
- [ ] Page Access Token obtained (recommended)
- [ ] `.env` file created with credentials
- [ ] Connection tested with `test_facebook_api.py`

---

## 🎯 What You Get

With Facebook Graph API integration:

- ✅ Post to Facebook Page automatically
- ✅ Monitor comments for sales leads
- ✅ Monitor page messages
- ✅ Auto-respond to common inquiries
- ✅ Get page insights and analytics
- ✅ Create and manage ad campaigns
- ✅ Sync leads to Odoo CRM
- ✅ Cross-platform posting (with LinkedIn)

---

## 📞 Need Help?

1. **Read:** `FACEBOOK_SETUP.md` for detailed setup
2. **Test:** Run `python scripts\test_facebook_api.py`
3. **Check:** Logs in `AI_Employee_Vault/Logs/facebook.log`

---

**Facebook Integration is now API-ONLY and production-ready! 🎉**

No browser automation. No Playwright. Just clean, fast API calls.

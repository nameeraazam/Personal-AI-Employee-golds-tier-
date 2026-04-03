# Scripts Documentation

## Overview

This directory contains the main automation scripts for the Gold Tier FTE.

## Main Scripts

### gold_tier_orchestrator.py
**Purpose**: Central orchestrator for all Gold Tier automation

**Usage**:
```bash
# Start all services
python gold_tier_orchestrator.py --start

# Check status
python gold_tier_orchestrator.py --status

# Post to all platforms
python gold_tier_orchestrator.py --post "Your message" --link "https://example.com"

# Start Odoo
python gold_tier_orchestrator.py --odoo-start

# Test connections
python gold_tier_orchestrator.py --test-connections
```

**Features**:
- Unified monitoring of all platforms
- Cross-platform posting
- Lead synchronization to Odoo
- Centralized logging

### linkedin_watcher.py
**Purpose**: Monitor LinkedIn for messages, connections, and notifications

**Usage**:
```bash
python linkedin_watcher.py
```

**Features**:
- Checks every 60 seconds
- Detects sales leads via keywords
- Creates action files in Needs_Action/
- Session persistence for auto-login

### facebook_permission_helper.py
**Purpose**: Help generate Facebook access token URLs

**Usage**:
```bash
python facebook_permission_helper.py
```

**Features**:
- Shows required permissions
- Opens Graph API Explorer
- Step-by-step token generation guide

### find_facebook_page_id.py
**Purpose**: Find your Facebook Page ID programmatically

**Usage**:
```bash
python find_facebook_page_id.py
```

**Features**:
- Queries /me/accounts endpoint
- Lists all pages you manage
- Shows page IDs and access tokens

### test_facebook_api.py
**Purpose**: Test Facebook Graph API connection

**Usage**:
```bash
python test_facebook_api.py
```

**Features**:
- Validates access token
- Tests page posting capability
- Shows page insights

### facebook_token_setup.py
**Purpose**: Interactive Facebook token setup wizard

**Usage**:
```bash
python facebook_token_setup.py
```

**Features**:
- Guides through OAuth flow
- Saves token to .env
- Validates permissions

## Dependencies

Install all dependencies:
```bash
pip install -r requirements.txt
```

See `requirements.txt` for the complete list of packages.

## Configuration

All scripts read credentials from the `.env` file in the project root.

Make sure `.env` exists and contains:
- LinkedIn credentials
- Facebook access token and page ID
- Odoo credentials (if using)

## Logging

All scripts log activity to:
- Console (real-time)
- `AI_Employee_Vault/Logs/` (persistent)

Check logs for troubleshooting.

## Error Handling

Scripts include error handling for:
- Network failures
- API rate limits
- Authentication issues
- Missing credentials

Most errors are logged and the script continues running.

---

*Part of AI Employee Gold Tier FTE*

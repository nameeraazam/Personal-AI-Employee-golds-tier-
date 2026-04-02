---
created: 2026-03-09
version: 1.0
status: Active
type: skill
category: social_media
---

# 💼 LinkedIn Post Skill

## Overview

Autonomous skill for posting updates to LinkedIn using the LinkedIn API v2. This skill enables AI employees to share company updates, achievements, job postings, and professional content automatically.

---

## Purpose

- Post professional updates to LinkedIn company/personal profiles
- Share company news, achievements, and announcements
- Automate social media presence management
- Maintain consistent professional online presence

---

## Capabilities

| Feature | Description |
|---------|-------------|
| **Text Posts** | Share text-based updates (up to 3000 characters) |
| **OAuth 2.0 Auth** | Secure authentication with LinkedIn API |
| **Session Management** | Persistent token storage for reuse |
| **Error Handling** | Graceful handling of API rate limits and errors |
| **Logging** | All posts logged to vault for audit trail |

---

## Requirements

### API Credentials

1. **LinkedIn Developer Account**: Required to create LinkedIn app
2. **App Registration**: Register at [LinkedIn Developer Portal](https://www.linkedin.com/developers/)
3. **Required Permissions**:
   - `w_member_social` - Post to member profile
   - `r_basicprofile` - Read basic profile (optional)

### Credentials Setup

1. Go to [LinkedIn Developer Portal](https://www.linkedin.com/developers/)
2. Create a new app or select existing app
3. Navigate to **Auth** tab
4. Note down:
   - **Client ID**
   - **Client Secret**
5. Set **Redirect URL**: `http://localhost:8080`
6. Save credentials to `credentials.json` or `.env`

---

## Usage

### First-Time Authentication

```bash
python linkedin_post.py --auth
```

This will:
1. Open browser for OAuth authorization
2. Prompt you to log in to LinkedIn
3. Grant permissions to the app
4. Save access token for future use

### Post Update

```bash
python linkedin_post.py --message "Your professional update here"
```

### With Environment Variables

```bash
# Set in .env file
LINKEDIN_CLIENT_ID=your_client_id
LINKEDIN_CLIENT_SECRET=your_client_secret
LINKEDIN_ACCESS_TOKEN=your_access_token  # After first auth

# Then run
python linkedin_post.py --message "Your update"
```

---

## API Endpoints

### Post to LinkedIn (API v2)

```http
POST https://api.linkedin.com/v2/shares
Authorization: Bearer {access_token}
X-Restli-Protocol-Version: 2.0.0
```

### Request Body

```json
{
  "text": {
    "text": "Your message content here"
  },
  "visibility": "PUBLIC"
}
```

---

## File Structure

```
Skills/
├── SKILL_LinkedIn_Post.md      # This documentation
└── linkedin_post.py            # LinkedIn posting script

Root/
├── credentials.json            # OAuth credentials
├── .env                        # Environment variables (optional)
└── AI_Employee_Vault/
    └── Logs/
        └── linkedin_posts.log  # Post activity log
```

---

## Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `message_text` | Yes | The content to post (max 3000 characters) |
| `visibility` | No | Post visibility: PUBLIC, CONNECTIONS, PRIVATE (default: PUBLIC) |
| `access_token` | Conditional | OAuth token (auto-retrieved if stored) |

---

## Response Format

### Success

```json
{
  "id": "urn:li:share:1234567890",
  "status": "PUBLISHED"
}
```

### Error

```json
{
  "serviceErrorCode": "INVALID_REQUEST",
  "message": "Error message",
  "status": 400
}
```

---

## Integration Examples

### Standalone Usage

```python
from linkedin_post import LinkedInPoster

poster = LinkedInPoster(
    client_id="your_client_id",
    client_secret="your_client_secret"
)

# Authenticate first time
poster.authenticate()

# Post update
result = poster.post_update("Exciting company news! We're hiring...")
print(f"Post ID: {result['id']}")
```

### As Part of AI Employee

```python
# In your AI employee script
from linkedin_post import LinkedInPoster

def announce_achievement(achievement: str):
    poster = LinkedInPoster.from_env()
    message = f"🎉 Company Update: {achievement}"
    result = poster.post_update(message)
    log_post_to_vault(result)
```

---

## Rate Limits

| Limit | Value |
|-------|-------|
| Posts per day | 200 (per member) |
| Requests per second | 100 |
| Character limit | 3000 characters |

---

## Troubleshooting

### Issue: Token Expired

**Solution**: Re-run authentication
```bash
python linkedin_post.py --auth
```

### Issue: Permission Denied

**Solution**: Ensure app has `w_member_social` permission in LinkedIn Developer Portal

### Issue: Invalid Credentials

**Solution**: Verify Client ID and Secret in credentials.json

---

## Security Notes

- Store credentials securely in `.env` or encrypted storage
- Never commit access tokens to version control
- Rotate tokens periodically
- Use environment variables for production deployments

---

## Related Skills

- [`SKILL_Gmail_Monitor.md`](./SKILL_Gmail_Monitor.md) - Email monitoring
- [`SKILL_WhatsApp_Watcher.md`](./SKILL_WhatsApp_Watcher.md) - WhatsApp message monitoring
- [`SKILL_Twitter_Post.md`](./SKILL_Twitter_Post.md) - Twitter/X posting

---

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-03-09 | Initial skill documentation |

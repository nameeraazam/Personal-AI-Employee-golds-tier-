# LinkedIn Post Skill

## Overview

This skill enables posting to LinkedIn via the LinkedIn API v2.

## When to Use

- Sharing company updates
- Posting job opportunities
- Sharing industry insights
- Cross-posting from Facebook
- Announcing product updates

## Setup

1. **Get LinkedIn Developer Credentials**:
   - Go to https://www.linkedin.com/developers/
   - Create a new app
   - Get Client ID and Client Secret
   - Add to `.env` file

2. **Authenticate** (First Time Only):
   ```bash
   python linkedin_post.py --auth
   ```

3. **Post an Update**:
   ```bash
   python linkedin_post.py -m "Your professional update here"
   ```

## API Details

### Endpoint
```
POST https://api.linkedin.com/v2/shares
```

### Required Scope
- `w_member_social`

### Request Format
```json
{
  "text": {
    "text": "Your message here"
  },
  "visibility": "PUBLIC"
}
```

### Response
```json
{
  "id": "urn:li:share:1234567890",
  "status": "PUBLISHED"
}
```

## Best Practices

1. **Message Length**: Keep under 3000 characters
2. **Professional Tone**: LinkedIn is a professional network
3. **Include Hashtags**: 3-5 relevant hashtags
4. **Add Links**: Include relevant links when appropriate
5. **Timing**: Post during business hours for best engagement

## Examples

### Simple Text Post
```bash
python linkedin_post.py -m "Excited to announce our new AI-powered automation platform! #AI #Automation #Innovation"
```

### Post with Link
```python
from linkedin_post import LinkedInPoster

poster = LinkedInPoster.from_env()
poster.authenticate()
result = poster.post_update(
    "Check out our latest blog post on AI automation!",
    visibility="PUBLIC"
)
```

### Check Profile
```bash
python linkedin_post.py --profile
```

## Error Handling

### Common Errors

**No Access Token**:
```
No access token. Run 'python linkedin_post.py --auth' first.
```
**Solution**: Run authentication flow.

**Token Expired**:
```
Token exchange failed
```
**Solution**: Re-authenticate.

**Message Too Long**:
```
Message text exceeds 3000 character limit
```
**Solution**: Shorten your message.

**Missing Credentials**:
```
LINKEDIN_CLIENT_ID not found!
```
**Solution**: Check `.env` file.

## Integration

This skill integrates with:
- Gold Tier Orchestrator
- Cross-platform posting
- Lead detection and tracking

---

*Part of AI Employee Gold Tier FTE*

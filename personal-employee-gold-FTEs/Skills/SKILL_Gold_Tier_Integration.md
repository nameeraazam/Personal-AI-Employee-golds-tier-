---
created: 2026-03-31
version: 1.0
status: Active
type: skill
category: enterprise_integration
tier: gold
---

# 🏆 Gold Tier FTE - Complete Integration Skill

## Overview

The **Gold Tier FTE** is an advanced autonomous AI employee system that integrates:
- **Facebook** for social media automation
- **Odoo ERP** for CRM, sales, and inventory management
- **Unified Orchestrator** for cross-platform automation

This skill enables AI agents to manage complete business workflows from social media engagement to sales pipeline management.

---

## Purpose

- Automate Facebook Page management and engagement
- Monitor and respond to customer inquiries automatically
- Create and manage leads in Odoo CRM from social media
- Generate quotations and sales orders automatically
- Sync data across all platforms seamlessly
- Provide unified monitoring and reporting

---

## Capabilities

| Feature | Description |
|---------|-------------|
| **Facebook Posting** | Post updates, links, and photos to Facebook Pages |
| **Facebook Monitoring** | Monitor comments, messages, and engagement |
| **Auto-Response** | Automatic responses to common inquiries |
| **Lead Detection** | Identify sales leads from keywords |
| **Odoo CRM** | Create and manage leads and opportunities |
| **Odoo Sales** | Generate quotations and sales orders |
| **Odoo Inventory** | Manage products and stock levels |
| **Cross-Platform Sync** | Sync leads across LinkedIn, Facebook, and Odoo |
| **Docker Deployment** | One-command Odoo ERP deployment |

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│              Gold Tier Orchestrator                      │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   LinkedIn   │  │   Facebook   │  │     Odoo     │  │
│  │   (Silver)   │  │  Integration │  │  Integration │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │
│         │                 │                 │           │
│         └─────────────────┼─────────────────┘           │
│                           │                             │
│                  ┌────────▼────────┐                    │
│                  │  Lead Sync &    │                    │
│                  │  Automation     │                    │
│                  └────────┬────────┘                    │
└───────────────────────────┼─────────────────────────────┘
                            │
                  ┌─────────▼──────────┐
                  │  AI Employee Vault │
                  │  (Logging & Stats) │
                  └────────────────────┘
```

---

## Requirements

### System Requirements

| Component | Requirement |
|-----------|-------------|
| **Python** | 3.8 or higher |
| **Docker** | Docker Desktop 20+ |
| **RAM** | 4GB minimum (8GB recommended) |
| **Disk** | 5GB free space |

### API Credentials

#### Facebook
- Facebook Developer Account
- Facebook App with Page permissions
- Page Access Token

#### Odoo
- Self-hosted via Docker (no external API needed)
- Or Odoo.sh / Odoo Online subscription

---

## Usage

### Quick Start

```bash
# 1. Setup
cd personal-employee-gold-FTEs
setup.bat

# 2. Configure credentials
# Edit .env file with your credentials

# 3. Start Odoo (optional)
docker-compose -f odoo-docker\docker-compose.yml up -d

# 4. Run orchestrator
run_gold_tier.bat
```

### Programmatic Usage

#### Post to Facebook

```python
from integrations.facebook_integration import FacebookIntegration

fb = FacebookIntegration()

# Post update
result = fb.post_update(
    message="Exciting company news!",
    link="https://example.com",
    photo_url="https://example.com/image.jpg"
)
```

#### Create Lead in Odoo

```python
from integrations.odoo_integration import OdooIntegration

odoo = OdooIntegration()
odoo.connect()

# Create lead
lead_id = odoo.crm.create_lead(
    name="John Doe",
    email="john@example.com",
    phone="+1234567890",
    company="Acme Corp",
    description="Interested in our enterprise plan"
)
```

#### Cross-Platform Post

```python
from scripts.gold_tier_orchestrator import post_to_all

results = post_to_all(
    message="Big announcement today!",
    link="https://example.com/news"
)
```

#### Sync Leads to Odoo

```python
from scripts.gold_tier_orchestrator import sync_leads

leads = [
    {
        'source': 'Facebook Comment',
        'sender': 'Jane Smith',
        'content': 'Interested in pricing',
        'email': 'jane@example.com'
    }
]

synced = sync_leads(leads)
```

---

## CLI Commands

### Orchestrator

```bash
# Start full orchestrator
python scripts/gold_tier_orchestrator.py --start

# Post to all platforms
python scripts/gold_tier_orchestrator.py --post "Message" --link "URL"

# Check status
python scripts/gold_tier_orchestrator.py --status

# Test connections
python scripts/gold_tier_orchestrator.py --test-connections
```

### Odoo Docker Management

```bash
# Start Odoo
python scripts/gold_tier_orchestrator.py --odoo-start

# Stop Odoo
python scripts/gold_tier_orchestrator.py --odoo-stop

# Check status
python scripts/gold_tier_orchestrator.py --odoo-status

# Create backup
python scripts/gold_tier_orchestrator.py --odoo-backup
```

### Facebook Integration

```bash
# Post to Facebook
python integrations/facebook_integration.py --post "Message"

# Monitor Facebook
python integrations/facebook_integration.py --monitor

# Get insights
python integrations/facebook_integration.py --insights

# Create ad campaign
python integrations/facebook_integration.py --ad-campaign "Summer Sale" --budget 50
```

### Odoo Integration

```bash
# Create lead
python integrations/odoo_integration.py --create-lead "John Doe" --lead-email "john@example.com"

# Get leads
python integrations/odoo_integration.py --get-leads

# Create quotation
python integrations/odoo_integration.py --create-quotation "Acme Corp"

# Get orders
python integrations/odoo_integration.py --get-orders

# Get products
python integrations/odoo_integration.py --get-products

# Check product quantity
python integrations/odoo_integration.py --product-qty "Product Name"
```

---

## Configuration

### Environment Variables

```bash
# Facebook
FACEBOOK_ACCESS_TOKEN=your_token
FACEBOOK_PAGE_ID=your_page_id
FACEBOOK_CHECK_INTERVAL=120
FACEBOOK_AUTO_RESPONSE=false

# Odoo
ODOO_URL=http://localhost:8069
ODOO_DB=odoo
ODOO_USERNAME=admin
ODOO_PASSWORD=your_password

# Orchestrator
GOLD_AUTO_SYNC_LEADS=true
GOLD_AUTO_CREATE_QUOTATIONS=false
GOLD_CROSS_POST=false
```

---

## Data Models

### Lead (Odoo CRM)

```json
{
  "name": "Lead Name",
  "contact_name": "Contact Person",
  "email_from": "email@example.com",
  "phone": "+1234567890",
  "partner_name": "Company Name",
  "description": "Lead details",
  "source": "Facebook",
  "priority": "3",
  "stage_id": 1
}
```

### Sales Quotation (Odoo)

```json
{
  "partner_id": 123,
  "state": "draft",
  "origin": "Gold Tier FTE - Auto Generated",
  "order_line": [
    {
      "product_id": 456,
      "product_uom_qty": 1,
      "price_unit": 1000.0
    }
  ]
}
```

### Facebook Post

```json
{
  "message": "Post content",
  "link": "https://example.com",
  "visibility": "PUBLIC"
}
```

---

## Workflows

### Lead Generation Workflow

```
1. User comments on Facebook post
2. Facebook Integration detects comment
3. Keyword analysis identifies sales intent
4. Lead created in Odoo CRM automatically
5. Action item created in Needs_Action/
6. Sales team notified
7. (Optional) Quotation auto-generated
```

### Cross-Platform Posting Workflow

```
1. Content created for announcement
2. Sent to Gold Tier Orchestrator
3. Posted to LinkedIn via Silver Tier
4. Posted to Facebook via Gold Tier
5. Both posts logged to AI_Employee_Vault
6. Engagement tracked across platforms
```

---

## Monitoring

### Logs

All activity logged to:
```
AI_Employee_Vault/Logs/
├── gold_tier.log
├── facebook.log
├── odoo.log
└── facebook_posts.log
```

### Stats

Real-time stats available:
- Posts created
- Comments monitored
- Messages processed
- Leads synced
- Quotations created
- Errors encountered

---

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| Facebook API errors | Check token validity and permissions |
| Odoo connection failed | Verify Docker containers are running |
| Leads not syncing | Check AUTO_SYNC_LEADS is enabled |
| Browser automation fails | Reinstall Playwright browsers |

### Debug Mode

Enable debug logging:
```bash
export LOG_LEVEL=DEBUG
python scripts/gold_tier_orchestrator.py --start
```

---

## Security

### Best Practices

- Never commit `.env` files
- Use strong passwords
- Rotate API tokens regularly
- Enable Docker network isolation
- Restrict file permissions
- Use HTTPS in production

### Sensitive Files

```
.env                    # Credentials
*_session.json          # Browser sessions
odoo-backups/*.dump     # Database backups
AI_Employee_Vault/      # Logs with sensitive data
```

---

## Performance

### Optimization

- Run in headless mode for lower resource usage
- Increase check intervals for lower CPU
- Use Odoo workers for better performance
- Enable Redis caching

### Resource Usage

| Component | RAM | CPU |
|-----------|-----|-----|
| Orchestrator | 100MB | Low |
| Facebook | 200MB | Low-Med |
| Odoo Docker | 1.5GB | Medium |

---

## Related Skills

- [`SKILL_LinkedIn_Post.md`](../Skills/SKILL_LinkedIn_Post.md) - LinkedIn posting
- LinkedIn Watcher (Silver Tier) - LinkedIn monitoring

---

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-03-31 | Initial Gold Tier skill |

---

*Gold Tier FTE - Enterprise-Grade AI Employee*

# Personal AI Employee - Gold Tier 🏆

Advanced autonomous AI employee system with **Facebook Graph API Integration**, **Odoo ERP Integration**, and unified cross-platform automation.

**Facebook: Graph API ONLY** - No browser automation, no Playwright needed!

---

## 🚀 Overview

The Gold Tier builds upon the Silver Tier (LinkedIn automation) by adding:

- **Facebook Graph API Integration**: Complete Facebook Page automation via API (posting, monitoring, ads)
- **Odoo ERP Integration**: Full Odoo CRM, Sales, and Inventory management via Docker
- **Unified Orchestrator**: Centralized control for all platforms with automatic lead sync
- **Cross-Platform Automation**: Post to multiple platforms simultaneously
- **Sales Pipeline Automation**: Auto-create leads and quotations from social media engagement

---

## 📁 Project Structure

```
personal-employee-gold-FTEs/
├── scripts/
│   ├── gold_tier_orchestrator.py    # Main orchestrator script
│   └── requirements.txt              # Python dependencies (no Playwright!)
├── integrations/
│   ├── facebook_integration.py       # Facebook Graph API integration
│   └── odoo_integration.py           # Odoo ERP integration
├── odoo-docker/
│   ├── docker-compose.yml            # Odoo Docker setup
│   └── manage.bat                    # Docker management script
├── AI_Employee_Vault/
│   └── Logs/                         # Activity logs
├── Needs_Action/                     # Auto-created action items
├── .env.example                      # Environment template
├── FACEBOOK_SETUP.md                 # Facebook API setup guide
├── setup.bat                         # Quick setup script
├── run_gold_tier.bat                 # Quick start script
└── README.md                         # This file
```

---

## 🛠️ Quick Start

### 1. Setup and Installation

```bash
# Navigate to Gold Tier directory
cd personal-employee-gold-FTEs

# Run setup (Windows)
setup.bat

# Or manually
pip install -r scripts\requirements.txt
playwright install chromium
```

### 2. Configure Credentials

Copy `.env.example` to `.env` and edit with your credentials:

```bash
# LinkedIn (from Silver Tier)
LINKEDIN_EMAIL=your.email@example.com
LINKEDIN_PASSWORD=your_password
LINKEDIN_CLIENT_ID=your_client_id
LINKEDIN_CLIENT_SECRET=your_client_secret

# Facebook
FACEBOOK_ACCESS_TOKEN=your_access_token
FACEBOOK_PAGE_ID=your_page_id

# Odoo ERP
ODOO_URL=http://localhost:8069
ODOO_DB=odoo
ODOO_USERNAME=admin
ODOO_PASSWORD=your_password
```

### 3. Start Odoo (Optional)

```bash
# Using Docker Compose
docker-compose -f odoo-docker\docker-compose.yml up -d

# Or use the management script
cd odoo-docker
manage.bat
```

### 4. Run Gold Tier Orchestrator

```bash
# Using the quick start script
run_gold_tier.bat

# Or manually
python scripts\gold_tier_orchestrator.py --start
```

---

## 📊 Features in Detail

### Facebook Integration

| Feature | Description |
|---------|-------------|
| **Page Posting** | Post updates, links, and photos to Facebook Page |
| **Comment Monitoring** | Monitor comments on posts for engagement |
| **Message Monitoring** | Monitor page inbox messages |
| **Auto-Response** | Automatic responses to comments/messages |
| **Lead Detection** | Detect sales leads from engagement |
| **Ads Management** | Create and manage Facebook Ad campaigns |
| **Page Insights** | Analytics and performance metrics |

### Odoo ERP Integration

| Feature | Description |
|---------|-------------|
| **CRM** | Lead and opportunity management |
| **Sales** | Quotations, orders, and invoices |
| **Inventory** | Product and stock management |
| **Docker Deployment** | One-command Odoo setup with Docker Compose |
| **Auto Lead Creation** | Create leads from social media engagement |
| **Auto Quotations** | Generate quotations from qualified leads |

### Gold Tier Orchestrator

| Feature | Description |
|---------|-------------|
| **Unified Monitoring** | Monitor all platforms from one place |
| **Cross-Platform Posting** | Post to LinkedIn + Facebook simultaneously |
| **Lead Sync** | Automatically sync leads to Odoo CRM |
| **Centralized Logging** | All activity logged to AI_Employee_Vault |
| **Background Threads** | Non-blocking monitoring for all platforms |

---

## 🎯 Use Cases

### 1. Social Media Lead Generation

```
User comments "Interested in pricing" on Facebook
    ↓
Gold Tier detects sales keyword
    ↓
Auto-creates lead in Odoo CRM
    ↓
Notifies sales team via Needs_Action folder
    ↓
(Optional) Auto-creates quotation
```

### 2. Cross-Platform Announcements

```
Company has news to share
    ↓
Send to Gold Tier Orchestrator
    ↓
Posts to LinkedIn (Silver Tier)
    ↓
Posts to Facebook (Gold Tier)
    ↓
Logs to AI_Employee_Vault
```

### 3. Automated Follow-up

```
Lead created in Odoo from Facebook
    ↓
Sales team qualifies lead
    ↓
Converts to opportunity in Odoo
    ↓
Creates quotation
    ↓
Sends to customer
```

---

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `FACEBOOK_CHECK_INTERVAL` | 120 | Facebook monitoring frequency (seconds) |
| `ODOO_SYNC_INTERVAL` | 300 | Odoo sync frequency (seconds) |
| `GOLD_AUTO_SYNC_LEADS` | true | Auto-sync leads to Odoo CRM |
| `GOLD_AUTO_CREATE_QUOTATIONS` | false | Auto-create quotations from leads |
| `GOLD_CROSS_POST` | false | Enable cross-platform posting |
| `FACEBOOK_AUTO_RESPONSE` | false | Enable auto-response to messages |

### Odoo Docker Configuration

Edit `odoo-docker/docker-compose.yml` to customize:

- **Ports**: Change `8069:8069` to different port if needed
- **Volumes**: Configure persistent data storage
- **Environment**: Set database passwords and admin credentials
- **Services**: Enable/disable PgAdmin, Nginx, Redis

---

## 📝 Usage Examples

### Post to All Platforms

```bash
python scripts\gold_tier_orchestrator.py --post "Exciting company news!" --link "https://example.com"
```

### Start Odoo Docker

```bash
python scripts\gold_tier_orchestrator.py --odoo-start
```

### Check System Status

```bash
python scripts\gold_tier_orchestrator.py --status
```

### Create Lead in Odoo

```bash
python integrations\odoo_integration.py --create-lead "John Doe" --lead-email "john@example.com"
```

### Get Facebook Insights

```bash
python integrations\facebook_integration.py --insights
```

### Monitor Facebook Only

```bash
python integrations\facebook_integration.py --monitor
```

---

## 🔌 API Setup

### Facebook Graph API

1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Create a new app or select existing
3. Add **Facebook Login** product
4. Get **App ID** and **App Secret**
5. Generate **Page Access Token**:
   - Go to Graph API Explorer
   - Select your app
   - Get token with `pages_manage_posts`, `pages_read_engagement` permissions
   - Select your page
6. Add to `.env`:
   ```
   FACEBOOK_ACCESS_TOKEN=your_token
   FACEBOOK_PAGE_ID=your_page_id
   ```

### Odoo ERP

Odoo is self-hosted via Docker. No external API needed.

1. Start Odoo: `docker-compose -f odoo-docker\docker-compose.yml up -d`
2. Access at `http://localhost:8069`
3. Default credentials: `admin / admin_secret_123`
4. Create database and configure apps via web interface

---

## 📊 Monitoring and Logging

### Log Files

All activity is logged to:

```
AI_Employee_Vault/
└── Logs/
    ├── gold_tier.log          # Main orchestrator logs
    ├── facebook.log           # Facebook activity
    ├── odoo.log               # Odoo sync logs
    └── facebook_posts.log     # Facebook post history
```

### Action Items

Sales leads and important items are created in:

```
Needs_Action/
├── FACEBOOK_COMMENT_John_Doe_2026-03-31_10-30-00.md
├── FACEBOOK_MESSAGE_Jane_Smith_2026-03-31_11-45-00.md
└── LINKEDIN_MESSAGE_Bob_Wilson_2026-03-31_09-15-00.md
```

---

## 🔐 Security

### Best Practices

⚠️ **Important:**

- Never commit `.env` file (contains passwords and tokens)
- Keep session files private (`linkedin_session.json`, `facebook_session.json`)
- Use strong, unique passwords
- Rotate API tokens periodically
- Use environment variables for production deployments
- Enable Docker network isolation for Odoo

### File Permissions

Ensure proper file permissions:

```bash
# Windows (PowerShell)
icacls .env /grant %USERNAME%:R
icacls AI_Employee_Vault /grant %USERNAME%:RW
```

---

## 🐛 Troubleshooting

### Issue: Odoo Docker won't start

**Solution:**
```bash
# Check Docker is running
docker ps

# Check for port conflicts
netstat -ano | findstr :8069

# Restart containers
docker-compose -f odoo-docker\docker-compose.yml down
docker-compose -f odoo-docker\docker-compose.yml up -d
```

### Issue: Facebook API errors

**Solution:**
- Verify access token is valid and not expired
- Check page ID is correct
- Ensure app has required permissions
- Try browser automation fallback (set email/password in .env)

### Issue: Leads not syncing to Odoo

**Solution:**
- Check Odoo is running: `http://localhost:8069`
- Verify credentials in `.env`
- Check `odoo.log` for errors
- Ensure CRM module is installed in Odoo

### Issue: Playwright browser fails

**Solution:**
```bash
# Reinstall Playwright
pip uninstall playwright
pip install playwright
playwright install chromium

# Clear cache
del /Q %LOCALAPPDATA%\ms-playwright
```

---

## 📈 Performance

### Resource Usage

| Component | RAM | CPU | Disk |
|-----------|-----|-----|------|
| Orchestrator | ~100MB | Low | ~50MB |
| Facebook Monitor | ~200MB | Low-Med | ~20MB |
| Odoo Docker | ~1GB | Medium | ~2GB |
| PostgreSQL | ~500MB | Low | Variable |

### Optimization Tips

- Run in headless mode for lower resource usage
- Increase check intervals for lower CPU usage
- Use Odoo workers for better performance
- Enable Redis caching for faster responses

---

## 🔄 Integration with Silver Tier

The Gold Tier is designed to work seamlessly with the Silver Tier (LinkedIn automation):

```
Silver Tier (LinkedIn)
    ↓
LinkedIn Watcher detects lead
    ↓
Gold Tier Orchestrator
    ↓
Syncs to Odoo CRM
    ↓
Creates action item
```

To enable full integration:

1. Ensure both tiers are in sibling directories
2. Set `GOLD_ENABLE_LINKEDIN=true` in `.env`
3. Run Gold Tier Orchestrator (it will import LinkedIn modules)

---

## 📄 License

MIT License

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Submit pull request

---

## 📞 Support

1. Check logs in `AI_Employee_Vault/Logs/`
2. Review `.env` configuration
3. Test connections: `python scripts\gold_tier_orchestrator.py --test-connections`

---

## 🎓 Learning Resources

- [Facebook Graph API Docs](https://developers.facebook.com/docs/graph-api/)
- [Odoo Documentation](https://www.odoo.com/documentation/)
- [Docker Compose Reference](https://docs.docker.com/compose/)
- [Playwright Documentation](https://playwright.dev/)

---

*Built with ❤️ using Python, Docker, Facebook Graph API, and Odoo ERP*

**Gold Tier FTE - Your Autonomous AI Employee**

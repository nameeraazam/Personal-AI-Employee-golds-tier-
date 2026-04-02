# Personal AI Employee - Silver Tier 🤖

Autonomous AI employee system for LinkedIn automation, monitoring, and engagement.

---

## 🚀 Features

### LinkedIn Automation
- **Auto Authentication**: OAuth 2.0 authentication with session persistence
- **Auto Posting**: Post updates to LinkedIn programmatically
- **LinkedIn Watcher**: Monitor messages, connections, and notifications every 60 seconds
- **Sales Lead Detection**: Automatic keyword detection for sales opportunities
- **Action Item Creation**: Auto-generates markdown files in `Needs_Action/` folder

---

## 📁 Project Structure

```
personal-employe-bronze-FTEs/
├── scripts/
│   ├── linkedin_watcher.py      # Main monitoring script
│   ├── requirements.txt          # Python dependencies
│   └── README.md                 # Setup guide
├── Needs_Action/                  # Auto-created action items
├── linkedin_auth.py              # Authentication script
├── linkedin_post.py              # Posting script
├── run_linkedin_watcher.bat      # Quick start script
├── .env                          # Environment variables (credentials)
└── README.md                     # This file
```

---

## 🛠️ Quick Start

### 1. Install Dependencies

```bash
pip install playwright python-dotenv requests
playwright install chromium
```

### 2. Configure Credentials

Edit `.env` file:

```bash
# LinkedIn Login (for Watcher)
LINKEDIN_EMAIL=your.email@example.com
LINKEDIN_PASSWORD=your_password

# LinkedIn API (for Posting)
LINKEDIN_CLIENT_ID=your_client_id
LINKEDIN_CLIENT_SECRET=your_client_secret
```

### 3. Run LinkedIn Watcher

```bash
# Windows
run_linkedin_watcher.bat

# Or manually
python scripts/linkedin_watcher.py
```

### 4. Post to LinkedIn

```bash
# First authenticate
python linkedin_auth.py

# Then post
python linkedin_post.py -m "Your message here"
```

---

## 📊 Features in Detail

### LinkedIn Watcher
- ✅ Checks every 60 seconds
- ✅ Monitors messages, connections, notifications
- ✅ Detects sales leads (keywords: interested, demo, pricing, etc.)
- ✅ Creates markdown files with frontmatter
- ✅ Session persistence for auto-login
- ✅ Console + file logging

### Action Item Format

```markdown
---
type: linkedin
from: John Smith
content: Interested in your demo...
status: pending
priority: high
---

# LinkedIn Message - John Smith
**Received:** 2026-03-11

## Content
Interested in your demo...
```

---

## 🔧 Configuration

Edit `.env` to customize:

| Variable | Default | Description |
|----------|---------|-------------|
| `LINKEDIN_CHECK_INTERVAL` | 60 | Check frequency (seconds) |
| `LINKEDIN_HEADLESS` | false | Run browser in background |
| `LINKEDIN_MONITOR_MESSAGES` | true | Monitor messages |
| `LINKEDIN_MONITOR_CONNECTIONS` | true | Monitor connections |
| `LINKEDIN_MONITOR_NOTIFICATIONS` | true | Monitor notifications |

---

## 🎯 Sales Keywords

Automatic detection for:
```
interested, demo, pricing, buy, purchase, quote, proposal,
contract, deal, opportunity, budget, decision, timeline,
requirements, rfp, rfi, vendor, solution, partnership
```

---

## 📝 Logs

- **Console**: Real-time output with colors
- **File**: `linkedin_watcher.log`

---

## 🔐 Security

⚠️ **Important:**
- Never commit `.env` file (contains passwords)
- Keep `linkedin_session.json` private
- Use app-specific passwords if available

---

## 📞 Support

1. Check `scripts/README.md` for detailed setup
2. Review `linkedin_watcher.log` for errors
3. Ensure credentials are correct in `.env`

---

## 📄 License

MIT License

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Submit pull request

---

*Built with ❤️ using Playwright & Python*

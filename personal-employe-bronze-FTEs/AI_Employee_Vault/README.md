# AI Employee - Bronze Tier

> **Hackathon 0: Building Autonomous FTEs in 2026**

A personal AI employee system that autonomously monitors external sources (Gmail, file system) and manages tasks using Claude Code and Obsidian.

---

## 📋 Overview

This Bronze Tier implementation provides the foundational layer for an autonomous AI employee:

- **Obsidian Vault**: Central knowledge base and task management system
- **Watcher Scripts**: Monitor Gmail for new important emails
- **Claude Code Integration**: AI-powered task processing and decision making
- **Agent Skills**: Modular capabilities for vault and watcher management

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      AI Employee System                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐   │
│  │   Gmail API  │     │ File System  │     │  Other Sources│   │
│  └──────┬───────┘     └──────┬───────┘     └──────┬───────┘   │
│         │                    │                    │            │
│         ▼                    ▼                    ▼            │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │              Watcher Layer (Python)                      │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │  │
│  │  │GmailWatcher │  │FileWatcher  │  │BaseWatcher  │     │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘     │  │
│  └─────────────────────────────────────────────────────────┘  │
│         │                    │                    │            │
│         ▼                    ▼                    ▼            │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │              Obsidian Vault                              │  │
│  │  ┌──────────┐ ┌──────────────┐ ┌──────┐ ┌───────────┐  │  │
│  │  │  Inbox   │ │Needs_Action  │ │ Done │ │   Logs    │  │  │
│  │  └──────────┘ └──────────────┘ └──────┘ └───────────┘  │  │
│  │  ┌──────────────────────────────────────────────────┐  │  │
│  │  │  Dashboard.md  │  Company_Handbook.md            │  │  │
│  │  └──────────────────────────────────────────────────┘  │  │
│  └─────────────────────────────────────────────────────────┘  │
│         │                                                      │
│         ▼                                                      │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │           Claude Code (AI Agent)                         │  │
│  │  ┌──────────────────┐  ┌──────────────────┐            │  │
│  │  │vault-management  │  │watcher-management│            │  │
│  │  └──────────────────┘  └──────────────────┘            │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📁 Folder Structure

```
AI_Employee_Vault/
├── .claude/
│   └── skills/              # Agent Skills for Claude Code
│       ├── vault-management.md
│       └── watcher-management.md
├── watchers/                # Python watcher scripts
│   ├── __init__.py
│   ├── base_watcher.py
│   └── gmail_watcher.py
├── Inbox/                   # Raw incoming items
├── Needs_Action/            # Items requiring attention
├── Done/                    # Completed items archive
├── Logs/                    # System and activity logs
├── .credentials/            # API credentials (gitignored)
├── Dashboard.md             # System dashboard
├── Company_Handbook.md      # Operational policies
├── requirements.txt         # Python dependencies
├── .env.example             # Environment template
└── README.md                # This file
```

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd AI_Employee_Vault
pip install -r requirements.txt
```

### 2. Setup Gmail API (Optional)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Gmail API
4. Create OAuth 2.0 credentials (Desktop app)
5. Download credentials JSON to `.credentials/gmail_credentials.json`

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env with your settings
```

### 4. Run Gmail Watcher

```bash
python -m watchers.gmail_watcher .
```

### 5. Open in Obsidian

Open the `AI_Employee_Vault` folder in Obsidian to view Dashboard and manage tasks.

---

## 🔧 Agent Skills

### vault-management

Read, write, and manage files in the Obsidian vault.

**Capabilities:**
- Read any markdown file
- Create new action files
- Update Dashboard.md
- Move files between folders

**Usage Example:**
```
Read the file at: Needs_Action/2026-02-25_email_review.md
Create a new file in Needs_Action with title "Review Report"
Update Dashboard.md with new counts
```

### watcher-management

Start, stop, and monitor watcher scripts.

**Capabilities:**
- Start Gmail watcher
- Stop watcher gracefully
- Check watcher status
- Monitor health metrics

**Usage Example:**
```
Start the Gmail watcher
Check if watcher is running
Stop the watcher gracefully
```

---

## 📊 Dashboard

The Dashboard.md provides real-time system status:

| Section | Description |
|---------|-------------|
| Last Updated | Timestamp of last update |
| Status | System health indicator |
| Today's Summary | Counts for Inbox, Needs Action, Completed |
| Recent Activity | Log of recent actions |
| System Status | Watcher and Claude Code status |

---

## 🔍 Watcher Details

### Gmail Watcher

Monitors Gmail for new important unread emails.

**Features:**
- OAuth 2.0 authentication
- Configurable check interval (default: 2 minutes)
- Priority classification based on keywords
- Automatic action file creation
- Processed email tracking

**Priority Keywords:**

| Priority | Keywords |
|----------|----------|
| High | urgent, asap, deadline, emergency, critical |
| Medium | review, feedback, meeting, schedule |
| Low | newsletter, update, notification |

---

## 📈 Performance Targets

| Metric | Target | Status |
|--------|--------|--------|
| Watcher latency | < 2 minutes | ✅ |
| Claude processing | < 30 seconds | ✅ |
| File operations | < 1 second | ✅ |
| Dashboard update | < 5 seconds | ✅ |
| Memory usage | < 200 MB | ✅ |

---

## ✅ Acceptance Criteria

### Vault Structure
- [x] All required folders created
- [x] `.claude/skills/` directory exists
- [x] At least 2 skills defined
- [x] Dashboard.md exists
- [x] Company_Handbook.md exists

### Watcher Functionality
- [x] Watcher script runs without errors
- [x] New items create files in Needs_Action/
- [x] Files have proper frontmatter
- [x] Files are valid Markdown

### Claude Integration
- [x] Claude Code can read vault files
- [x] Claude Code can write to vault
- [x] Claude Code updates Dashboard
- [x] Skills properly defined

---

## 🔮 Next Tiers

### Silver Tier (Coming Soon)
- Approval workflow with `/Approved/` and `/Rejected/` folders
- Automated escalation for threshold items
- Multi-watcher support
- Enhanced dashboard with charts

### Gold Tier (Coming Soon)
- Full autonomous decision making
- Multi-channel monitoring (Slack, SMS, etc.)
- Advanced AI reasoning
- Performance analytics

---

## 📝 License

MIT License - See LICENSE file for details.

---

## 🙏 Acknowledgments

- **Hackathon**: Personal AI Employee Hackathon 0: Building Autonomous FTEs in 2026
- **Tools**: Claude Code, Obsidian, Playwright MCP
- **Inspiration**: Autonomous AI agents for personal productivity

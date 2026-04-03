# AI Employee Vault

Central knowledge management and task tracking system for AI Employee automation.

## Structure

```
AI_Employee_Vault/
├── Logs/                    # Activity and watcher logs
├── Inbox/                   # New tasks awaiting processing
├── Needs_Action/            # Active tasks requiring attention
│   └── watchers/            # Watcher module implementations
├── Done/                    # Completed tasks archive
├── drop_folder/             # File intake folder for monitoring
├── .claude/                 # Claude AI skills configuration
└── README.md                # This file
```

## How It Works

1. **Watchers** monitor external sources (Gmail, File System, etc.)
2. When new items are detected, they create **action files** in `Needs_Action/`
3. Action files contain YAML frontmatter with metadata
4. Tasks are processed and moved to `Done/` when complete
5. All activity is logged to `Logs/`

## Watchers

- **Gmail Watcher**: Monitors Gmail for important emails
- **File System Watcher**: Monitors drop_folder for new files
- **LinkedIn Watcher**: Monitors LinkedIn for messages and leads
- **WhatsApp Watcher**: Monitors WhatsApp Web for messages

## Usage

Start all watchers:
```bash
python -m watchers.orchestrator start
```

Check status:
```bash
python -m watchers.orchestrator status
```

Stop all watchers:
```bash
python -m watchers.orchestrator stop
```

## Action File Format

Action files use YAML frontmatter:

```markdown
---
created: 2026-04-03 10:30:00
source: Gmail: john@example.com
priority: high
status: pending
tags: [email, gmail]
---

# Task Title

## Summary
Brief description

## Details
Full content and context

## Action Required
- [ ] Review content
- [ ] Take appropriate action
- [ ] Move to Done when complete
```

## Priority Levels

- **High**: Urgent, ASAP, deadline, emergency, critical
- **Medium**: Review, feedback, meeting, schedule, reminder
- **Low**: General information, non-urgent items

## Integration

This vault integrates with:
- Gold Tier FTE (Facebook, Odoo, LinkedIn)
- Silver Tier FTE (LinkedIn automation)
- Bronze Tier FTE (Basic watchers)

---

*Built for autonomous AI employee automation*

# Company Handbook

## Overview

This handbook contains guidelines and procedures for AI Employee operations.

## Core Principles

1. **Autonomous Operation**: AI Employees should operate with minimal human intervention
2. **Task Tracking**: All tasks must be tracked in the Needs_Action folder
3. **Logging**: All activities must be logged
4. **Priority Management**: Tasks are prioritized automatically based on content

## Workflow

### Task Lifecycle

1. **Detection**: Watchers detect new items from external sources
2. **Creation**: Action files created in Needs_Action folder
3. **Processing**: Tasks reviewed and actioned
4. **Completion**: Tasks moved to Done folder

### Priority Levels

| Priority | Response Time | Examples |
|----------|--------------|----------|
| High | Immediate | Urgent emails, deadlines, emergencies |
| Medium | Within 24 hours | Meeting requests, reviews, follow-ups |
| Low | Within 48 hours | General information, newsletters |

## Integration Points

### Email (Gmail)
- Monitors for important emails
- Filters by keywords and importance
- Creates action files automatically

### Social Media
- LinkedIn messages and connections
- Facebook comments and messages
- WhatsApp messages with keywords

### File System
- Monitors drop_folder for new files
- Processes markdown, text, and PDF files
- Creates action items for review

## Best Practices

1. Review Needs_Action folder daily
2. Process high priority items first
3. Move completed items to Done folder
4. Keep logs organized and accessible
5. Update this handbook as processes evolve

## Troubleshooting

### Watcher Not Starting
- Check credentials are valid
- Verify .env file exists
- Check logs for error messages

### Missing Action Files
- Verify watcher is running
- Check watch paths are correct
- Review processed files list

### Authentication Issues
- Refresh OAuth tokens
- Re-run authentication flow
- Update credentials in .env

---

*Last updated: April 2026*

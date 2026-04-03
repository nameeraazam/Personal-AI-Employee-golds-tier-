# Watcher Management Skill

## Overview

This skill manages and monitors the AI Employee watchers.

## Capabilities

1. **Start/Stop Watchers**
   - Launch individual watchers
   - Stop specific watchers gracefully
   - Restart failed watchers

2. **Monitor Health**
   - Check watcher status
   - Review recent activity logs
   - Detect and report errors

3. **Configure Settings**
   - Adjust check intervals
   - Update keywords for monitoring
   - Modify watcher priorities

## Available Watchers

- **Gmail Watcher**: Monitors email inbox
- **File System Watcher**: Monitors drop folder
- **LinkedIn Watcher**: Monitors LinkedIn activity
- **WhatsApp Watcher**: Monitors WhatsApp messages

## Commands

```bash
# Start all watchers
python -m watchers.orchestrator start

# Start specific watcher
python -m watchers.orchestrator start gmail

# Stop all watchers
python -m watchers.orchestrator stop

# Check status
python -m watchers.orchestrator status
```

## Troubleshooting

### Watcher Won't Start
1. Check credentials in .env
2. Verify dependencies installed
3. Review error logs in Logs/

### High Error Rate
1. Check API rate limits
2. Verify network connectivity
3. Update authentication tokens

### Missing Items
1. Check processed items list
2. Verify watch paths
3. Review filter criteria

---

*Part of AI Employee Gold Tier FTE*

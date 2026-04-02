---
name: watcher-management
description: |
  Start, stop, and monitor watcher scripts that observe external sources (Gmail, file system).
  Manages watcher lifecycle and status tracking.
version: 1.0
tier: bronze
---

# Watcher Management Skill

## Purpose

Manages the lifecycle of watcher scripts that monitor external data sources. Watchers continuously observe for new items (emails, files) and create action files in the vault when new items are detected.

## Capabilities

### Start Watcher
- Launch watcher script as background process
- Verify watcher is running
- Log startup in Dashboard

### Stop Watcher
- Gracefully terminate watcher process
- Save current state
- Log shutdown in Dashboard

### Monitor Status
- Check if watcher is running
- Get watcher health metrics
- Retrieve last check timestamp

## Usage

### Start Gmail Watcher

```
Start the Gmail watcher script
Verify it's running
Update Dashboard with watcher status: Running
```

### Stop Watcher

```
Stop the Gmail watcher gracefully
Wait for current cycle to complete
Update Dashboard with watcher status: Stopped
```

### Check Status

```
Check if watcher is running
Get last check timestamp
Report any errors from Logs
```

## Watcher Interface

All watchers must inherit from `BaseWatcher` class:

```python
class BaseWatcher:
    def check_for_updates(self) -> list:
        """Check for new items. Returns list of new items."""
        pass
    
    def create_action_file(self, item: dict) -> str:
        """Create action file in Needs_Action/. Returns file path."""
        pass
    
    def run(self):
        """Main loop - continuously monitor for new items."""
        pass
```

## Watcher Configuration

### Gmail Watcher Settings

| Setting | Description | Default |
|---------|-------------|---------|
| `check_interval` | Seconds between checks | 120 |
| `only_unread` | Only process unread emails | True |
| `only_important` | Only process important emails | True |
| `max_results` | Max emails per check | 10 |

### File System Watcher Settings

| Setting | Description | Default |
|---------|-------------|---------|
| `watch_path` | Directory to monitor | ./drop_folder |
| `check_interval` | Seconds between checks | 60 |
| `file_patterns` | File patterns to watch | *.md, *.txt |

## Status Tracking

### Watcher States

| State | Description |
|-------|-------------|
| `running` | Actively monitoring |
| `stopped` | Gracefully shut down |
| `error` | Encountered an error |
| `starting` | Initializing |
| `stopping` | Shutting down |

### Dashboard Integration

Watcher status is tracked in Dashboard.md:

```markdown
## System Status

| Component | Status | Last Check |
|-----------|--------|------------|
| 📧 Watcher | 🟢 Running | 2026-02-25 10:30:00 |
```

## Error Handling

1. **Process Crash**: Log error, attempt restart (max 3 times)
2. **API Rate Limit**: Backoff exponentially, retry after delay
3. **Authentication Error**: Stop watcher, log error, notify user
4. **Network Error**: Retry with exponential backoff

## Performance Targets

| Metric | Target |
|--------|--------|
| Watcher latency | < 2 minutes |
| Memory usage | < 200 MB per watcher |
| Restart time | < 10 seconds |
| Error recovery | < 1 minute |

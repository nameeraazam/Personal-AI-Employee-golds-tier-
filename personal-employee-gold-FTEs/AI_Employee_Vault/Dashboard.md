# AI Employee Dashboard

## Quick Links

- [Needs Action Folder](./Needs_Action/) - Active tasks
- [Inbox](./Inbox/) - New unprocessed items
- [Done](./Done/) - Completed tasks archive
- [Drop Folder](./drop_folder/) - File intake
- [Logs](./Logs/) - Activity logs

## Current Status

### Active Watchers

| Watcher | Status | Last Check | Items Processed |
|---------|--------|------------|-----------------|
| Gmail | ⏳ Not Started | - | 0 |
| File System | ⏳ Not Started | - | 0 |
| LinkedIn | ⏳ Not Started | - | 0 |
| WhatsApp | ⏳ Not Started | - | 0 |

### Task Summary

| Category | Count |
|----------|-------|
| High Priority | 0 |
| Medium Priority | 0 |
| Low Priority | 0 |
| **Total Active** | **0** |

## Getting Started

1. **Configure Credentials**
   - Edit `.env` file with your credentials
   - Run authentication for each service

2. **Start Watchers**
   ```bash
   python -m watchers.orchestrator start
   ```

3. **Monitor Activity**
   - Check `Needs_Action/` for new tasks
   - Review logs in `Logs/` folder

4. **Process Tasks**
   - Review action files
   - Take required actions
   - Move to `Done/` when complete

## Keyboard Shortcuts

- Start all watchers: `python -m watchers.orchestrator start`
- Stop all watchers: `python -m watchers.orchestrator stop`
- Check status: `python -m watchers.orchestrator status`

## Recent Activity

*No recent activity - watchers not yet started*

---

*Dashboard auto-updates when watchers are running*

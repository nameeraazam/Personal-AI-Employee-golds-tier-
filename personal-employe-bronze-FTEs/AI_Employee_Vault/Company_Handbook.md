---
created: 2026-02-25
version: 1.0
status: Active
---

# 📖 Company Handbook

## Overview

This handbook defines the operational policies, communication rules, and guidelines for the AI Employee system. All autonomous agents must adhere to these policies when performing tasks.

---

## Communication Rules

### Email Guidelines

1. **Priority Classification**
   - **High Priority**: Contains keywords like "urgent", "asap", "deadline", "emergency"
   - **Medium Priority**: Contains keywords like "review", "feedback", "meeting", "schedule"
   - **Low Priority**: General notifications, newsletters, updates

2. **Response Templates**

   **Acknowledgment Template:**
   ```
   Thank you for your message. I am an AI assistant managing this inbox.
   Your message has been received and logged for review.
   
   Reference: [AUTO-ACK-{timestamp}]
   ```

   **Action Required Template:**
   ```
   Your request has been logged and requires action.
   Expected response time: Within 24 hours.
   
   Ticket: [TICKET-{id}]
   Status: Pending Review
   ```

3. **Email Processing Rules**
   - All unread important emails are monitored every 2 minutes
   - Emails are categorized by priority keywords
   - Action items are created in `/Needs_Action/` folder
   - Processed emails are logged in `/Logs/`

---

## Operational Policies

### Working Hours

- **Standard Hours**: 24/7 autonomous operation
- **Human Review Window**: 9:00 AM - 6:00 PM (for items requiring approval)
- **Batch Processing**: Every 2 minutes for incoming items

### Priority Keywords

| Priority | Keywords |
|----------|----------|
| High | urgent, asap, deadline, emergency, critical, immediate |
| Medium | review, feedback, meeting, schedule, call, discuss |
| Low | newsletter, update, notification, info, FYI |

### File Organization

```
AI_Employee_Vault/
├── Inbox/           # Raw incoming items (auto-processed)
├── Needs_Action/    # Items requiring human attention or AI action
├── Done/            # Completed and archived items
├── Logs/            # System logs and activity history
└── .claude/         # Agent skills and configuration
```

### Naming Conventions

- **Action Files**: `{YYYY-MM-DD}_{source}_{brief-description}.md`
- **Log Files**: `log-{YYYY-MM-DD}.md`
- **Email Files**: `{YYYY-MM-DD}_{sender}_{subject}.md`

---

## Approval Thresholds (Bronze Tier - Logging Only)

> **Note**: In Bronze tier, all items requiring approval are logged but NOT automatically escalated. This is a logging-only feature for tracking purposes.

### Threshold Categories

| Category | Auto-Process | Log Only | Human Review Required |
|----------|-------------|----------|----------------------|
| Financial < $100 | ✅ | - | - |
| Financial >= $100 | - | ✅ | ✅ |
| Calendar Events | ✅ | - | - |
| New Contacts | ✅ | ✅ | - |
| Document Requests | ✅ | ✅ | - |

### Logging Format

When an item meets approval threshold criteria:

```markdown
---
type: approval_log
threshold_category: financial
amount: 150
auto_approved: false
logged_at: 2026-02-25 00:00:00
requires_human: true
---

## Approval Required

**Item**: [Description]
**Category**: Financial
**Amount**: $150.00
**Reason**: Exceeds Bronze tier auto-approval threshold

**Status**: Logged for Silver tier escalation
```

---

## Agent Behavior Guidelines

### Decision Making

1. **Autonomous Decisions** (No human required)
   - Categorizing incoming emails
   - Creating action files
   - Updating dashboard
   - Logging activities

2. **Logged Decisions** (Track for review)
   - Items meeting approval thresholds
   - Unusual patterns detected
   - System anomalies

3. **Human Required** (Bronze: log only)
   - Financial transactions >= $100
   - External communications requiring approval
   - Policy exceptions

### Error Handling

1. **On Failure**: Log error to `/Logs/error-{timestamp}.md`
2. **On Uncertainty**: Create item in `/Needs_Action/` with uncertainty flag
3. **On System Issue**: Update Dashboard status and log incident

---

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-25 | Initial Bronze tier handbook |

---
name: vault-management
description: |
  Read, write, and manage files in the Obsidian vault. 
  Supports creating, updating, and organizing files across Inbox, Needs_Action, Done, and Logs folders.
version: 1.0
tier: bronze
---

# Vault Management Skill

## Purpose

Provides core file operations for the AI Employee to interact with the Obsidian vault. This skill enables reading existing files, creating new action items, updating the dashboard, and archiving completed items.

## Capabilities

### Read Files
- Read any markdown file in the vault
- Parse YAML frontmatter
- Extract content and metadata

### Write Files
- Create new files in any folder
- Update existing files
- Manage frontmatter metadata

### Organize Files
- Move files between folders (Inbox → Needs_Action → Done)
- Archive completed items
- Maintain folder structure

## Usage

### Read a File

```
Read the file at: Needs_Action/2026-02-25_email_review.md
```

### Create New File

```
Create a new file in Needs_Action with:
- Title: Review Quarterly Report
- Priority: High
- Source: Email
- Content: [details]
```

### Update Dashboard

```
Update Dashboard.md with:
- Increment Needs_Action count
- Add entry to Recent Activity
- Update last_updated timestamp
```

### Move File to Done

```
Move file Needs_Action/2026-02-25_task.md to Done/
Update Dashboard.md to increment Completed count
```

## File Format Standards

### Frontmatter Template

```yaml
---
created: YYYY-MM-DD HH:MM:SS
source: email|file|manual
priority: high|medium|low
status: pending|in_progress|completed
tags: []
---
```

### Action File Template

```markdown
---
created: 2026-02-25 10:30:00
source: email
priority: high
status: pending
tags: [review, urgent]
---

# {Title}

## Summary
Brief description of the action item.

## Details
Full content and context.

## Action Required
Specific steps needed.

## Source
- From: sender@example.com
- Received: 2026-02-25 10:30:00
- Original: [link or reference]
```

## Error Handling

1. **File Not Found**: Return clear error message with suggested paths
2. **Invalid Frontmatter**: Log warning and attempt to parse content
3. **Permission Denied**: Log error and notify in Dashboard

## Performance Targets

| Operation | Target |
|-----------|--------|
| Read file | < 100ms |
| Write file | < 500ms |
| Update Dashboard | < 5 seconds |
| Move file | < 1 second |

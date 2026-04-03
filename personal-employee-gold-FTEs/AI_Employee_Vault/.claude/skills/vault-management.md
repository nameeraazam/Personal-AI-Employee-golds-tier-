# Vault Management Skill

## Overview

This skill manages the AI Employee vault structure and organization.

## Capabilities

1. **Create Action Files**
   - Generate properly formatted markdown files with YAML frontmatter
   - Set appropriate priority levels
   - Add relevant tags and metadata

2. **Organize Tasks**
   - Move tasks between folders (Inbox → Needs_Action → Done)
   - Update task status
   - Archive completed tasks

3. **Maintain Vault Health**
   - Check folder structure integrity
   - Verify log files are being created
   - Ensure watchers are configured correctly

## Usage

When managing the vault:
- Always use proper YAML frontmatter
- Include all required metadata
- Maintain consistent naming conventions
- Log all significant actions

## File Naming Convention

```
{DATE}_{SOURCE}_{TITLE}.md
Example: 2026-04-03_gmail_Important_Client_Request.md
```

## Priority Assignment

- **High**: Contains urgent/asap/deadline/emergency/critical
- **Medium**: Contains review/meeting/schedule/reminder
- **Low**: General information

---

*Part of AI Employee Gold Tier FTE*

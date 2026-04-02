# Project Overview

This repository contains the **browsing-with-playwright** skill - a browser automation module that enables autonomous agents to interact with websites via the Playwright MCP (Model Context Protocol) server. It is designed for building autonomous FTEs (Full-Time Employees) capable of web browsing, form submission, data extraction, and UI testing.

## Purpose

Enable AI agents to perform browser-based tasks including:
- Web navigation and page state inspection
- Form filling and submission
- Click, type, hover, and drag-and-drop interactions
- Screenshot capture and accessibility snapshots
- Data extraction from web pages
- Multi-step automation workflows

---

# Directory Structure

```
personal employe bronze-FTEs/
├── .qwen/
│   └── skills/
│       └── browsing-with-playwright/
│           ├── SKILL.md              # Skill documentation and usage guide
│           ├── scripts/
│           │   ├── mcp-client.py     # Universal MCP client (HTTP/stdio transport)
│           │   ├── start-server.sh   # Start Playwright MCP server
│           │   ├── stop-server.sh    # Stop server gracefully
│           │   └── verify.py         # Server health check script
│           └── references/
│               └── playwright-tools.md  # Complete tool reference (22 tools)
├── skills-lock.json                  # Skill versioning and source tracking
├── .gitattributes
└── QWEN.md                           # This file
```

---

# Key Files

| File | Description |
|------|-------------|
| `scripts/mcp-client.py` | Python MCP client supporting HTTP and stdio transports. Used to call Playwright tools. |
| `scripts/start-server.sh` | Shell script to launch the Playwright MCP server on port 8808. |
| `scripts/stop-server.sh` | Gracefully stops the server and closes browser. |
| `scripts/verify.py` | Verifies server is running and accessible. |
| `references/playwright-tools.md` | Auto-generated documentation for all 22 available browser tools. |
| `skills-lock.json` | Tracks skill source (`bilalmk/todo_correct` from GitHub) and version hash. |

---

# Server Lifecycle

## Start Server

```bash
# Recommended: Use helper script
bash .qwen/skills/browsing-with-playwright/scripts/start-server.sh

# Manual alternative
npx @playwright/mcp@latest --port 8808 --shared-browser-context &
```

**Note:** The `--shared-browser-context` flag is required to maintain browser state across multiple calls.

## Stop Server

```bash
# Recommended: Use helper script (closes browser first)
bash .qwen/skills/browsing-with-playwright/scripts/stop-server.sh

# Manual alternative
python .qwen/skills/browsing-with-playwright/scripts/mcp-client.py call -u http://localhost:8808 -t browser_close -p '{}'
pkill -f "@playwright/mcp"
```

## Verify Server

```bash
python .qwen/skills/browsing-with-playwright/scripts/verify.py
```

Expected output: `✓ Playwright MCP server running`

---

# Available Tools (22)

## Navigation
| Tool | Description |
|------|-------------|
| `browser_navigate` | Navigate to a URL |
| `browser_navigate_back` | Go back to previous page |
| `browser_tabs` | List, create, close, or select tabs |

## Page State
| Tool | Description |
|------|-------------|
| `browser_snapshot` | Capture accessibility snapshot (element refs for interaction) |
| `browser_take_screenshot` | Take PNG/JPEG screenshot |
| `browser_console_messages` | Get console messages |
| `browser_network_requests` | Get network request log |

## Interaction
| Tool | Description |
|------|-------------|
| `browser_click` | Click or double-click element |
| `browser_hover` | Hover over element |
| `browser_type` | Type text into input field |
| `browser_fill_form` | Fill multiple form fields at once |
| `browser_select_option` | Select dropdown options |
| `browser_drag` | Drag and drop between elements |
| `browser_press_key` | Press keyboard key |
| `browser_file_upload` | Upload files |
| `browser_handle_dialog` | Accept/dismiss dialogs |

## Automation
| Tool | Description |
|------|-------------|
| `browser_run_code` | Execute multi-step Playwright code |
| `browser_evaluate` | Run JavaScript on page/element |
| `browser_wait_for` | Wait for text or time duration |

## Utility
| Tool | Description |
|------|-------------|
| `browser_resize` | Resize browser window |
| `browser_close` | Close page |
| `browser_install` | Install browser if missing |

---

# Usage Examples

## Basic Navigation and Snapshot

```bash
# Navigate
python scripts/mcp-client.py call -u http://localhost:8808 \
  -t browser_navigate -p '{"url": "https://example.com"}'

# Get page snapshot (returns element refs)
python scripts/mcp-client.py call -u http://localhost:8808 \
  -t browser_snapshot -p '{}'
```

## Form Submission

```bash
# Fill form fields
python scripts/mcp-client.py call -u http://localhost:8808 \
  -t browser_fill_form -p '{"fields": [{"ref": "e10", "value": "john@example.com"}]}'

# Click submit
python scripts/mcp-client.py call -u http://localhost:8808 \
  -t browser_click -p '{"element": "Submit", "ref": "e42"}'
```

## Multi-Step Automation

```bash
python scripts/mcp-client.py call -u http://localhost:8808 \
  -t browser_run_code -p '{"code": "async (page) => { await page.goto(\"https://example.com\"); await page.click(\"text=Learn more\"); return await page.title(); }"}'
```

---

# Typical Workflow

### Form Submission
1. Navigate to page
2. Get snapshot to find element refs
3. Fill form fields using refs
4. Click submit
5. Wait for confirmation
6. Screenshot result

### Data Extraction
1. Navigate to page
2. Get snapshot (contains text content)
3. Use `browser_evaluate` for complex extraction
4. Process results

---

# Troubleshooting

| Issue | Solution |
|-------|----------|
| Element not found | Run `browser_snapshot` first to get current refs |
| Click fails | Try `browser_hover` first, then click |
| Form not submitting | Use `"submit": true` with `browser_type` |
| Page not loading | Increase wait time or use `browser_wait_for` |
| Server not responding | Restart: `bash scripts/stop-server.sh && bash scripts/start-server.sh` |

---

# Development Notes

- **Transport**: MCP client supports both HTTP (port 8808) and stdio transports
- **Session Management**: HTTP transport maintains session via `Mcp-Session-Id` header
- **JSON-RPC 2.0**: All communication follows JSON-RPC 2.0 protocol
- **Shared Context**: Server must run with `--shared-browser-context` for stateful interactions

---

# Related

- **Skill Source**: [bilalmk/todo_correct](https://github.com/bilalmk/todo_correct) on GitHub
- **MCP Protocol**: Model Context Protocol for AI agent tool integration
- **Playwright**: Microsoft's browser automation library

# Browsing with Playwright

## Overview

This skill enables web browsing and automation using Playwright for AI Employee tasks.

## When to Use

- Scraping web data for research
- Automating web-based workflows
- Testing web applications
- Capturing screenshots
- Filling forms programmatically

## Setup

1. Install Playwright:
   ```bash
   pip install playwright
   playwright install chromium
   ```

2. Start the MCP server (if using MCP integration):
   ```bash
   python scripts/mcp-client.py
   ```

## Capabilities

### 1. Navigate to URLs
```python
await page.goto('https://example.com')
await page.wait_for_load_state('networkidle')
```

### 2. Click Elements
```python
await page.click('button#submit')
await page.click('a[href="/login"]')
```

### 3. Fill Forms
```python
await page.fill('input[name="email"]', 'user@example.com')
await page.fill('input[name="password"]', 'secret')
```

### 4. Extract Data
```python
text = await page.text_content('div.content')
all_items = await page.query_selector_all('.item')
```

### 5. Take Screenshots
```python
await page.screenshot(path='screenshot.png')
```

### 6. Wait for Conditions
```python
await page.wait_for_selector('.loaded-element')
await page.wait_for_function('() => document.readyState === "complete"')
```

## Best Practices

1. **Use Explicit Waits**: Always wait for elements or states
2. **Handle Errors**: Catch and log exceptions
3. **Use Selectors Wis**: Prefer data-testid or unique IDs
4. **Close Browser**: Always clean up resources
5. **Respect Rate Limits**: Don't overload servers

## Anti-Detection

```python
browser = await playwright.chromium.launch(
    headless=False,
    args=['--disable-blink-features=AutomationControlled']
)

context = await browser.new_context(
    viewport={'width': 1920, 'height': 1080},
    user_agent='Mozilla/5.0 ...'
)
```

## Common Patterns

### Login Flow
```python
await page.goto('https://site.com/login')
await page.fill('#username', username)
await page.fill('#password', password)
await page.click('button[type="submit"]')
await page.wait_for_load_state('networkidle')
```

### Data Extraction
```python
items = await page.query_selector_all('.item')
for item in items:
    title = await item.text_content('h3')
    link = await item.get_attribute('a', 'href')
    print(f"{title}: {link}")
```

## Troubleshooting

### Element Not Found
- Check selector is correct
- Add wait for element to appear
- Verify page loaded completely

### Browser Won't Start
- Ensure Playwright installed: `playwright install chromium`
- Check for port conflicts

### Session Lost
- Save cookies regularly
- Re-authenticate if needed

## Integration with AI Employee

This skill integrates with:
- LinkedIn automation
- Facebook monitoring
- WhatsApp Web
- General web research

---

*Part of AI Employee Gold Tier FTE*

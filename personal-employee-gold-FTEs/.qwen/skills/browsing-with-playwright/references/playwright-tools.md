# Playwright Tools Reference

## Available Tools

### 1. Page Navigation
- `page.goto(url, options)` - Navigate to URL
- `page.reload(options)` - Reload current page
- `page.goBack(options)` - Navigate back
- `page.goForward(options)` - Navigate forward

### 2. Element Interaction
- `page.click(selector, options)` - Click element
- `page.dblclick(selector, options)` - Double click
- `page.fill(selector, value, options)` - Fill input field
- `page.check(selector, options)` - Check checkbox
- `page.uncheck(selector, options)` - Uncheck checkbox
- `page.selectOption(selector, values, options)` - Select dropdown option

### 3. Data Extraction
- `page.text_content(selector, options)` - Get text content
- `page.get_attribute(selector, attribute, options)` - Get attribute value
- `page.inner_html(selector, options)` - Get inner HTML
- `page.input_value(selector, options)` - Get input value

### 4. Query Methods
- `page.$(selector)` - Query single element
- `page.$$(selector)` - Query multiple elements
- `page.waitForSelector(selector, options)` - Wait for element
- `page.waitForFunction(pageFunction, options)` - Wait for JS condition

### 5. Page Info
- `page.url()` - Get current URL
- `page.title()` - Get page title
- `page.content()` - Get full HTML
- `page.viewportSize()` - Get viewport dimensions

### 6. Screenshots & PDF
- `page.screenshot(options)` - Take screenshot
- `page.pdf(options)` - Generate PDF

### 7. Keyboard & Mouse
- `page.keyboard.press(key, options)` - Press key
- `page.keyboard.type(text, options)` - Type text
- `page.mouse.click(x, y, options)` - Click at coordinates
- `page.mouse.move(x, y, options)` - Move mouse

### 8. Frames & Dialogs
- `page.frame(name)` - Get frame by name
- `page.on('dialog', handler)` - Handle dialogs
- `page.on('popup', handler)` - Handle popups

## Common Selectors

### CSS Selectors
```
div.container
button#submit
input[name="email"]
a[href*="/products"]
.item:nth-child(2)
```

### Text Selectors
```
text="Submit"
text=/.*login.*/i
```

### XPath Selectors
```
xpath=//div[@class='container']
xpath=//button[text()='Submit']
```

## Wait Strategies

### Wait for Selector
```python
await page.wait_for_selector('.element', state='visible')
await page.wait_for_selector('.element', state='attached')
```

### Wait for Load State
```python
await page.wait_for_load_state('load')
await page.wait_for_load_state('domcontentloaded')
await page.wait_for_load_state('networkidle')
```

### Wait for Function
```python
await page.wait_for_function('() => window.dataLoaded')
await page.wait_for_function('() => document.querySelectorAll(".item").length > 0')
```

## Error Handling

```python
try:
    await page.click('button#submit', timeout=5000)
except TimeoutError:
    print("Button not found within timeout")
except Exception as e:
    print(f"Error: {e}")
```

## Performance Tips

1. Use `headless=True` for faster execution
2. Block unnecessary resources (images, fonts)
3. Reuse browser contexts
4. Use efficient selectors (ID > class > XPath)
5. Minimize waits to only what's necessary

---

*Reference for Playwright Python API*

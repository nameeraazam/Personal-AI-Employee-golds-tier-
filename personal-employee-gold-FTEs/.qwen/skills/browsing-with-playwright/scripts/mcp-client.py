#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP Client for Playwright Integration

Provides tools for web automation via MCP protocol.
"""

import asyncio
import json
import sys
from playwright.async_api import async_playwright


class PlaywrightMCPClient:
    """MCP client for Playwright web automation."""

    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    async def initialize(self):
        """Initialize Playwright."""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=False,
            args=['--disable-blink-features=AutomationControlled']
        )
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        self.page = await self.context.new_page()
        print("✓ Playwright initialized")

    async def navigate(self, url):
        """Navigate to URL."""
        await self.page.goto(url, wait_until='networkidle')
        return {"status": "success", "url": self.page.url, "title": await self.page.title()}

    async def click(self, selector):
        """Click element."""
        await self.page.click(selector)
        return {"status": "success", "clicked": selector}

    async def fill(self, selector, text):
        """Fill input field."""
        await self.page.fill(selector, text)
        return {"status": "success", "filled": selector}

    async def get_text(self, selector):
        """Get text content."""
        text = await self.page.text_content(selector)
        return {"status": "success", "text": text}

    async def screenshot(self, path):
        """Take screenshot."""
        await self.page.screenshot(path=path)
        return {"status": "success", "path": path}

    async def close(self):
        """Close browser."""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        print("✓ Browser closed")


async def main():
    """Main loop for MCP communication."""
    client = PlaywrightMCPClient()

    try:
        await client.initialize()

        # Simple command loop for testing
        print("\nPlaywright MCP Client Ready")
        print("Commands: navigate, click, fill, get_text, screenshot, close, exit")

        while True:
            try:
                line = input("\n> ").strip()
                if not line:
                    continue

                parts = line.split(' ', 1)
                command = parts[0]

                if command == 'exit':
                    break
                elif command == 'navigate' and len(parts) > 1:
                    result = await client.navigate(parts[1])
                    print(json.dumps(result, indent=2))
                elif command == 'close':
                    await client.close()
                else:
                    print(f"Unknown command or missing args: {command}")

            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")

    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())

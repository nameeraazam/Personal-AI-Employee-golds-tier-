#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verify Playwright Installation

Tests that Playwright is properly installed and can launch a browser.
"""

import asyncio
import sys


async def verify():
    """Verify Playwright installation."""
    print("Verifying Playwright installation...\n")

    try:
        from playwright.async_api import async_playwright
        print("✓ Playwright module imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import Playwright: {e}")
        print("\nInstall with: pip install playwright")
        print("Then run: playwright install chromium")
        return False

    try:
        playwright = await async_playwright().start()
        print("✓ Playwright started successfully")

        browser = await playwright.chromium.launch(headless=True)
        print("✓ Chromium browser launched")

        page = await browser.new_page()
        await page.goto('https://example.com')
        title = await page.title()
        print(f"✓ Navigated to example.com - Title: {title}")

        await browser.close()
        await playwright.stop()

        print("\n" + "="*50)
        print("✅ PLAYWRIGHT VERIFICATION SUCCESSFUL!")
        print("="*50)
        print("\nYou can now use web automation features.")
        return True

    except Exception as e:
        print(f"\n✗ Verification failed: {e}")
        print("\nTry reinstalling:")
        print("  pip uninstall playwright")
        print("  pip install playwright")
        print("  playwright install chromium")
        return False


if __name__ == "__main__":
    success = asyncio.run(verify())
    sys.exit(0 if success else 1)

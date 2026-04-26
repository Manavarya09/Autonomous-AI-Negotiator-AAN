"""Anti-detection utilities for web scraping."""

import asyncio
import random
from typing import Optional

from playwright.async_api import Browser, BrowserContext, Page, async_playwright


USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/122.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/122.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Ed/122.0.0.0 Safari/537.36",
]

VIEWPORTS = [
    (1280, 720),
    (1366, 768),
    (1440, 900),
    (1536, 864),
    (1920, 1080),
]


def get_random_user_agent() -> str:
    return random.choice(USER_AGENTS)


def get_random_viewport() -> tuple[int, int]:
    return random.choice(VIEWPORTS)


async def random_delay(min_seconds: float = 1.5, max_seconds: float = 4.5) -> None:
    delay = random.uniform(min_seconds, max_seconds)
    await asyncio.sleep(delay)


async def create_stealth_context(
    browser: Browser,
    proxy: Optional[str] = None,
    headless: bool = True,
) -> BrowserContext:
    user_agent = get_random_user_agent()
    width, height = get_random_viewport()

    context_options = {
        "user_agent": user_agent,
        "viewport": {"width": width, "height": height},
        "locale": "en-US",
        "timezone_id": "Asia/Dubai",
        "geolocation": {"longitude": 55.2708, "latitude": 25.2048},
        "permissions": ["geolocation"],
        "headless": headless,
    }

    if proxy:
        context_options["proxy"] = {"server": proxy}

    context = await browser.new_context(**context_options)

    await context.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined,
        });
    """)

    await context.add_init_script("""
        window.navigator.chrome = {
            runtime: {},
        };
    """)

    await context.add_init_script("""
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5],
        });
    """)

    await context.add_init_script("""
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en'],
        });
    """)

    return context


async def get_playwright() -> async_playwright:
    pw = await async_playwright().start()
    return pw


async def launch_browser(
    headless: bool = True,
    proxy: Optional[str] = None,
) -> Browser:
    pw = await async_playwright().start()
    browser = await pw.chromium.launch(
        headless=headless,
        proxy={"server": proxy} if proxy else None,
        args=[
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-dev-shm-usage",
            "--disable-accelerated-2d-canvas",
            "--no-first-run",
            "--no-zygote",
            "--disable-gpu",
        ],
    )
    return browser
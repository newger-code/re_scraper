import asyncio
import random
from abc import ABC, abstractmethod
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from playwright_stealth import Stealth
from config import settings
from logging_config import setup_logging

logger = setup_logging()

class BaseScraper(ABC):
    """
    Abstract base class for all scrapers.
    Handles browser initialization, proxy setup, and anti-evasion techniques.
    """
    def __init__(self, source_name: str):
        self.source_name = source_name
        self.proxy = {"server": settings.proxy_url} if settings.proxy_url else None

    @abstractmethod
    async def scrape(self, address: str) -> dict:
        """
        The main method to be implemented by each scraper.
        It should take a normalized address and return a dictionary of scraped data.
        """
        pass

    async def _get_stealth_page(self, p_playwright, retries=settings.MAX_RETRIES):
        """
        Creates a new browser page with stealth features and proxy configured.
        Includes retry logic for browser launch.
        """
        for attempt in range(retries):
            try:
                browser = await p_playwright.chromium.launch(
                    headless=True,
                    proxy=self.proxy,
                    args=['--ignore-certificate-errors'] # Necessary for some proxy setups
                )
                context = await browser.new_context(
                    user_agent=random.choice(settings.USER_AGENTS),
                    ignore_https_errors=True # Also helpful for proxies
                )
                page = await context.new_page()
                stealth = Stealth()
                await stealth.apply_stealth_async(context)
                logger.info("Browser page created successfully.", source=self.source_name)
                return page, browser, context
            except Exception as e:
                logger.error(
                    "Failed to launch browser",
                    source=self.source_name,
                    attempt=attempt + 1,
                    error=str(e)
                )
                if attempt < retries - 1:
                    await asyncio.sleep(settings.RETRY_DELAY)
                else:
                    raise

    async def _navigate_and_get_content(self, page, url: str, wait_selector: str = None):
        """
        Navigates to a URL and waits for a specific element if provided.
        Returns the page content.
        """
        try:
            await page.goto(url, timeout=settings.REQUEST_TIMEOUT * 1000)
            if wait_selector:
                await page.wait_for_selector(wait_selector, timeout=15000)

            content = await page.content()
            logger.info("Successfully navigated and fetched content.", url=url, source=self.source_name)
            return content
        except PlaywrightTimeoutError:
            logger.warning("Timeout while navigating or waiting for selector.", url=url, selector=wait_selector, source=self.source_name)
            return None
        except Exception as e:
            logger.error("Error during navigation.", url=url, error=str(e), source=self.source_name)
            return None

    def _clean_text(self, text):
        """Utility to clean and strip text."""
        return text.strip() if text else None

    def _to_int(self, value_str):
        """Utility to convert a string to an integer, handling currency symbols and commas."""
        if not value_str:
            return None
        try:
            return int(''.join(filter(str.isdigit, str(value_str))))
        except (ValueError, TypeError):
            return None

    def _to_float(self, value_str):
        """Utility to convert a string to a float."""
        if not value_str:
            return None
        try:
            # Handle cases like '2.5'
            cleaned_str = ''.join(c for c in str(value_str) if c.isdigit() or c == '.')
            return float(cleaned_str)
        except (ValueError, TypeError):
            return None

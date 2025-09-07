from scrapers.base_scraper import BaseScraper
from logging_config import setup_logging
from playwright.async_api import async_playwright
from config import settings

logger = setup_logging()

class SpatialestScraper(BaseScraper):
    def __init__(self, county_name: str, county_url: str):
        super().__init__(f"{county_name}_Spatialest")
        self.county_url = county_url

    async def scrape(self, address: str) -> dict:
        """
        (Temporary Investigation Code)
        Navigates to a Spatialest portal and takes a screenshot for analysis.
        """
        logger.info("INVESTIGATION: Starting Spatialest scrape for screenshot", url=self.county_url)

        async with async_playwright() as p:
            page = None
            browser = None
            context = None
            try:
                page, browser, context = await self._get_stealth_page(p)
                await page.goto(self.county_url, timeout=settings.REQUEST_TIMEOUT * 1000)

                screenshot_path = "spatialest_screenshot.png"
                await page.screenshot(path=screenshot_path, full_page=True)
                logger.info(f"Screenshot saved to {screenshot_path}")

                return {"status": "ok", "screenshot": screenshot_path}
            except Exception as e:
                logger.error("An error occurred during Spatialest investigation", error=str(e), exc_info=True)
                return {"error": str(e)}
            finally:
                if browser:
                    await browser.close()

import json
from playwright.async_api import async_playwright
from scrapers.base_scraper import BaseScraper
from logging_config import setup_logging
from config import settings

logger = setup_logging()

class RealtorScraper(BaseScraper):
    def __init__(self):
        super().__init__("Realtor")

    async def scrape(self, address: str) -> dict:
        """
        Scrapes property data from Realtor.com by finding the embedded __NEXT_DATA__ JSON blob.
        """
        # Realtor.com search is a good way to find the canonical URL
        search_url = f"https://www.realtor.com/search/{address.replace(' ', '_')}"
        logger.info("Starting Realtor.com scrape", address=address, search_url=search_url)

        async with async_playwright() as p:
            page, browser, context = await self._get_stealth_page(p)
            try:
                # First, perform a search to find the property's canonical URL
                await page.goto(search_url, timeout=settings.REQUEST_TIMEOUT * 1000)

                # Often, the search redirects directly to the property page if it's a unique match.
                # Or we might need to click the first result. For simplicity, we'll assume a direct match or redirect.
                # A more robust solution would be to find the first result link and click it.
                property_url = page.url
                if "/search/" in property_url:
                    logger.info("Search page detected, attempting to click first result.")
                    first_result_selector = '[data-testid="property-card-link"]'
                    if await page.locator(first_result_selector).count() > 0:
                        await page.locator(first_result_selector).first.click()
                        await page.wait_for_load_state('networkidle')
                        property_url = page.url
                    else:
                        logger.warning("No property card link found on search results page.", url=property_url)
                        return {"error": "Could not find property on Realtor.com"}


                logger.info("Navigated to property page", url=property_url)

                content = await self._navigate_and_get_content(page, property_url, wait_selector='script#__NEXT_DATA__')
                if not content:
                    return {"error": "Failed to load page content."}

                json_data_text = await page.locator('script#__NEXT_DATA__').text_content()
                if not json_data_text:
                    logger.error("Could not find __NEXT_DATA__ script tag on Realtor.com.", url=property_url)
                    return {"error": "Could not find __NEXT_DATA__ script tag."}

                data = json.loads(json_data_text)
                parsed_data = self._parse_next_data(data)

                return {"raw_payload": data, "parsed_data": parsed_data}

            except Exception as e:
                logger.error("An error occurred during Realtor.com scraping", error=str(e), exc_info=True)
                return {"error": str(e)}
            finally:
                await browser.close()

    def _parse_next_data(self, data: dict) -> dict:
        """
        Parses the __NEXT_DATA__ from Realtor.com.
        """
        try:
            # Path to property details can vary, this is based on observation
            property_data = data.get("props", {}).get("pageProps", {}).get("initialReduxState", {}).get("property", {}).get("detailsV2", {})
            if not property_data:
                property_data = data.get("props", {}).get("pageProps", {}).get("property", {}) # Alternative path

            if not property_data:
                 return {"error": "Property data not found in __NEXT_DATA__"}

            # Realtor provides multiple AVMs
            estimates = property_data.get('estimates', [])
            sale_avm = None
            if estimates:
                # Take the first available estimate as the primary one
                sale_avm = self._to_int(estimates[0].get('estimate'))

            return {
                "sale_avm": sale_avm,
                "rent_avm": None, # Realtor.com doesn't typically provide a direct rental AVM on sales pages
                "beds": self._to_float(property_data.get('beds')),
                "baths": self._to_float(property_data.get('baths_full')),
                "sqft": self._to_int(property_data.get('sqft')),
                "lot_sqft": self._to_int(property_data.get('lot_sqft')),
                "year_built": self._to_int(property_data.get('year_built')),
                "property_type": self._clean_text(property_data.get('type')),
            }
        except (json.JSONDecodeError, AttributeError, KeyError, IndexError) as e:
            logger.error("Failed to parse Realtor.com __NEXT_DATA__", error=str(e))
            return {"error": f"Parsing error: {e}"}

import json
from playwright.async_api import async_playwright
from scrapers.base_scraper import BaseScraper
from logging_config import setup_logging
from config import settings

logger = setup_logging()

class MovotoScraper(BaseScraper):
    def __init__(self):
        super().__init__("Movoto")

    async def scrape(self, address: str) -> dict:
        """
        Scrapes property data from Movoto.com by searching and then parsing the __NEXT_DATA__ JSON blob.
        """
        search_url = f"https://www.movoto.com/search/real_estate/{address.replace(' ', '-')}/"
        logger.info("Starting Movoto scrape", address=address, search_url=search_url)

        async with async_playwright() as p:
            page, browser, context = await self._get_stealth_page(p)
            try:
                # First, perform a search to find the property's canonical URL
                await page.goto(search_url, timeout=settings.REQUEST_TIMEOUT * 1000)

                # Movoto might redirect directly, or we might need to click the first result.
                property_url = page.url
                if "/search/" in property_url:
                    logger.info("Search page detected, attempting to click first result.")
                    # This selector targets the link within the first property card. It's fragile.
                    first_result_selector = 'a[data-context="card-anchor"]'
                    if await page.locator(first_result_selector).count() > 0:
                        await page.locator(first_result_selector).first.click()
                        await page.wait_for_load_state('networkidle')
                        property_url = page.url
                    else:
                        logger.warning("No property card link found on Movoto search results page.", url=property_url)
                        return {"error": "Could not find property on Movoto.com"}

                logger.info("Navigated to property page", url=property_url)

                content = await self._navigate_and_get_content(page, property_url, wait_selector='script#__NEXT_DATA__')
                if not content:
                    return {"error": "Failed to load page content."}

                json_data_text = await page.locator('script#__NEXT_DATA__').text_content()
                if not json_data_text:
                    logger.error("Could not find __NEXT_DATA__ script tag on Movoto.", url=property_url)
                    return {"error": "Could not find __NEXT_DATA__ script tag."}

                data = json.loads(json_data_text)
                parsed_data = self._parse_next_data(data)

                return {"raw_payload": data, "parsed_data": parsed_data}

            except Exception as e:
                logger.error("An error occurred during Movoto scraping", error=str(e), exc_info=True)
                return {"error": str(e)}
            finally:
                await browser.close()

    def _parse_next_data(self, data: dict) -> dict:
        """
        Parses the __NEXT_DATA__ from Movoto.com.
        NOTE: This is based on inspecting the JSON and is highly subject to change.
        """
        try:
            property_data = data.get("props", {}).get("pageProps", {}).get("pageData", {}).get("property", {})
            if not property_data:
                 return {"error": "Property data not found in __NEXT_DATA__"}

            details = property_data.get("details", {})

            return {
                "sale_avm": self._to_int(details.get("avm", {}).get("avm")),
                "rent_avm": None, # Movoto does not seem to provide a rental AVM.
                "beds": self._to_float(details.get("beds")),
                "baths": self._to_float(details.get("baths")),
                "sqft": self._to_int(details.get("sqft")),
                "lot_sqft": self._to_int(details.get("lotSize", {}).get("value")),
                "year_built": self._to_int(details.get("yearBuilt")),
                "property_type": self._clean_text(details.get("propertyType")),
                "last_sale_price": self._to_int(property_data.get("priceHistory", [])[0].get("price")) if property_data.get("priceHistory") else None,
            }
        except (json.JSONDecodeError, AttributeError, KeyError, IndexError) as e:
            logger.error("Failed to parse Movoto.com __NEXT_DATA__", error=str(e))
            return {"error": f"Parsing error: {e}"}

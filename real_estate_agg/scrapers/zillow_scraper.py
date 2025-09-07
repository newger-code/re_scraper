import json
from playwright.async_api import async_playwright
from scrapers.base_scraper import BaseScraper
from logging_config import setup_logging

logger = setup_logging()

class ZillowScraper(BaseScraper):
    def __init__(self):
        super().__init__("Zillow")

    async def scrape(self, address: str) -> dict:
        """
        Scrapes property data from Zillow by finding the embedded __NEXT_DATA__ JSON blob.
        """
        url = f"https://www.zillow.com/homes/{address.replace(' ', '-')}_rb/"
        logger.info("Starting Zillow scrape", address=address, url=url)

        async with async_playwright() as p:
            page, browser, context = await self._get_stealth_page(p)
            try:
                content = await self._navigate_and_get_content(page, url, wait_selector='script#__NEXT_DATA__')
                if not content:
                    return {"error": "Failed to load page content."}

                # Use Playwright's evaluation to parse the JSON directly in the browser context
                json_data_text = await page.locator('script#__NEXT_DATA__').text_content()
                if not json_data_text:
                    logger.error("Could not find __NEXT_DATA__ script tag.", url=url)
                    return {"error": "Could not find __NEXT_DATA__ script tag."}

                data = json.loads(json_data_text)
                parsed_data = self._parse_next_data(data)

                return {"raw_payload": data, "parsed_data": parsed_data}

            except Exception as e:
                logger.error("An error occurred during Zillow scraping", error=str(e), exc_info=True)
                return {"error": str(e)}
            finally:
                await browser.close()

    def _parse_next_data(self, data: dict) -> dict:
        """
        Parses the complex __NEXT_DATA__ JSON object to extract key property details.
        This function is brittle and will need maintenance if Zillow changes its structure.
        """
        try:
            # The property data is often nested deep within the JSON structure.
            # This path is based on current observations and may change.
            gdp_client_cache_str = data.get("props", {}).get("pageProps", {}).get("componentProps", {}).get("gdpClientCache")
            if not gdp_client_cache_str:
                return {"error": "gdpClientCache not found in __NEXT_DATA__"}

            gdp_client_cache = json.loads(gdp_client_cache_str)

            # The key is dynamic, so we find the first key in the dictionary that looks like a ZPID
            property_key = next((key for key in gdp_client_cache if key.startswith('zpid_')), None)
            if not property_key:
                 property_key = next(iter(gdp_client_cache), None) # Fallback to first key

            if not property_key:
                 return {"error": "Property key not found in gdpClientCache"}

            property_data = gdp_client_cache.get(property_key, {}).get("property", {})
            if not property_data:
                return {"error": "Property data not found"}

            zestimate = property_data.get("zestimate")
            rent_zestimate = property_data.get("rentZestimate")

            return {
                "sale_avm": self._to_int(zestimate),
                "rent_avm": self._to_int(rent_zestimate),
                "beds": self._to_float(property_data.get("bedrooms")),
                "baths": self._to_float(property_data.get("bathrooms")),
                "sqft": self._to_int(property_data.get("livingArea")),
                "lot_sqft": self._to_int(property_data.get("lotSize")),
                "year_built": self._to_int(property_data.get("yearBuilt")),
                "property_type": self._clean_text(property_data.get("homeType")),
                "last_sale_price": self._to_int(property_data.get("lastSoldPrice")),
                "last_sale_date": property_data.get("lastSoldDate"), # Will need parsing
                "property_tax_amount": self._to_int(property_data.get("annualHomeownersInsurance")), # Example, path may differ
            }

        except (json.JSONDecodeError, StopIteration, AttributeError, KeyError) as e:
            logger.error("Failed to parse Zillow __NEXT_DATA__", error=str(e))
            return {"error": f"Parsing error: {e}"}

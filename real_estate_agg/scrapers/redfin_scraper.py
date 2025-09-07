import json
import re
from playwright.async_api import async_playwright
from scrapers.base_scraper import BaseScraper
from logging_config import setup_logging
from config import settings

logger = setup_logging()

class RedfinScraper(BaseScraper):
    def __init__(self):
        super().__init__("Redfin")

    async def scrape(self, address: str) -> dict:
        """
        Scrapes Redfin using a two-step process:
        1. Visit the property page to get internal IDs.
        2. Call the internal '/stingray/' API to get structured JSON data.
        """
        # Redfin URL format is more structured. This is a best-guess construction.
        # A more robust method might involve a search first to get the exact URL.
        url_address = address.lower().replace(' ', '-').replace(',', '')
        # This initial info URL seems to be a reliable way to get property/listing IDs
        initial_page_url = f"https://www.redfin.com/stingray/do/v2/public/initial-info?path=/{url_address}"
        logger.info("Starting Redfin scrape", address=address, initial_url=initial_page_url)

        async with async_playwright() as p:
            page, browser, context = await self._get_stealth_page(p)
            try:
                # Step 1: Get initial info to find propertyId and listingId
                await page.goto(initial_page_url, timeout=settings.REQUEST_TIMEOUT * 1000)
                content = await page.content()

                # The response is often a JSON object wrapped in HTML, need to clean it
                json_text_match = re.search(r'>({.*})<', content)
                if not json_text_match:
                    logger.error("Could not find initial info JSON in Redfin response.", url=initial_page_url)
                    return {"error": "Could not find initial info JSON."}

                # The response starts with {}&& - we need to strip it
                cleaned_json_text = json_text_match.group(1).replace('{}&&', '')
                initial_data = json.loads(cleaned_json_text)
                payload = initial_data.get('payload', {})

                # propertyId is crucial for subsequent API calls
                property_id = payload.get('propertyId')
                # listingId may or may not be present, but is good to have
                listing_id = payload.get('listingId', '0') # Use '0' if not found

                if not property_id:
                    logger.error("propertyId not found in Redfin initial info.", url=initial_page_url)
                    return {"error": "propertyId not found."}

                # Step 2: Use IDs to call other APIs for detailed data
                # This API provides most of the core data
                api_url = f"https://www.redfin.com/stingray/api/home/details/main-info?propertyId={property_id}&accessLevel=1"

                await page.goto(api_url, timeout=settings.REQUEST_TIMEOUT * 1000)
                api_content = await page.text_content()

                cleaned_api_content = api_content.replace('{}&&', '')
                api_data = json.loads(cleaned_api_content)

                parsed_data = self._parse_api_data(api_data)

                return {"raw_payload": api_data, "parsed_data": parsed_data}

            except Exception as e:
                logger.error("An error occurred during Redfin scraping", error=str(e), exc_info=True)
                return {"error": str(e)}
            finally:
                await browser.close()

    def _parse_api_data(self, data: dict) -> dict:
        """
        Parses the JSON response from Redfin's main-info API.
        """
        try:
            payload = data.get('payload', {})
            property_data = payload.get('propertyData', {})
            avm_details = payload.get('marketSourcedData', {}).get('predictedValue', {})
            rental_avm = payload.get('rentalEstimate', {})

            return {
                "sale_avm": self._to_int(avm_details.get('predictedValue')),
                "rent_avm": self._to_int(rental_avm.get('rentalEstimate')),
                "beds": self._to_float(property_data.get('numBeds')),
                "baths": self._to_float(property_data.get('numBaths')),
                "sqft": self._to_int(property_data.get('sqFt', {}).get('value')),
                "lot_sqft": self._to_int(property_data.get('lotSize', {}).get('value')),
                "year_built": self._to_int(property_data.get('yearBuilt')),
                "property_type": self._clean_text(property_data.get('propertyTypeWithCondo')),
                "last_sale_price": self._to_int(payload.get('publicRecordsInfo', {}).get('lastSalePriceData', {}).get('lastSoldPrice')),
            }
        except (json.JSONDecodeError, AttributeError, KeyError) as e:
            logger.error("Failed to parse Redfin API data", error=str(e))
            return {"error": f"Parsing error: {e}"}

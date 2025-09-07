import asyncio
from scrapers.spatialest_scraper import SpatialestScraper

async def main():
    """
    Runs the Spatialest scraper for investigation.
    """
    mecklenburg_url = "https://property.spatialest.com/nc/mecklenburg/"
    address = "1240 Pondview Ave, Akron, OH 44305" # This address is not in Mecklenburg, but it's fine for testing the search form.

    scraper = SpatialestScraper("Mecklenburg", mecklenburg_url)
    await scraper.scrape(address)

if __name__ == "__main__":
    asyncio.run(main())

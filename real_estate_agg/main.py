import asyncio
import uvicorn
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from typing import List

from sqlalchemy.orm import Session
from database import init_db, get_db, Property, Source, RawSnapshot
from utils.address_normalizer import normalize_address
from logging_config import setup_logging
from scrapers.zillow_scraper import ZillowScraper
from scrapers.redfin_scraper import RedfinScraper
from scrapers.realtor_scraper import RealtorScraper
from scrapers.movoto_scraper import MovotoScraper

# --- FastAPI App Initialization ---
app = FastAPI(
    title="Real Estate Data Aggregation Platform",
    description="An API to trigger and manage real estate data scraping.",
    version="1.0.0"
)
logger = setup_logging()

# --- Pydantic Models ---
class ScrapeRequest(BaseModel):
    addresses: List[str]

class CountyScrapeRequest(BaseModel):
    address: str

# --- Event Handlers ---
@app.on_event("startup")
def on_startup():
    """Initialize the database on application startup."""
    logger.info("Application starting up. Initializing database...")
    init_db()
    logger.info("Database initialized.")

# --- API Endpoints ---
@app.get("/", tags=["Health Check"])
def read_root():
    """Root endpoint for basic health check."""
    return {"status": "ok", "message": "Welcome to the Real Estate Data Aggregator API"}

@app.post("/scrape", status_code=202, tags=["Scraping"])
async def trigger_scrape(request: ScrapeRequest, background_tasks: BackgroundTasks):
    """
    Accepts a list of addresses and triggers the commercial scraping process (Zillow, etc.) in the background.
    """
    logger.info("Received scrape request for addresses", addresses=request.addresses)
    for address in request.addresses:
        background_tasks.add_task(process_property, address)

    return {"message": "Scraping process initiated in the background.", "addresses": request.addresses}

@app.post("/scrape-county", tags=["Scraping"])
def trigger_county_scrape(request: CountyScrapeRequest):
    """
    Accepts a single address and attempts to fetch data from county sources (ArcGIS or LLM fallback).
    This is a synchronous endpoint that returns the result directly.
    """
    from county_data_extractor import get_county_data

    logger.info("Received county scrape request for address", address=request.address)
    normalized_address = normalize_address(request.address)
    county_data = get_county_data(normalized_address)

    return county_data

from etl import run_master_etl

@app.post("/run-etl", status_code=202, tags=["ETL"])
async def trigger_etl(background_tasks: BackgroundTasks):
    """
    Scans for all 'ingested' snapshots and runs the ETL process for each one in the background.
    """
    logger.info("ETL process triggered via API.")
    background_tasks.add_task(run_master_etl)
    return {"message": "ETL process for all ingested snapshots initiated in the background."}

# --- Core Scraping Logic (modified for background tasks) ---

async def run_scraper_for_property(db: Session, property_id: int, address_to_scrape: str, scraper_instance):
    """
    Runs a single scraper for a single property and saves the raw result.
    This function uses the database session passed into it.
    """
    source_name = scraper_instance.source_name
    logger.info("Running scraper for property", property_id=property_id, source=source_name)

    try:
        source = db.query(Source).filter(Source.name == source_name).first()
        if not source:
            logger.error("Source not found in database", source_name=source_name)
            return

        result = await scraper_instance.scrape(address_to_scrape)

        if result and not result.get("error"):
            raw_payload = result.get("raw_payload", {})
            parsed_data = result.get("parsed_data", {})

            snapshot = RawSnapshot(
                property_id=property_id,
                source_id=source.id,
                raw_payload=raw_payload,
                status="ingested"
            )
            db.add(snapshot)
            db.commit()
            db.refresh(snapshot)
            logger.info("Successfully scraped and saved snapshot.", property_id=property_id, source=source_name, snapshot_id=snapshot.id)

            # The ETL process is now decoupled and run via a separate API endpoint.

        else:
            logger.error("Scraper returned an error or no result.", property_id=property_id, source=source_name, result=result)

    except Exception as e:
        logger.critical(
            "A critical, unhandled exception occurred in a scraper.",
            property_id=property_id,
            source=source_name,
            error=str(e),
            exc_info=True
        )
        db.rollback()


async def process_property(input_address: str):
    """
    Processes a single property: normalizes, saves, and triggers all scrapers.
    This function manages a single DB session for its entire lifecycle.
    """
    db_gen = get_db()
    db = next(db_gen)

    try:
        # Step 1: Normalize Address
        normalized = normalize_address(input_address)
        logger.info("Normalized address", input_address=input_address, normalized=normalized['canonical'])

        # Step 2: Get or Create Property Record in DB
        property_record = db.query(Property).filter(Property.input_address == input_address).first()
        if not property_record:
            property_record = Property(
                input_address=input_address,
                canonical_address=normalized['canonical'],
                address_components=normalized['components']
            )
            db.add(property_record)
            db.commit()
            db.refresh(property_record)
            logger.info("Created new property record in DB.", property_id=property_record.id)
        else:
            logger.info("Found existing property record in DB.", property_id=property_record.id)

        if not property_record:
            logger.error("Failed to get or create property record.", input_address=input_address)
            return

        # Step 3: Initialize and run all scrapers concurrently
        scrapers = [
            ZillowScraper(),
            RedfinScraper(),
            RealtorScraper(),
            MovotoScraper(),
        ]

        address_to_scrape = property_record.canonical_address or property_record.input_address
        tasks = [run_scraper_for_property(db, property_record.id, address_to_scrape, s) for s in scrapers]
        await asyncio.gather(*tasks)
    finally:
        db.close()

# --- Uvicorn Runner ---
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

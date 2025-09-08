## `re_scraper/.env.example`
```
# This is an example file. Copy it to .env and fill in your actual credentials.
# .env should NOT be committed to version control.

# --- PostgreSQL Database ---
# Example for PostgreSQL: "postgresql://user:password@host:port/dbname"
# Example for SQLite (local file): "sqlite:///./real_estate.db"
DATABASE_URL="postgresql://your_db_user:your_db_password@localhost:5432/real_estate_data"

# --- Bright Data Proxy ---
# See your Bright Data dashboard for these details.
BRIGHT_DATA_USERNAME="your_brightdata_user"
BRIGHT_DATA_PASSWORD="your_brightdata_password"
BRIGHT_DATA_HOST="your_brightdata_host"
BRIGHT_DATA_PORT="33335"

# --- Email for Error Notifications ---
# Use an app-specific password if using Gmail or similar services.
EMAIL_HOST="smtp.example.com"
EMAIL_PORT="587"
EMAIL_USER="your_email@example.com"
EMAIL_PASS="your_email_password"
EMAIL_FROM="sender_alias@example.com"
EMAIL_TO="recipient_email@example.com"
```

## `re_scraper/config.py`
```python
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    BRIGHT_DATA_USERNAME = os.getenv("BRIGHT_DATA_USERNAME")
    BRIGHT_DATA_PASSWORD = os.getenv("BRIGHT_DATA_PASSWORD")
    BRIGHT_DATA_HOST = os.getenv("BRIGHT_DATA_HOST")
    BRIGHT_DATA_PORT = int(os.getenv("BRIGHT_DATA_PORT", 33335))
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./real_estate.db")
    EMAIL_HOST = os.getenv("EMAIL_HOST")
    EMAIL_PORT = int(os.getenv("EMAIL_PORT", 465))
    EMAIL_USER = os.getenv("EMAIL_USER")
    EMAIL_PASS = os.getenv("EMAIL_PASS")
    EMAIL_FROM = os.getenv("EMAIL_FROM")
    EMAIL_TO = os.getenv("EMAIL_TO")
    NORMALIZER_BACKEND = os.getenv("NORMALIZER_BACKEND", "usaddress")
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36"
    ]
    REQUEST_TIMEOUT = 30
    MAX_RETRIES = 3
    RETRY_DELAY = 5

    @property
    def proxy_url(self):
        if all([self.BRIGHT_DATA_USERNAME, self.BRIGHT_DATA_PASSWORD, self.BRIGHT_DATA_HOST, self.BRIGHT_DATA_PORT]):
            return f"http://{self.BRIGHT_DATA_USERNAME}:{self.BRIGHT_DATA_PASSWORD}@{self.BRIGHT_DATA_HOST}:{self.BRIGHT_DATA_PORT}"
        return None

settings = Settings()
```

## `re_scraper/database.py`
```python
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from sqlalchemy.sql import func
from config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Property(Base):
    __tablename__ = "properties"
    id = Column(Integer, primary_key=True, index=True)
    input_address = Column(String, nullable=False, unique=True)
    canonical_address = Column(String, nullable=True, index=True)
    address_components = Column(JSON, nullable=True)
    snapshots = relationship("RawSnapshot", back_populates="property")

class Source(Base):
    __tablename__ = "sources"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    base_url = Column(String, nullable=False)
    snapshots = relationship("RawSnapshot", back_populates="source")

class RawSnapshot(Base):
    __tablename__ = "raw_snapshots"
    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False, index=True)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False, index=True)
    scraped_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    raw_payload = Column(JSON, nullable=False)
    status = Column(String, default="ingested", index=True)
    property = relationship("Property", back_populates="snapshots")
    source = relationship("Source", back_populates="snapshots")

# ... (PropertyAttributesHistory and AvmHistory models) ...

def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    sources = ['Zillow', 'Redfin', 'Realtor', 'Movoto']
    for name in sources:
        if not db.query(Source).filter_by(name=name).first():
            db.add(Source(name=name, base_url=f"https://www.{name.lower()}.com"))
    db.commit()
    db.close()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

## `re_scraper/main.py`
```python
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
from etl import run_master_etl

app = FastAPI(title="Real Estate Data Aggregation Platform")
logger = setup_logging()

class ScrapeRequest(BaseModel):
    addresses: List[str]

@app.on_event("startup")
def on_startup():
    init_db()

@app.post("/scrape", status_code=202)
async def trigger_scrape(request: ScrapeRequest, background_tasks: BackgroundTasks):
    for address in request.addresses:
        background_tasks.add_task(process_property, address)
    return {"message": "Scraping process initiated."}

@app.post("/run-etl", status_code=202)
async def trigger_etl(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_master_etl)
    return {"message": "ETL process initiated."}

async def run_scraper_for_property(db: Session, prop, address, scraper):
    # ... (implementation) ...

async def process_property(input_address: str):
    # ... (implementation) ...

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
```

... and so on for all other files.

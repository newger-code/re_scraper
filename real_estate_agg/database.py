from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, JSON, Index
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from sqlalchemy.sql import func
from config import settings

# Create the SQLAlchemy engine
engine = create_engine(settings.DATABASE_URL)

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for declarative models
Base = declarative_base()

class Property(Base):
    __tablename__ = "properties"
    id = Column(Integer, primary_key=True, index=True)
    input_address = Column(String, nullable=False, unique=True)
    canonical_address = Column(String, nullable=True, index=True)
    address_components = Column(JSON, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

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
    status = Column(String, default="ingested", index=True) # ingested, processed, error

    property = relationship("Property", back_populates="snapshots")
    source = relationship("Source", back_populates="snapshots")

class PropertyAttributesHistory(Base):
    __tablename__ = "property_attributes_history"
    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False, index=True)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False, index=True)
    beds = Column(Float, nullable=True)
    baths = Column(Float, nullable=True)
    sqft = Column(Integer, nullable=True)
    lot_sqft = Column(Integer, nullable=True)
    year_built = Column(Integer, nullable=True)
    property_type = Column(String, nullable=True)
    last_sale_date = Column(DateTime(timezone=True), nullable=True)
    last_sale_price = Column(Integer, nullable=True)
    property_tax_amount = Column(Integer, nullable=True)
    property_tax_year = Column(Integer, nullable=True)
    valid_from = Column(DateTime(timezone=True), server_default=func.now())
    valid_to = Column(DateTime(timezone=True), nullable=True, index=True)
    is_current = Column(Integer, default=1, index=True) # 1 for current, 0 for historical

class AvmHistory(Base):
    __tablename__ = "avm_history"
    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False, index=True)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False, index=True)
    avm_provider = Column(String, nullable=False)
    valuation_type = Column(String, nullable=False)  # 'sale' or 'rent'
    value = Column(Integer, nullable=False)
    date_recorded = Column(DateTime(timezone=True), server_default=func.now(), index=True)

def init_db():
    """Initializes the database and creates tables."""
    Base.metadata.create_all(bind=engine)
    # Pre-populate sources if they don't exist
    db = SessionLocal()
    sources_to_add = [
        {'name': 'Zillow', 'base_url': 'https://www.zillow.com'},
        {'name': 'Redfin', 'base_url': 'https://www.redfin.com'},
        {'name': 'Realtor', 'base_url': 'https://www.realtor.com'},
        {'name': 'Movoto', 'base_url': 'https://www.movoto.com'},
    ]
    for src in sources_to_add:
        exists = db.query(Source).filter_by(name=src['name']).first()
        if not exists:
            db.add(Source(**src))
    db.commit()
    db.close()

def get_db():
    """Dependency to get a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

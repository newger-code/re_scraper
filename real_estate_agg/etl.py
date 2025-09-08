from sqlalchemy.orm import Session
from database import get_db, RawSnapshot, PropertyAttributesHistory, AvmHistory
from logging_config import setup_logging

logger = setup_logging()

def run_master_etl():
    """
    Finds all 'ingested' snapshots and runs the ETL process on them.
    """
    db_gen = get_db()
    db = next(db_gen)
    try:
        snapshots_to_process = db.query(RawSnapshot).filter(RawSnapshot.status == 'ingested').all()
        logger.info(f"Found {len(snapshots_to_process)} snapshots to process.")
        for snapshot in snapshots_to_process:
            if not snapshot.raw_payload:
                logger.warning("Snapshot has no raw_payload, skipping ETL.", snapshot_id=snapshot.id)
                continue

            parsed_data = snapshot.raw_payload.get("parsed_data", {})
            run_etl(db, snapshot, parsed_data)
    finally:
        db.close()

def run_etl(db: Session, snapshot: RawSnapshot, parsed_data: dict):
    """
    Runs the ETL process for a given snapshot and its already-parsed data.
    """
    if not parsed_data or parsed_data.get("error"):
        logger.error("ETL Error: Parsed data contains an error or is empty.", snapshot_id=snapshot.id, error=parsed_data.get("error"))
        snapshot.status = "error"
        db.commit()
        return

    source_name = snapshot.source.name
    logger.info("Running ETL for snapshot", snapshot_id=snapshot.id, source=source_name)

    try:
        # --- Populate PropertyAttributesHistory ---
        db.query(PropertyAttributesHistory).\
            filter(
                PropertyAttributesHistory.property_id == snapshot.property_id,
                PropertyAttributesHistory.source_id == snapshot.source_id,
                PropertyAttributesHistory.is_current == 1
            ).\
            update({"is_current": 0, "valid_to": snapshot.scraped_at})

        new_attributes = PropertyAttributesHistory(
            property_id=snapshot.property_id,
            source_id=snapshot.source_id,
            beds=parsed_data.get("beds"),
            baths=parsed_data.get("baths"),
            sqft=parsed_data.get("sqft"),
            lot_sqft=parsed_data.get("lot_sqft"),
            year_built=parsed_data.get("year_built"),
            property_type=parsed_data.get("property_type"),
            last_sale_price=parsed_data.get("last_sale_price"),
            property_tax_amount=parsed_data.get("property_tax_amount"),
            valid_from=snapshot.scraped_at,
            is_current=1
        )
        db.add(new_attributes)

        # --- Populate AvmHistory ---
        if parsed_data.get("sale_avm"):
            sale_avm = AvmHistory(
                property_id=snapshot.property_id,
                source_id=snapshot.source_id,
                avm_provider=source_name,
                valuation_type="sale",
                value=parsed_data["sale_avm"],
                date_recorded=snapshot.scraped_at
            )
            db.add(sale_avm)

        if parsed_data.get("rent_avm"):
            rent_avm = AvmHistory(
                property_id=snapshot.property_id,
                source_id=snapshot.source_id,
                avm_provider=source_name,
                valuation_type="rent",
                value=parsed_data["rent_avm"],
                date_recorded=snapshot.scraped_at
            )
            db.add(rent_avm)

        snapshot.status = "processed"
        db.commit()
        logger.info("ETL process completed successfully.", snapshot_id=snapshot.id)

    except Exception as e:
        logger.critical("A critical error occurred during the ETL process", snapshot_id=snapshot.id, error=str(e), exc_info=True)
        db.rollback()

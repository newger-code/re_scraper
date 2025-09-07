from arcgis.gis import GIS
from arcgis.features import FeatureLayer
import google.generativeai as genai
from config import settings
from logging_config import setup_logging

logger = setup_logging()

# --- Hardcoded County to ArcGIS Server URL Mapping ---
COUNTY_ARCGIS_ENDPOINTS = {
    "cook county": "https://wwws.cookcountyil.gov/cookviewer/rest/services/cookviewer_query/MapServer",
    # ... more counties would be added here
}

def get_data_from_arcgis(county: str, address: str) -> dict:
    """
    Connects to a county's ArcGIS server and queries for parcel data.
    """
    endpoint = COUNTY_ARCGIS_ENDPOINTS.get(county.lower())
    if not endpoint:
        logger.warning("No ArcGIS endpoint configured for county", county=county)
        return None

    try:
        gis = GIS() # Anonymous connection
        layer_url = f"{endpoint}/0" # A common pattern is that the first layer (index 0) is the parcel layer.
        feature_layer = FeatureLayer(layer_url, gis)

        logger.info("Attempting to query ArcGIS feature layer", layer_url=layer_url)

        # This is a guess for the field name. Common names are 'SITE_ADDRESS', 'FULL_ADDR', etc.
        # This will need to be customized for each county's schema.
        where_clause = f"upper(SITE_ADDRESS) = '{address.upper()}'"

        parcels = feature_layer.query(where=where_clause, out_fields='*')

        if len(parcels.features) > 0:
            parcel = parcels.features[0]
            attributes = parcel.attributes
            logger.info("Found parcel data on ArcGIS server", attributes=attributes)
            # Map the attributes to our internal schema
            return {
                "source": "arcgis",
                "assessed_value": attributes.get("ASSESSED_VALUE_FIELD_NAME"), # Placeholder field name
                "owner": attributes.get("OWNER_NAME_FIELD_NAME") # Placeholder field name
            }
        else:
            logger.warning("No parcel found for address on ArcGIS server", address=address)
            return None

    except Exception as e:
        logger.error("Failed to get data from ArcGIS", county=county, error=str(e), exc_info=True)
        return None

def get_data_with_llm(county: str, address: str) -> dict:
    # ... (rest of the file is unchanged) ...
    return {"error": "Not implemented"}


def get_county_data(normalized_address: dict) -> dict:
    """
    Main entry point for acquiring county-level data for a property.
    It orchestrates the dual-strategy approach.

    Our target schema for the returned dictionary is:
    - parcel_id: The unique county identifier (APN/PIN).
    - full_address: The property's location address.
    - legal_description: The legal description of the property.
    - land_use_code: e.g., Residential, Commercial.
    - property_class: e.g., Single Family, Condo.
    - acreage or lot_size_sqft.
    - building_sqft.
    - year_built.
    - market_value: Total assessed market value.
    - assessed_value: The value used for tax calculations.
    - tax_year.
    - annual_property_tax.
    - last_sale_date.
    - last_sale_price.
    - taxes_owed_or_due.
    - last_tax_amount_paid.
    - last_tax_paid_date.
    - delinquent_tax_amount.
    - notice_of_default_date.
    - owner_name.
    - owner_mailing_address.
    - tax_mailing_address.
    - mortgage_amount.
    - mortgage_date.
    - lender_name.
    """
    if not normalized_address or not normalized_address.get('components'):
        return {"error": "Invalid normalized address provided."}

    components = normalized_address['components']
    county = components.get('county')
    full_address = normalized_address.get('canonical')

    if not county:
        logger.warning("County not found in normalized address components.", address=full_address)
        return {"error": "County not found in address"}

    logger.info("Starting county data extraction", county=county, address=full_address)

    # 1. Try the primary strategy: ArcGIS API
    arcgis_data = get_data_from_arcgis(county, full_address)
    if arcgis_data:
        logger.info("Successfully retrieved data from ArcGIS", county=county)
        return arcgis_data

    # 2. If that fails, try the fallback strategy: LLM scraping
    llm_data = get_data_with_llm(county, full_address)
    if llm_data and not llm_data.get("error"):
        logger.info("Successfully retrieved data using LLM fallback", county=county)
        return llm_data

    logger.error("All county data extraction strategies failed.", county=county, address=full_address)
    return {"error": "All county data extraction strategies failed"}

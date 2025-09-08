import requests
import zipfile
import geopandas
import os
from io import BytesIO
from logging_config import setup_logging

logger = setup_logging()

# A map of county names to their bulk data download URLs.
COUNTY_BULK_DATA_URLS = {
    "summit county": "https://fiscaloffice.summitoh.net/index.php/component/jdownloads/finish/68-parcels/503-parcels"
}

def download_and_process_county_data(county: str) -> bool:
    """
    Downloads, unzips, and processes a county's bulk parcel data.
    """
    county_lower = county.lower()
    if county_lower not in COUNTY_BULK_DATA_URLS:
        logger.warning("No bulk data URL configured for county", county=county)
        return False

    url = COUNTY_BULK_DATA_URLS[county_lower]

    try:
        logger.info("Downloading bulk data", county=county, url=url)
        response = requests.get(url, stream=True)
        response.raise_for_status()

        zip_file = BytesIO(response.content)

        temp_dir = f"/tmp/{county_lower}_parcels"
        os.makedirs(temp_dir, exist_ok=True)

        with zipfile.ZipFile(zip_file) as zf:
            zf.extractall(temp_dir)
            logger.info("Successfully extracted zip file", path=temp_dir)

        shapefile_path = None
        for file in os.listdir(temp_dir):
            if file.endswith(".shp"):
                shapefile_path = os.path.join(temp_dir, file)
                break

        if not shapefile_path:
            logger.error("No .shp file found in the extracted archive.", county=county)
            return False

        logger.info("Reading shapefile with geopandas", path=shapefile_path)
        gdf = geopandas.read_file(shapefile_path)

        print(f"--- {county.upper()} PARCEL DATA (HEAD) ---")
        print(gdf.head())
        print("------------------------------------------")

        return True

    except requests.exceptions.RequestException as e:
        logger.error("Failed to download bulk data file", county=county, error=str(e))
        return False
    except zipfile.BadZipFile:
        logger.error("Downloaded file is not a valid zip file.", county=county)
        return False
    except Exception as e:
        logger.error("An error occurred during bulk data processing", county=county, error=str(e), exc_info=True)
        return False

def get_county_data(county_name: str) -> dict:
    """
    Main entry point for acquiring county-level data.
    """
    success = download_and_process_county_data(county_name)
    if success:
        return {"status": "success", "message": f"Successfully processed bulk data for {county_name}."}
    else:
        return {"status": "error", "message": f"Failed to process bulk data for {county_name}."}

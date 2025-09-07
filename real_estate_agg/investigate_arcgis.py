from arcgis.gis import GIS
from arcgis.features import FeatureLayer
from arcgis.mapping import MapImageLayer

def investigate_cook_county():
    """
    Connects to the Cook County ArcGIS server and prints information
    about its layers and fields to help with development.
    """
    print("--- Starting ArcGIS Investigation for Cook County ---")

    endpoint = "https://wwws.cookcountyil.gov/cookviewer/rest/services/cookviewer_query/MapServer"

    try:
        # Use an anonymous connection
        gis = GIS()
        map_service = MapImageLayer(endpoint, gis)

        print(f"Successfully connected to Map Service.")
        print("\n--- Layers ---")
        for layer in map_service.layers:
            print(f"Layer: {layer.properties.name} (ID: {layer.properties.id})")

            # Let's inspect the fields of a promising layer
            # Looking for layers with "Tax" or "Parcel" in the name.
            if "tax" in layer.properties.name.lower() or "parcel" in layer.properties.name.lower() or "pin" in layer.properties.name.lower():
                print("  --- Inspecting Fields for Promising Layer ---")
                try:
                    # We need a FeatureLayer object to inspect fields in detail
                    feature_layer = FeatureLayer(layer.url, gis)
                    for field in feature_layer.properties.fields:
                        print(f"    - {field.name} (Type: {field.type})")
                except Exception as e:
                    print(f"    - Could not inspect fields for this layer: {e}")
                print("  -------------------------------------------")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    investigate_cook_county()

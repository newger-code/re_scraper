from config import settings

# --- INSTRUCTIONS FOR LOCAL USE ---
# To use the more accurate `pypostal` library, you must:
# 1. Have the libpostal C library installed on your local machine.
# 2. In `requirements.txt`, uncomment 'pypostal-multiarch' and run `pip install -r requirements.txt`.
# 3. In your local `.env` file, set the following variable:
#    NORMALIZER_BACKEND="pypostal"
#
# The application will default to the less accurate `usaddress` library if
# this variable is not set or if `pypostal` fails to import.

def _normalize_with_usaddress(raw_address: str) -> dict:
    """Parses address using the 'usaddress' library."""
    import usaddress
    try:
        parsed = usaddress.tag(raw_address)
        components = parsed[0]
        parts = [
            components.get('AddressNumber', ''),
            components.get('StreetNamePreDirectional', ''),
            components.get('StreetName', ''),
            components.get('StreetNamePostType', ''),
            components.get('PlaceName', ''),
            components.get('StateName', ''),
            components.get('ZipCode', '')
        ]
        canonical = ' '.join(p for p in parts if p).strip().upper()
        return {"canonical": canonical, "components": components}
    except usaddress.RepeatedLabelError:
        return {"canonical": raw_address, "components": {}}

def _normalize_with_pypostal(raw_address: str) -> dict:
    """Parses address using the 'pypostal' library."""
    from postal.expand import expand_address
    from postal.parser import parse_address
    try:
        expanded_addresses = expand_address(raw_address)
        if not expanded_addresses:
            return {"canonical": raw_address, "components": {}}

        parsed = parse_address(expanded_addresses[0])
        components = {label: value for value, label in parsed}
        parts = [
            components.get('house_number', ''),
            components.get('road', ''),
            components.get('city', ''),
            components.get('state', ''),
            components.get('postcode', '')
        ]
        canonical = ' '.join(p for p in parts if p).strip().upper()
        return {"canonical": canonical, "components": components}
    except Exception:
        return {"canonical": raw_address, "components": {}}

# --- Main Function ---
def normalize_address(raw_address: str) -> dict:
    """
    Dynamically normalizes an address based on the configured backend.
    """
    if not raw_address:
        return {"canonical": None, "components": {}}

    if settings.NORMALIZER_BACKEND == 'pypostal':
        try:
            return _normalize_with_pypostal(raw_address)
        except ImportError:
            print("WARNING: `pypostal` backend configured but not installed. Falling back to `usaddress`.")
            return _normalize_with_usaddress(raw_address)

    # Default to usaddress
    return _normalize_with_usaddress(raw_address)

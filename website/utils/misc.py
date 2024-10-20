def extract_address_components(address):
    parts = address.split(" ", 1)  # Split on the first space only
    street_number = parts[0]
    street_name = parts[1] if len(parts) > 1 else ""
    return street_number, street_name
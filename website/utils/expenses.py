from sqlalchemy import create_engine, MetaData, Table, text
from sqlalchemy.orm import sessionmaker
import re

ETJ_TAX_RATE = {
    'DURHAM CITY': 1.3099,  # $1.3099 per $100 of assessed value
    'DURHAM COUNTY': 0.7522,  # $0.7522 per $100 of assessed value
    'DURHAM COUNTY,DURHAM CITY': 1.3099,  # Same as Durham City
    'CHAPEL-HILL': 0.82,  # Approximate, adjust if needed
    'RALEIGH': 0.98,  # Approximate, adjust if needed
    'DURHAM COUNTY,RALEIGH': 0.98,  # Follows Raleigh's rate
    'DURHAM COUNTY,MORRISVILLE': 0.75,  # Lower estimate
    'MORRISVILLE': 0.75,  # Estimated for Morrisville
    'CHAPEL-HILL,DURHAM CITY': 1.3099,  # Same as Durham City
    'CARY': 1.15,  # Approximate rate
    'CHAPEL-HILL,DURHAM COUNTY': 0.82  # Uses Chapel-Hill approximation
}

MANAGEMENT_RESERVE_PCT = 8/100
MAINTENENCE_RESERVE_PCT = 4/100

ELECTRIC_PER_KWH = 13.72
KWH_USAGE_PER_SQFT = 12 # can be up to around 15
ELECTRIC_PER_SQFT = ELECTRIC_PER_KWH*KWH_USAGE_PER_SQFT

WATER_TIERS = {
    2: 2.45, # TOP LIMIT USAGE CCF: $ PER CCF
    5: 3.69,
    8: 4.05,
    15: 5.28,
    "else": 7.4
}
SEWER_COST_PER_CCF = 5.26 # $ PER CCF WATER USAGE
WATER_USAGE_PER_OCCUPANT = (3,4)

GARBAGE_COST_PER_UNIT = 24 # PER UNIT

INSURANCE_COST_PCT = 0.5/100 # PERCENT OF TOTAL PROPERTY VALUE

NATURAL_GAS_PER_SQFT_PER_HR = 0.00049836
ELECTRIC_PER_SQFT_PER_HR = 0.0015463

LAWN_CARE_PER_ACRE = (100,1600) # RANGE FROM MOWING TWICE A WEEK TO LUXURY FULL SERVICE

LEGAL_AND_PROFESSIONAL_PCT = 1.5/100 # FOR MULTI-FAMILY HOMES 

def get_tables(db_path):
    # Create the engine
    engine = create_engine(f'sqlite:///{db_path}')

    # Reflect the existing database into a new MetaData object
    metadata = MetaData()
    metadata.reflect(bind=engine)

    # Print all table names
    print(metadata.tables.keys())
    

def get_db_schema(db_path):
    
    # Create an engine that connects to the SQLite database
    engine = create_engine(f'sqlite:///{db_path}')

    # Create a session
    Session = sessionmaker(bind=engine)
    session = Session()

    # Reflect the tables from the database
    metadata = MetaData()
    metadata.reflect(bind=engine)

    # You can now access the tables and work with them
    for table_name, table in metadata.tables.items():
        print(f'Table: {table_name}')
        for column in table.columns:
            print(f'Column: {column.name}, Type: {column.type}')

    # Example: querying a table (replace 'your_table' with an actual table name)
    your_table = Table('your_table_name', metadata, autoload_with=engine)
    results = session.query(your_table).all()

    # for row in results:
    #     print(row)
    
def query_db(db_path, query):
    engine = create_engine(f'sqlite:///{db_path}')
    with engine.connect() as connection:
        result = connection.execute(text(query))
        rows = result.fetchall()
    for row in rows:
        print(row)
    print(f"\n There are {len(rows)} rows")

def estimate_water_cost(num_occupants, water_usage_per_occupant):
    total_usage = water_usage_per_occupant * num_occupants
    teirs = [val if type(val) == int else float("inf") for val in WATER_TIERS.keys()]
    teirs.sort()
    uncalculated_usage = total_usage
    # print(total_usage)
    cost = total_usage * SEWER_COST_PER_CCF # calcualate sewer usage
    for i in range(len(teirs)):
        if i < len(teirs) - 1:
            ccf_to_pay = min(teirs[i]-teirs[i-1], uncalculated_usage) if i > 0 else min(teirs[i]-0, uncalculated_usage)
            cost += ccf_to_pay * WATER_TIERS[teirs[i]]
            uncalculated_usage -= ccf_to_pay
        else:
            if uncalculated_usage > 0:
                cost += uncalculated_usage*WATER_TIERS['else']
    return cost

def estimate_garbage_cost(num_units, include):
    return GARBAGE_COST_PER_UNIT * num_units if include else False

def estimate_units(zoning_code, lot_size_acres=1):
    """
    Estimates the number of residential units based on the zoning code and lot size.
    
    Args:
        zoning_code (str): The zoning code (e.g., 'RS-10', 'PDR 6.050', 'RU-5').
        lot_size_acres (float): The total size of the land in acres (default is 1 acre).
    
    Returns:
        int: Estimated number of residential units for the given zoning code.
    """
    # Handle PDR zones (e.g., 'PDR 6.050')
    pdr_match = re.match(r'PDR (\d+\.\d+)', zoning_code)
    if pdr_match:
        units_per_acre = float(pdr_match.group(1))
        return max(int(units_per_acre * lot_size_acres), 1)

    # Handle RS zones (e.g., 'RS-10', 'RS-8')
    rs_match = re.match(r'RS-(\d+)', zoning_code)
    if rs_match:
        min_lot_size_sqft = int(rs_match.group(1)) * 1_000  # Convert to square feet
        units = (lot_size_acres * 43_560) // min_lot_size_sqft  # 43,560 sq ft in an acre
        return max(1, int(units))  # Ensure at least one unit is returned

    # Handle RU zones (e.g., 'RU-5', 'RU-5(2)')
    ru_match = re.match(r'RU-5(?:\((\d)\))?', zoning_code)
    if ru_match:
        multiplier = int(ru_match.group(1)) if ru_match.group(1) else 1
        units = (lot_size_acres * 43_560) // (5_000 / multiplier)
        return max(1, int(units))

    # Handle special or mixed-use zones
    if 'MU' in zoning_code or 'CC' in zoning_code:
        return max(int(10 * lot_size_acres), 1)  # Assume 10 units per acre for mixed-use areas

    # Default for unhandled zoning codes
    return 1

def estimate_insurance_cost(property_value):
    return INSURANCE_COST_PCT*property_value

def estimate_heating_cost(isGas, sqft):
    avg_heat_running_hrs = 5
    days_in_month = 30
    return NATURAL_GAS_PER_SQFT_PER_HR*avg_heat_running_hrs*days_in_month*sqft if isGas else ELECTRIC_PER_SQFT_PER_HR*avg_heat_running_hrs*days_in_month*sqft
            
def estimate_legal_cost(annual_rental_income, num_units):
    if num_units > 1:
        return annual_rental_income*.015
    else:
        return 0

def management_reserve_cost(property_value):
    return property_value*MANAGEMENT_RESERVE_PCT

def maintenence_reserve_cost(property_value):
    return property_value*MAINTENENCE_RESERVE_PCT
    
def calculate_property_tax(etj, property_value):
    if etj is None or etj not in ETJ_TAX_RATE:
        raise ValueError("Invalid or unknown ETJ code provided.")

    tax_rate = ETJ_TAX_RATE[etj]

    property_tax = (tax_rate / 100) * property_value

    return round(property_tax, 2)

def calculate_lawn_snow_cost(acres, lawn_care_per_acre):
    return acres*lawn_care_per_acre
    
def estimate_expenses(annual_rental_income, num_units, isGas, sqft, property_value, num_beds, etj, acres):
    sqft = 625 * num_beds
    costs = [
        estimate_legal_cost(annual_rental_income, num_units),
        estimate_heating_cost(isGas, sqft),
        estimate_insurance_cost(property_value),
        estimate_garbage_cost(num_units, include=True),
        estimate_water_cost(num_beds, water_usage_per_occupant=sum(WATER_USAGE_PER_OCCUPANT)/len(WATER_USAGE_PER_OCCUPANT)),
        management_reserve_cost(property_value),
        maintenence_reserve_cost(property_value),
        calculate_property_tax(etj, property_value),
        calculate_lawn_snow_cost(acres, lawn_care_per_acre=sum(LAWN_CARE_PER_ACRE)/len(LAWN_CARE_PER_ACRE))
    ]
    print(costs)
    return sum(costs)
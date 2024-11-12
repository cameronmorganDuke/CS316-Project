from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, session, flash
from flask_login import login_required, current_user
from .models import Note
from . import db
import json
from .utils import *
from sqlalchemy import *

pick_home = Blueprint('pick_home', __name__)

@pick_home.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST': 
        address = request.form.get('address')
        return redirect(url_for('pick_home.home_info', address=address))

    return render_template("get_home.html", user=current_user)

@pick_home.route('/<address>', methods=['GET', 'POST'])
def home_info(address):
    street_number, street_name = extract_address_components(address)
    street_number = street_number.strip()
    street_name = street_name.upper().strip()
    query = f"""
        SELECT ZONING, GROSS_LEASABLE_AREA, TOTAL_PROP_VALUE, Total_Bedrooms, ETJ, CALCULATED_ACRES, NEIGHBORHOOD
        FROM dtarp
        WHERE TRIM(street)='{street_name}' and number='{street_number}'
    """
    
    result = db.session.execute(text(query))
    rows = result.fetchall()
    
    print(f"\n\n{len(rows)}\n\n")
    
    if len(rows) != 1:
        flash(f"There are {len(rows)} entries in the database for this address", 'error')
        return redirect(url_for('pick_home.home'))
            
    zoning, sqft, property_value, num_beds, etj, acres, neighborhood = rows[0]
    property_value = property_value if property_value else 1
    
    assert zoning != None and sqft != None and property_value != None and num_beds != None and etj != None and acres, "Not all values are initialized"
    
    sqft = 625*num_beds if not sqft else sqft
    
    monthly_rent = int(property_value*0.005)
    
    vacancy_allowance_pct = 5/100
    
    annual_rental_income = monthly_rent * 12 * (1 - vacancy_allowance_pct)
    
    num_units = estimate_units(zoning, acres)
    
    isGas = False
    
    utilities = estimate_heating_cost(isGas, sqft) + \
        estimate_garbage_cost(num_units, include=True) + \
        estimate_water_cost(num_beds, water_usage_per_occupant=sum(WATER_USAGE_PER_OCCUPANT)/len(WATER_USAGE_PER_OCCUPANT)) + \
        calculate_lawn_snow_cost(acres, lawn_care_per_acre=sum(LAWN_CARE_PER_ACRE)/len(LAWN_CARE_PER_ACRE))
    
    utilities = round(utilities, 0)
    
    legal = round(estimate_legal_cost(annual_rental_income, num_units), 0)
    
    expenses = estimate_expenses(
        annual_rental_income, num_units, 
        isGas, sqft, property_value, 
        num_beds, etj, acres
    )
    
    # annual operating expenses = electricity + water + sewer + garbage + real estate taxes + property insurance + heating + management reserve calculated + maintenance reserve calculated + legal and professional + lawn and snow
    # annual gross scheduled income = total monthly rental income * 12
    # gross operating income = annual gross scheduled income - vacancy allowance % * annual gross scheduled income

    #create function to get Cap Rate and NOI 
    noi = annual_rental_income - expenses
    cap_rate = noi / property_value * 100
        
    selected_value = request.form.get('selected_value')
    print(f"Slider value received: {selected_value}")
    query = f"""
            SELECT number, street 
            FROM dtarp
            WHERE NEIGHBORHOOD='{neighborhood}' and Total_Bedrooms = '{num_beds}' and number != '{street_number}' and street != '{street_name}'
            """
    
    result = db.session.execute(text(query))
    rows = result.fetchall()
    all_link = []
    for i in range(3):
        try: 
            address_part = f'{int(rows[i][0])} {rows[i][-1]}'
            address_part = " ".join(address_part.split())
            url = url_for('pick_home.home_info', address=address_part)
            all_link.append([address_part, url])
        except:
            address_part = f'{int(street_number)} {street_name}'
            address_part = " ".join(address_part.split())
            url = url_for('pick_home.home_info', address=address_part)
            all_link.append(["None", url])
    
    
    if request.method == 'POST': 
        
        #create function to get Cap Rate and NOI 

        # Create a note string with the gathered data
        note = f"Address: {address} Cap Rate: {cap_rate} Net Operating Income: {noi}"
        print(address)

        # Save note in the database
        new_note = Note(data=note, user_id=current_user.id)
        db.session.add(new_note)
        db.session.commit()
        flash('Note added!', category='success')
        
    return render_template(
        "display_home.html", 
        user=current_user, address=address, cap_rate=cap_rate, noi=noi, 
        monthly_rent=monthly_rent, annual_rental_income=annual_rental_income, 
        expenses=expenses, zoning=zoning, sqft=sqft, property_value=property_value, 
        num_beds=num_beds, acres=acres, etj=etj, all_link=all_link,
        vacancy_allowance_pct=vacancy_allowance_pct * 100, isGas=isGas,
        num_units=num_units, utilities=utilities, legal=legal
    )
    # return render_template(
        # "display_home.html", user=current_user, 
        # address=address, cap_rate=cap_rate, noi=noi, 
        # monthly_rent=monthly_rent, annual_rental_income=annual_rental_income, 
        # expenses=expenses, zoning=zoning, sqft=sqft, property_value=property_value, 
        # num_beds=num_beds, acres=acres, etj=etj, all_link=all_link
    # )

@pick_home.route('/favorites', methods=['GET', 'POST'])
def fav():
    return render_template("favorites.html", user=current_user)

@pick_home.route('/delete-note', methods=['POST'])
def delete_note():  
    note = json.loads(request.data) # this function expects a JSON from the INDEX.js file 
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return redirect(url_for('pick_home.fav'))

@pick_home.route('/process_form1', methods=['POST'])
def get_form():
    form_one = request.form.get('selected_value_one')
    form_two = request.form.get('selected_value_two')
    print(form_one)
    print(form_two)
    flash('Information updated!', category='success')
    return redirect(url_for('pick_home.home_info'))

# Route for rendering the HTML page
@pick_home.route('/all_addresses', methods=['GET'])
@login_required
def all_addresses():
    return render_template('all_addresses.html', user=current_user)

# API route to return the addresses as JSON
@pick_home.route('/api/addresses', methods=['GET'])
@login_required
def get_all_addresses():
    try:
        # Query to fetch all addresses
        # query = """
        #     SELECT street, number, city, state, zip_code, country 
        #     FROM dtarp
        # """
        query = """
            SELECT street, number, NEIGHBORHOOD, CITY, PIN_EXT
            FROM dtarp
        """
        result = db.session.execute(text(query))
        addresses = result.fetchall()

        # Convert the query result to a list of dictionaries


        address_list = []

        for row in addresses:
            try:
                # Attempt to create the address part
                address_part = f'{int(row[1])} {row[0]}'
                address_part = " ".join(address_part.split())  # Clean up any extra spaces

                # Generate the URL using url_for
                url = url_for('pick_home.home_info', address=address_part)

                # Create the link
                link = f'<a href="{url}">View Property</a>'
            except (TypeError, ValueError, AssertionError):
                # If it fails (e.g., row[1] is None), set link to None
                link = None

            # Add the address to the list
            address = {
                'street': row[0],
                'city': row[3],
                'state': 'NC',
                'zip_code': row[2],
                'country': 'USA',
                'number': row[1],
                'link': link
            }

            address_list.append(address)


        # Return the list as a JSON response
        return jsonify(address_list)

    except Exception as e:
        # Print the full exception for debugging
        print(f"Error: {str(e)}")
        return jsonify({'error': 'Failed to fetch addresses', 'details': str(e)}), 500
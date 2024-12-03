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
    
    if len(rows) != 1:
        flash(f"There are {len(rows)} entries in the database for this address", 'error')
        return redirect(url_for('pick_home.home'))
            
    zoning, sqft, property_value, num_beds, etj, acres, neighborhood = rows[0]
    property_value = property_value if property_value else 1
    
    assert zoning != None and sqft != None and property_value != None and num_beds != None and etj != None and acres, "Not all values are initialized"
    
    num_units = estimate_units(zoning, acres)
    
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
        note = f"Address: {address}"
        # note = f"Address: {address} Cap Rate: {cap_rate} Net Operating Income: {noi}"
        print(address)

        # Save note in the database
        new_note = Note(data=note, user_id=current_user.id)
        db.session.add(new_note)
        db.session.commit()
        flash('Note added!', category='success')
        
    return render_template(
        "display_home.html", 
        user=current_user, address=address, zoning=zoning, sqft=sqft, property_value=property_value, 
        num_beds=num_beds, acres=acres, etj=etj, all_link=all_link,
        num_units=num_units
    )

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
        query = """
            SELECT street, number, NEIGHBORHOOD, CITY, PIN_EXT
            FROM dtarp
        """
        result = db.session.execute(text(query))
        addresses = result.fetchall()

        address_list = []

        for row in addresses:
            street = row[0]
            number = row[1]
            neighborhood = row[2] or ''
            city = row[3] or ''

            if number and street:
                address_part = f"{int(number)} {street}".strip()
                # Generate the URL
                url = url_for('pick_home.home_info', address=address_part)
                # Create the link
                link = f'<a href="{url}">View Property</a>'
            else:
                link = ''

            # Build the address dictionary
            address_dict = {
                'number': number or '',
                'street': street or '',
                'city': city,
                'state': 'NC',
                'neighborhood': neighborhood,
                'country': 'USA',
                'link': link
            }
            address_list.append(address_dict)

        # Return the list as a JSON response
        return jsonify(address_list)

    except Exception as e:
        # Print the full exception for debugging
        print(f"Error: {str(e)}")
        return jsonify({'error': 'Failed to fetch addresses', 'details': str(e)}), 500
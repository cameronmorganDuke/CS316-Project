from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, session
from flask_login import login_required, current_user
from .models import Note
from . import db
import json
from .utils import *

pick_home = Blueprint('pick_home', __name__)
address = ""
city = ""
state = ""
zip_code = ""
country = ""
change_input_one = ""
change_input_two = ""

@pick_home.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST': 
        global address, city, state, zip_code, country
        session['address'] = request.form.get('address')
        session['city'] = request.form.get('city')
        session['state'] = request.form.get('state')
        session['zip_code'] = request.form.get('zip')  # 'zip' matches the name attribute
        session['country'] = request.form.get('country')
        print(address, city, state, zip_code, country)
        
        
        
        # After processing the POST request, render display_home.html
        return redirect(url_for('pick_home.home_info'))

    # If it's a GET request, render the initial form
    return render_template("get_home.html", user=current_user)

@pick_home.route('/display_home', methods=['GET', 'POST'])
def home_info():
    global address, city, state, zip_code, country
    
    street_number, street_name = extract_address_components(session['address'])
    street_number = street_number.strip()
    street_name = street_name.upper().strip()
    city_name = session['city'].upper().strip()
    
    query = f"""
        SELECT ZONING, GROSS_LEASABLE_AREA, TOTAL_PROP_VALUE, Total_Bedrooms, ETJ, CALCULATED_ACRES
        FROM dtarp
        WHERE TRIM(street)='{street_name}' and number='{street_number}'
    """
        # WHERE TRIM(street)='{street_name}' and TRIM(number)='{street_number}'
    
    result = db.session.execute(text(query))
    rows = result.fetchall()
    
    print(f"\n\n{len(rows)}\n\n")
    
    assert len(rows) != 0, "There are no entries in the database for this address"
    assert len(rows) == 1, f"There are {len(rows)} entries in the database for this address"
    
    zoning, sqft, property_value, num_beds, etj, acres = rows[0]
    
    assert zoning != None and sqft != None and property_value != None and num_beds != None and etj != None and acres, "Not all values are initialized"
    
    monthly_rent = property_value*0.015
    annual_rental_income = monthly_rent*12
    
    vacancy_allowance_pct = 5/100
    
    annual_rental_income = annual_rental_income - annual_rental_income*vacancy_allowance_pct
    
    num_units = estimate_units(zoning, acres)
    
    isGas = False
    
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
    
    print('zoning', 'sqft', 'property_value', 'num_beds', 'etj', 'acres')
    print(zoning, sqft, property_value, num_beds, etj, acres)
    print()
    print("monthly rent", monthly_rent)
    print("rental income", annual_rental_income)
    print("expenses", expenses)
    print("noi", noi)
    print("cap rate", cap_rate)
    
    selected_value = request.form.get('selected_value')
    print(f"Slider value received: {selected_value}")
    #cap_rate = function to get cap rate
    #noi = function to get noi
    #new_info = 
    if request.method == 'POST': 
        #create function to get Cap Rate and NOI 

        # Create a note string with the gathered data
        note = f"Address: {address} Cap Rate: {cap_rate} Net Operating Income: {noi}"

        # Save note in the database
        new_note = Note(data=note, user_id=current_user.id)
        db.session.add(new_note)
        db.session.commit()
        flash('Note added!', category='success')
    return render_template("display_home.html", user=current_user, address=address, cap_rate=cap_rate, noi=noi)

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


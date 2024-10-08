from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Note
from . import db
import json

pick_home = Blueprint('pick_home', __name__)

@pick_home.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST': 
        address = request.form.get('address')
        city = request.form.get('city')
        state = request.form.get('state')
        zip_code = request.form.get('zip')  # 'zip' matches the name attribute
        country = request.form.get('country')
        print(address, city, state, zip_code, country)
        
        #cap_rate = function to get cap rate
        # noi = function to get noi
        
        # After processing the POST request, render display_home.html
        return render_template("display_home.html", user=current_user, address=address, cap_rate="test_cr", noi="test_noi")

    # If it's a GET request, render the initial form
    return render_template("get_home.html", user=current_user)

@pick_home.route('/display_home', methods=['GET', 'POST'])
def home_info():
    print("working")
    if request.method == 'POST': 
        address = request.form.get('address')  # Correct spelling
        cap_rate = request.form.get('cap_rate')
        noi = request.form.get('noi')

        # Create a note string with the gathered data
        note = f"Address: {address} Cap Rate: {cap_rate} Net Operating Income: {noi}"
        print(note)

        # Save note in the database
        new_note = Note(data=note, user_id=current_user.id)
        db.session.add(new_note)
        db.session.commit()
        flash('Note added!', category='success')
    return render_template("home.html", user=current_user)


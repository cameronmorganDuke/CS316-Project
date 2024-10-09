from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from .models import Note
from . import db
import json

pick_home = Blueprint('pick_home', __name__)
address = ""
city = ""
state = ""
zip_code = ""
country = ""

@pick_home.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST': 
        global address, city, state, zip_code, country
        address = request.form.get('address')
        city = request.form.get('city')
        state = request.form.get('state')
        zip_code = request.form.get('zip')  # 'zip' matches the name attribute
        country = request.form.get('country')
        print(address, city, state, zip_code, country)
        
        
        
        # After processing the POST request, render display_home.html
        return redirect(url_for('pick_home.home_info'))

    # If it's a GET request, render the initial form
    return render_template("get_home.html", user=current_user)

@pick_home.route('/display_home', methods=['GET', 'POST'])
def home_info():
    global address, city, state, zip_code, country
    #create function to get Cap Rate and NOI 
    cap_rate = "test cap rate"
    noi = "test noi"
    
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


from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User
from .models import Note
from . import db
import json

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        note = request.form.get('note')

        if len(note) < 1:
            flash('Note is too short!', category='error')
        else:
            new_note = Note(data=note, user_id=current_user.id)
            db.session.add(new_note)
            db.session.commit()
            flash('Note added!', category='success')

    return render_template("home.html", user=current_user)


@views.route('/delete-note', methods=['POST'])
def delete_note():
    note = json.loads(request.data)
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})

@views.route('/account', methods = ["GET","POST"])    
def profile():
    if request.method == "POST":
        name = request.form.get('name')
        email = request.form.get('email')
        address = request.form.get('address')
        

        user = User.query.filter_by(email=current_user.email).first()

        if len(name) > 0:
            user.first_name = name
            flash('Name successfully changed', category='success')

        elif len(email) > 3:
            user2 = User.query.filter_by(email=email).first()
            if user2:
                flash("Email already taken", category="error")
            else:
                user.email = email
                flash('Email successfully changed', category='success')

        elif len(address) != 0:
            user.address = address
            flash('Address Updated', category='success')

        else :
            flash("Invalid entry, please re-enter",category='error')

        
        db.session.commit()
        return redirect('/account')

    return render_template('profile.html', user=current_user)
    

    

from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User, Staff, Manager, Movie
from .models import Note
from . import db
import json

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    # if request.method == 'POST':
    #     note = request.form.get('note')

    #     if len(note) < 1:
    #         flash('Note is too short!', category='error')
    #     else:
    #         new_note = Note(data=note, user_id=current_user.id)
    #         db.session.add(new_note)
    #         db.session.commit()
    #         flash('Note added!', category='success')
    movie = Movie.query.all()
    movie_data = []
    if len(movie) == 0:
        with open('./movie.json') as json_file:
            movie_data = json.load(json_file)
        for mov in movie_data:
            movie1 = Movie(name = mov['title'], json_data = mov, url = mov['img_url'], rent_cost = 100,buy_cost = 200)
            db.session.add(movie1)
            db.session.commit()
        
    movie = Movie.query.all()
    rs = []
    for ele in movie:
        if ele.json_data['votes'] > 30000:
            rs.append(ele)
        if(len(rs) == 20):
            break

    return render_template("home.html", user=current_user, movies = rs)


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
        
        if len(name) > 0:
            current_user.first_name = name
            flash('Name successfully changed', category='success')

        elif len(email) > 3:
            if current_user.cred == 1:
                user2 = User.query.filter_by(email=email).first()
            elif current_user.cred == 2:
                user2 = Staff.query.filter_by(email=email).first()
            elif current_user.cred == 3:
                user2 = Manager.query.filter_by(email=email).first()
            else:
                pass
            if user2:
                flash("Email already taken", category="error")
            else:
                current_user.email = email
                flash('Email successfully changed', category='success')

        elif len(address) != 0:
            current_user.address = address
            flash('Address Updated', category='success')

        else :
            flash("Invalid entry, please re-enter",category='error')

        db.session.commit()
        return redirect('/account')

    return render_template('profile.html', user=current_user)

    
@views.route('/staff', methods=['GET', 'POST'])
@login_required
def home_staff():
    return render_template("home_staff.html", user=current_user)

@views.route('/staff/account',methods= ["GET","POST"])
def profile_staff():
    return render_template("profile_staff.html",user=current_user)

@views.route('/manager', methods=['GET', 'POST'])
@login_required
def home_manager():
    return render_template("home_manager.html", user=current_user)

@views.route('/manager/account', methods=['GET', 'POST'])
def profile_manager():
    return render_template("profile_manager.html", user=current_user)


@views.route('/movie')
def movie():
    return render_template("movie.html")

@views.route('/search', methods = ["GET","POST"])    
def search():
    if request.method == 'POST':
        form = request.form
        search_value = form['searched']
        print(search_value)
        search = "%{0}%".format(search_value)
        results = Movie.query.filter(Movie.name.like(search)).all()

        while len(results)%4 != 0:
            results.pop()
        return render_template('search.html', movies=results, query = search_value)

    else:
        return redirect('/')
    
    
@views.route('/contact', methods = ["GET","POST"])
def contact():
    return render_template('contact.html')

@views.route('/feedback', methods = ["GET","POST"])
def feedback():
    if request.method == 'POST':
        form = request.form
        feedback = form['message']
        if len(feedback) < 1:
            flash('Message is too short!', category='error')
        else:
            flash('Thank you for your feedback!', category='success')
        
    return render_template('feedback.html', user = current_user)
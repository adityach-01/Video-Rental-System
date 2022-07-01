from nis import cat
from unicodedata import category
from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User, Staff, Manager, Movie
from .models import Note
from . import db
import json
import requests, shutil
import random

views = Blueprint('views', __name__)

def save_img(url,filename):
    r = requests.get(url,stream = True)
    if r.status_code == 200:
        with open(filename,'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    movie = Movie.query.all()
    movie_data = []
    if len(movie) == 0:
        with open('./movie.json') as json_file:
            movie_data = json.load(json_file)
        for mov in movie_data:
            movie1 = Movie(name = mov['title'],imdb_id = mov['id'], json_data = mov, url = mov['img_url'], rent_cost = 100,buy_cost = random.randint(100, 200))
            db.session.add(movie1)
            db.session.commit()
        
    movie = Movie.query.all()
    rs = []
    for ele in movie:
        if ele.json_data['votes'] > 70000:
            rs.append(ele)
        if(len(rs) == 20):
            break

    return render_template("home.html", user=current_user, movies = rs)


@views.route('/delete-note/<id>', methods=["GET",'POST'])
def delete_note(id):
    note = Note.query.filter_by(id=id).first()
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return redirect('/user_feedback')

@views.route('/account', methods = ["GET","POST","P"])    
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

    # if request.method == "P":


    return render_template('profile.html', user=current_user)

    
@views.route('/staff', methods=['GET', 'POST'])
@login_required
def home_staff():
    return render_template("home_staff.html", user=current_user)

@views.route('/staff/account',methods= ["GET","POST"])
def profile_staff():
    return render_template("profile_staff.html",user=current_user)


@views.route('/manager/account', methods=['GET', 'POST'])
def profile_manager():
    return render_template("profile_manager.html", user=current_user)

@views.route('/search', methods = ["GET","POST"])    
def search():
    if request.method == 'POST':
        form = request.form
        search_value = form['searched']
        print(search_value)
        search = "%{0}%".format(search_value)
        results = Movie.query.filter(Movie.name.like(search)).all()

        # while len(results)%4 != 0:
        #     results.pop()
        if len(results) == 0:
            results = 0
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
        user = User.query.filter_by(email = current_user.email).first()

        if len(feedback) < 1:
            flash('Message is too short!', category='error')
        else:
            new_note = Note(data = feedback)
            new_note.user_id = user.id
            db.session.add(new_note)
            db.session.commit()
            # This feeback has been added to the feedback database to be displayed at the manager end

            flash('Thank you for your feedback!', category='success')
        
    return render_template('feedback.html', user = current_user)


@views.route('/movie/<id>', methods = ["GET","POST"])
def movie(id):
    movie = Movie.query.filter_by(id=id).first()
    user = User.query.filter_by(email=current_user.email).first()

    if request.method == 'POST':
        type = request.form.get('type')

        # if movie.availability == 0:
        #     flash("Movie is not available in our shop", category="error")
        # code to be implemented later
        
        if movie in user.movie_cart:
            flash("Movie is already there in your cart", category="error")
        else:
            user.movie_cart.append(movie)
            db.session.commit()

    return render_template("movie.html", movie=movie)

@views.route('/delete-film/<id>', methods = ["GET","POST"])
def movie_remove(id):
    movie = Movie.query.filter_by(id=id).first()
    user = User.query.filter_by(email=current_user.email).first()

    if movie in user.movie_cart:
        user.movie_cart.remove(movie)
        db.session.commit()
        return redirect('/account')

    return render_template("profile.html", movie=movie, user=current_user)

@views.route('/account/purchase/<user_id>', methods = ["GET","POST"])
def process_order(user_id):
    user = User.query.filter_by(id=user_id).first()

    buy_list = []
    price = 0

    if len(user.movie_cart) == 0:
        flash("Please select movies in our cart first", category='error')
        return redirect('/account')

    else:
        for movie in user.movie_cart:
            # if movie.availability == 0:
            #     flash("Movie {{movie.name}} is not there in our shop", category="error")
            price += movie.buy_cost
            user.movie_buy.append(movie)
            buy_list.append(movie)
            
        db.session.commit()

        user.movie_cart.clear()
        db.session.commit()

    return render_template("transaction.html",buy_list = buy_list, user=current_user, price=price)

@views.route('/account/delete_history/<user_id>', methods = ["GET","POST"])
def delete_history(user_id):
    user = User.query.filter_by(id=user_id).first()
    
    if len(user.movie_buy) == 0:
        flash("Buy History is already empty", category="error")
        return redirect('/account')
    else:
        user.movie_buy.clear()
        db.session.commit()
        return redirect('/account')

@views.route('/user_feedback', methods = ["GET", "POST"])
def user_feed():
    note = Note.query.all()
    user_list = []
    if len(note)==0:
        note = 0
    else:
        pass
    return render_template('user_feedback.html', notes = note)

# This section of the code deals with adding movie to the database


@views.route('/manager', methods=['GET', 'POST'])
@login_required
def home_manager():
    if request.method == "POST":
        link = request.form.get('api')
        # print(url)

        url1 = "https://data-imdb1.p.rapidapi.com/titles/"

        querystring = {"info":"base_info"}

        headers = {
            "X-RapidAPI-Host": "data-imdb1.p.rapidapi.com",
            "X-RapidAPI-Key": "1bce1e6548msh04953ac9cbfa59ap17fff6jsn63321cf8fe55"
        }

        # link = input("Enter imdb url:")
        link = link[link.find('/tt')+1:link.find('/tt')+10]
        url = url1 + link

        try:
            response = requests.request("GET", url, headers=headers, params=querystring)
        except:
            flash("Could not be added to the database", category='error')
            return redirect('/manager')
        response = response.json()['results']
        # print(response.json()['results'])

        filename = 'movie.json'
        file_data = []

        with open(filename,mode = 'r+') as file:
            file_data = json.load(file)

            data = {}

            data['id'] = response['id']
            if not isinstance(response['titleText'],type(None)):
                data['title'] = response['titleText']['text']
            else:
                data['title'] = None

            if not isinstance(response['releaseDate'],type(None)):
                data['release_date'] = str(response['releaseDate']['day']) + "-" + str(response['releaseDate']['month']) + "-" + str(response['releaseDate']['year'])
            else:
                data['release_date'] = None

            if not isinstance(response['ratingsSummary'],type(None)):

                if not isinstance(response['ratingsSummary']['aggregateRating'],type(None)):
                    data['rating'] = response['ratingsSummary']['aggregateRating']
                else:
                    data['rating'] = 0

                if not isinstance(response['ratingsSummary']['voteCount'],type(None)):
                    data['votes'] = response['ratingsSummary']['voteCount']
                else:
                    data['votes'] = 0
            

            if not isinstance(response['runtime'],type(None)):
                data['runtime'] = response['runtime']['seconds']
            else:
                data['runtime'] = None
            
            if not isinstance(response['runtime'],type(None)):
                data['runtime_sec'] = response['runtime']['seconds']
                hr = data['runtime_sec'] // 3600
                min = (data['runtime_sec'] % 3600) // 60
                data['runtime'] = str(hr) + " hr " + str(min) + " min"
            else:
                data['runtime_sec'] = None
                data['runtime'] = None

            if not isinstance(response['primaryImage'],type(None)):

                data['img_url'] = response['primaryImage']['url']
                data['dim'] = (response['primaryImage']['width'],response['primaryImage']['height'])
                data['img_caption'] = response['primaryImage']['caption']['plainText']
            
            else:
                data['img_url'] = None
                data['dim'] = None
                data['img_caption'] = None

            if not isinstance(response['plot'],type(None)) and not isinstance(response['plot']['plotText'],type(None)):
                    data['summary'] = response['plot']['plotText']['plainText']
            else:
                data['summary'] = None

            data['genres'] = []

            if not isinstance(response['genres'],type(None)):
                for gen in response['genres']['genres']:
                    data['genres'].append(gen['text'])

            if data['rating'] < 7:
                print(f"Rating of {data['id']} is too low : {data['rating']}")
                exit()
            
            if not isinstance(data['img_url'],type(None)) and not isinstance(data['id'],type(None)):
                filename = "website/static/images/" + str(data['id']) + ".jpg"
                save_img(data['img_url'],filename)
                print(f"Saved image for {data['id']} Successfully.")
            else:
                print(f"No image for {data['id']}")

            # mov = Movie.query.filter(imdb_id = data['id']).first()
            # if mov:
            #     flash("Movie already exists in the database", category='error')
            if 10>2:
                movie1 = Movie(name = data['title'],imdb_id = data['id'], json_data = data, url = data['img_url'], rent_cost = 100,buy_cost = random.randint(100, 200))
                db.session.add(movie1)
                db.session.commit()
                flash("Movie added to the database", category='success')

    return render_template("home_manager.html", user=current_user)
    
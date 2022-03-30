from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import Movie
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
import json
from flask_login import login_user, login_required, logout_user, current_user

movie_data = {}

with open('./website/movie.json') as file:
    movie_data = json.load(file)

for movie in movie_data:
    print(movie['title'])


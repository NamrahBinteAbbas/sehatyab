from flask import Blueprint, render_template

auth = Blueprint('auth',__name__)

@auth.route('/login')
def login():
    return render_template("login.html")
# @auth.route('/logout')
# def logout():
#     return "<p>logout please</p>"
# @auth.route('/sign up')
# def signup():
#     return "<p>sign up please </p>"
from flask import Blueprint, render_template, request, session, redirect, url_for
import psycopg2
import uuid

auth = Blueprint('auth', __name__)

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    return render_template('signup.html')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')
from flask import Blueprint, render_template

views = Blueprint('views',__name__)

@views.route('/')
def home():
    return render_template("base.html")
def login():
    return render_template("login.html")
def signup():
    return render_template("signup.html")
def admin():
    return render_template("admin.html")
def patient():
    return render_template("patient.html")
def doctor():
    return render_template("doctor.html")
# app/__init__.py

from flask import Flask, g
import psycopg2
from dotenv import load_dotenv
import os

# Load .env variables
load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

def get_db_connection():
    return psycopg2.connect(
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME
    )

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'namrahsapp'

    # Store connection in app context
    conn = get_db_connection()
    app.db_connection = conn

    # Helper to get cursor for each request
    @app.before_request
    def create_cursor():
        if app.db_connection:
            g.cursor = app.db_connection.cursor()

    @app.teardown_request
    def close_cursor(exception):
        cursor = g.pop("cursor", None)
        if cursor:
            cursor.close()

    # Register routes
    from .views import views
    app.register_blueprint(views, url_prefix='/')

    from .auth import auth
    app.register_blueprint(auth, url_prefix='/')
    
    from .admin import admin
    app.register_blueprint(admin, url_prefix='/')
    
    from .patient import patient
    app.register_blueprint(patient, url_prefix='/patient')

    from .doctor_api import doctor
    app.register_blueprint(doctor, url_prefix='/doctor')

    return app

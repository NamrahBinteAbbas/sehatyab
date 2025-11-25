from flask import Blueprint, render_template, request, session, redirect, url_for
import psycopg2
import uuid
from website import get_db_connection

auth = Blueprint('auth', __name__)

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        age = request.form.get('age')
        gender = request.form.get('gender')
        address = request.form.get('address')
        contactno = request.form.get('contactno')
        bloodgroup = request.form.get('bloodgroup')
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirmPassword')

        # Validation
        if not all([name, age, gender, address, contactno, bloodgroup, email, username, password]):
            print('All fields are required!', 'error')
            return render_template('signup.html')

        if password != confirm_password:
            print('Passwords do not match!', 'error')
            return render_template('signup.html')

        conn = get_db_connection()
        cur = conn.cursor()

        try:
            # Check if username already exists
            cur.execute("SELECT * FROM patient WHERE username = %s", (username,))
            if cur.fetchone():
                print('Username already exists!', 'error')
                return render_template('signup.html')

            # Check if email already exists
            cur.execute("SELECT * FROM patient WHERE email = %s", (email,))
            if cur.fetchone():
                print('Email already registered!', 'error')
                return render_template('signup.html')

            # Insert into patient table
            cur.execute("""
                INSERT INTO patient
                (name, age, gender, address, contactno, bloodgroup, createdat, email, username, password)
                VALUES (%s, %s, %s, %s, %s, %s, NOW(), %s, %s, %s)
            """, (name, age, gender, address, contactno, bloodgroup, email, username, password))

            conn.commit()
            print('Account created successfully! Please login.', 'success')
            return redirect(url_for('auth.login'))

        except Exception as e:
            print('Error:', e)
            conn.rollback()
            return render_template('signup.html')

        finally:
            cur.close()
            conn.close()

    return render_template('signup.html')
            
    
    # GET request - show the signup form
    return render_template('signup.html')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email_or_username = request.form.get('email')  # your form field is "email"
        password = request.form.get('password')

        if not email_or_username or not password:
            print("All fields are required!", "error")
            return render_template('login.html')

        conn = get_db_connection()
        cur = conn.cursor()
        try:
            # Check patient table for username or email
            cur.execute("""
                SELECT * FROM patient
                WHERE email = %s OR username = %s
            """, (email_or_username, email_or_username))
            user = cur.fetchone()

            if user and user[-1] == password:  # assuming password is last column
                # Login successful → redirect to patient panel
                print("Login successful!", "success")
                return redirect(url_for('patient.patient_page'))  # replace with patient blueprint dashboard route
            else:
                print("Invalid username/email or password", "error")
                return render_template('login.html')
        finally:
            cur.close()
            conn.close()

    return render_template('login.html')
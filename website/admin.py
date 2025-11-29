# THIS PAGE HANDLES ADMIN ROUTE AND LOGIC

from flask import Blueprint, render_template, request
from website.__init__ import get_db_connection

admin = Blueprint('admin', __name__)

@admin.route('/admin', methods=('GET', 'POST'))
def admin_page():
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT * FROM employee
    """)
    
    doctors = cur.fetchall()
    print(doctors)
    
    return render_template("admin.html", doctors=doctors)

@admin.route('/admin/add_doctor', methods=['POST'])
def add_doctor():
    try:
        # Get JSON data from request
        data = request.get_json()
        
        # Extract form fields
        empid = data.get('empid')
        name = data.get('name')
        gender = data.get('gender')
        role = data.get('role')
        contact = data.get('contact')
        salary = data.get('salary')
        deptid = data.get('deptid')
        
        # Validate required fields
        if not all([empid, name, gender, role, contact, salary, deptid]):
            return "All fields are required", 400
        
        # Connect to database
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Simple insert - let database handle defaults
        cur.execute("""
            INSERT INTO employee (empid, name, gender, role, contact, salary, deptid) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (empid, name, gender, role, contact, salary, deptid))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return "Doctor added successfully!", 200
        
    except Exception as e:
        print(f"Error adding doctor: {e}")
        if conn:
            conn.rollback()
        return f"Error: {str(e)}", 500
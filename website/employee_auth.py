from flask import Blueprint, render_template, request, session, redirect, url_for
import psycopg2
import psycopg2.extras
from website import get_db_connection

employee_auth = Blueprint('employee_auth', __name__)

@employee_auth.route('/employee_login', methods=['GET', 'POST'])
def employee_login():
    if request.method == 'POST':
        employee_id = request.form.get('employeeId')
        password = request.form.get('password')

        if not employee_id or not password:
            print("All fields are required!")
            return render_template('employee-login.html')

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            # Convert employee_id to integer if needed
            try:
                emp_id = int(employee_id)
            except ValueError:
                print("Invalid employee ID format")
                return render_template('employee-login.html')

            # Check employee table for empid and password
            cur.execute("""
                SELECT empid, role, password FROM employee
                WHERE empid = %s
            """, (emp_id,))
            employee = cur.fetchone()

            if employee and employee['password'] == password:
                # Store employee info in session
                session['employee_id'] = employee['empid']
                session['employee_role'] = employee['role']
                
                print(f"Login successful for employee {employee['empid']}!")
                
                # Redirect based on role from database
                if employee['role'].lower() == 'doctor':
                    return redirect(url_for('doctor.doctor_page'))
                else:  # admin or any other role
                    return redirect(url_for('admin.admin_page'))
            else:
                print(f"Invalid employee ID or password")
                return render_template('employee-login.html')
                
        except Exception as e:
            print(f'Error: {e}')
            return render_template('employee-login.html')
        finally:
            cur.close()
            conn.close()

    return render_template('employee-login.html')

@employee_auth.route('/employee-logout')
def employee_logout():
    session.pop('employee_id', None)
    session.pop('employee_role', None)
    print("Logged out successfully!")
    return redirect(url_for('employee_auth.employee_login'))
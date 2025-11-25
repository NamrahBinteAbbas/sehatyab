# THIS PAGE HANDLES ADMIN ROUTE AND LOGIC

from flask import Blueprint, render_template
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

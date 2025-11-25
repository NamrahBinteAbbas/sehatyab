# THIS PAGE HANDLES ADMIN ROUTE AND LOGIC

from flask import Blueprint, render_template
from website.__init__ import get_db_connection

patient = Blueprint('patient', __name__)

@patient.route('/patient_dashboard', methods=('GET', 'POST'))
def patient_page():
    conn = get_db_connection()
    cur = conn.cursor()
    
    return render_template("patient.html")
